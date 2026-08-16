#!/usr/bin/env python3
"""Export Markdown or LaTeX math to DOCX and verify native OMML output."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.request import url2pathname

from verify_omml import inspect_docx

INPUT_FORMATS = {
    ".md": (
        "markdown+tex_math_dollars+tex_math_single_backslash"
        "+tex_math_double_backslash"
    ),
    ".markdown": (
        "markdown+tex_math_dollars+tex_math_single_backslash"
        "+tex_math_double_backslash"
    ),
    ".mdown": (
        "markdown+tex_math_dollars+tex_math_single_backslash"
        "+tex_math_double_backslash"
    ),
    ".mkd": (
        "markdown+tex_math_dollars+tex_math_single_backslash"
        "+tex_math_double_backslash"
    ),
    ".tex": "latex",
    ".latex": "latex",
}
EXTERNAL_IMAGE_SCHEMES = {"data", "ftp", "http", "https"}
IMAGE_WARNING_RE = re.compile(
    r"could not (?:fetch|find|load) (?:image|resource)|"
    r"(?:image|resource).*(?:not found|failed to (?:fetch|load))",
    re.IGNORECASE,
)


class ExportError(RuntimeError):
    """Raised when conversion or validation cannot complete safely."""


@dataclass(frozen=True)
class PandocRuntime:
    """Resolved Pandoc executable and provenance."""

    executable: str
    source: str
    version: str


@dataclass(frozen=True)
class ImageManifest:
    """Resolved image references discovered through Pandoc's source AST."""

    total: int
    unique: int
    local: int
    external: int
    targets: tuple[str, ...]
    resolved_local_files: tuple[str, ...]


def _run(executable: str, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    """Run Pandoc without invoking a user-controlled shell."""
    return subprocess.run(
        [executable, *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _validate_pandoc(candidate: Path, source: str) -> PandocRuntime | None:
    """Return runtime metadata when a Pandoc candidate is executable."""
    if not candidate.is_file():
        return None
    try:
        result = _run(str(candidate), ["--version"])
    except OSError:
        return None
    if result.returncode != 0:
        return None
    first_line = next(
        (line.strip() for line in result.stdout.splitlines() if line.strip()), ""
    )
    return PandocRuntime(
        executable=str(candidate.resolve()),
        source=source,
        version=first_line or "pandoc (version unknown)",
    )


def resolve_pandoc(explicit: Path | None = None) -> PandocRuntime:
    """Resolve Pandoc from an exact path, PATH, or pypandoc package."""
    candidates: list[tuple[Path, str]] = []
    if explicit is not None:
        candidates.append((explicit.expanduser(), "--pandoc"))

    environment_path = os.environ.get("PANDOC_PATH")
    if environment_path:
        candidates.append((Path(environment_path).expanduser(), "PANDOC_PATH"))

    system_path = shutil.which("pandoc")
    if system_path:
        candidates.append((Path(system_path), "PATH"))

    try:
        import pypandoc  # type: ignore[import-not-found]

        candidates.append((Path(pypandoc.get_pandoc_path()), "pypandoc"))
    except (ImportError, OSError):
        pass

    seen: set[str] = set()
    for candidate, source in candidates:
        key = os.path.normcase(str(candidate.resolve(strict=False)))
        if key in seen:
            continue
        seen.add(key)
        runtime = _validate_pandoc(candidate.resolve(strict=False), source)
        if runtime:
            return runtime

    if explicit is not None:
        raise ExportError(
            f"指定的 Pandoc 不可用: {explicit.expanduser().resolve(strict=False)}"
        )
    raise ExportError(
        "未找到可用 Pandoc。请安装系统 Pandoc，或在当前 Python 环境安装 "
        "pypandoc-binary；安装依赖前应先获得用户许可。"
    )


def _resolve_input_format(source: Path, requested: str | None) -> str:
    """Resolve a Pandoc reader from an explicit value or file extension."""
    if requested:
        return requested
    try:
        return INPUT_FORMATS[source.suffix.lower()]
    except KeyError as exc:
        supported = ", ".join(sorted(INPUT_FORMATS))
        raise ExportError(
            f"无法从扩展名判断输入格式: {source.suffix or '(none)'}；支持 {supported}，"
            "或使用 --from-format 明确指定 Pandoc reader。"
        ) from exc


def _validate_reference_doc(reference: Path) -> Path:
    """Validate that a Pandoc reference document is a DOCX package."""
    resolved = reference.expanduser().resolve()
    if not resolved.is_file():
        raise ExportError(f"Word 参考模板不存在: {resolved}")
    if resolved.suffix.lower() != ".docx" or not zipfile.is_zipfile(resolved):
        raise ExportError(f"Word 参考模板不是有效 DOCX: {resolved}")
    return resolved


def _resource_directories(source: Path, requested: list[Path]) -> list[Path]:
    """Resolve and deduplicate Pandoc resource search directories."""
    directories = [source.parent]
    directories.extend(path.expanduser().resolve() for path in requested)
    unique: list[Path] = []
    seen: set[str] = set()
    for directory in directories:
        resolved = directory.resolve()
        if not resolved.is_dir():
            raise ExportError(f"资源目录不存在: {resolved}")
        key = os.path.normcase(str(resolved))
        if key not in seen:
            seen.add(key)
            unique.append(resolved)
    return unique


def _resource_path_value(directories: list[Path]) -> str:
    """Build Pandoc's platform-specific resource search path value."""
    return os.pathsep.join(str(directory) for directory in directories)


def _pandoc_image_targets(document: object) -> list[str]:
    """Return image targets from a Pandoc JSON AST."""
    targets: list[str] = []

    def visit(node: object) -> None:
        if isinstance(node, dict):
            if node.get("t") == "Image":
                content = node.get("c")
                if (
                    isinstance(content, list)
                    and content
                    and isinstance(content[-1], list)
                    and content[-1]
                    and isinstance(content[-1][0], str)
                ):
                    targets.append(content[-1][0])
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(document)
    return targets


def _local_image_path(target: str) -> Path | None:
    """Convert a local Pandoc image target to a filesystem path."""
    if target.startswith("//"):
        return None
    if re.match(r"^[A-Za-z]:[\\/]", target):
        return Path(unquote(target))

    parsed = urlsplit(target)
    if parsed.scheme.casefold() in EXTERNAL_IMAGE_SCHEMES:
        return None
    if parsed.scheme.casefold() == "file":
        return Path(url2pathname(unquote(parsed.path)))
    if parsed.scheme:
        return None
    return Path(unquote(parsed.path))


def _resolve_local_image(target: str, directories: list[Path]) -> Path | None:
    """Resolve a local image target using Pandoc's resource search order."""
    candidate = _local_image_path(target)
    if candidate is None:
        return None
    if candidate.is_absolute():
        return candidate.resolve() if candidate.is_file() else None
    for directory in directories:
        resolved = (directory / candidate).resolve()
        if resolved.is_file():
            return resolved
    return None


def _inspect_source_images(
    runtime: PandocRuntime,
    source: Path,
    input_format: str,
    resource_directories: list[Path],
) -> ImageManifest:
    """Parse source images through Pandoc and fail when local files are missing."""
    resource_path = _resource_path_value(resource_directories)
    result = _run(
        runtime.executable,
        [
            f"--from={input_format}",
            "--to=json",
            "--standalone",
            f"--resource-path={resource_path}",
            str(source),
        ],
    )
    if result.returncode != 0:
        diagnostic = (result.stderr or result.stdout or "Pandoc 未返回诊断").strip()
        raise ExportError(f"Pandoc 无法解析源文件（exit {result.returncode}）:\n{diagnostic}")
    try:
        document = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ExportError(f"Pandoc 没有返回有效的文档结构: {exc}") from exc

    targets = _pandoc_image_targets(document)
    missing: list[str] = []
    resolved_files: list[Path] = []
    unique_keys: list[str] = []
    external = 0
    for target in targets:
        candidate = _local_image_path(target)
        if candidate is None:
            external += 1
            unique_keys.append(f"external:{target}")
            continue
        resolved = _resolve_local_image(target, resource_directories)
        if resolved is None:
            missing.append(target)
            continue
        resolved_files.append(resolved)
        unique_keys.append(f"local:{os.path.normcase(str(resolved))}")

    if missing:
        searched = ", ".join(str(path) for path in resource_directories)
        missing_list = "\n".join(f"- {target}" for target in dict.fromkeys(missing))
        raise ExportError(
            "源文件引用的图片不存在，已停止导出以避免生成无图 DOCX:\n"
            f"{missing_list}\n资源搜索目录: {searched}\n"
            "请补齐图片、修正源文件路径，或使用 --resource-path 添加图片目录。"
        )

    unique_files = tuple(dict.fromkeys(str(path) for path in resolved_files))
    return ImageManifest(
        total=len(targets),
        unique=len(dict.fromkeys(unique_keys)),
        local=len(targets) - external,
        external=external,
        targets=tuple(targets),
        resolved_local_files=unique_files,
    )


def _publish_atomically(temporary_docx: Path, output: Path, force: bool) -> None:
    """Copy a verified DOCX to its final path using atomic replacement."""
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not force:
        raise ExportError(f"输出已存在；只有明确允许覆盖时才使用 --force: {output}")

    descriptor, staging_name = tempfile.mkstemp(
        prefix=f".{output.stem}-", suffix=".tmp.docx", dir=output.parent
    )
    os.close(descriptor)
    staging = Path(staging_name)
    try:
        shutil.copy2(temporary_docx, staging)
        if output.exists() and not force:
            raise ExportError(f"输出在转换过程中已出现，拒绝覆盖: {output}")
        os.replace(staging, output)
    finally:
        staging.unlink(missing_ok=True)


def export_docx(args: argparse.Namespace) -> dict[str, object]:
    """Run Pandoc, verify OMML, and publish the final DOCX."""
    source = args.input.expanduser().resolve()
    output = args.output.expanduser().resolve()
    report_path = args.report.expanduser().resolve() if args.report else None
    if not source.is_file():
        raise ExportError(f"输入文件不存在: {source}")
    if output.suffix.lower() != ".docx":
        raise ExportError(f"输出文件必须使用 .docx 扩展名: {output}")
    if output.exists() and not args.force:
        raise ExportError(f"输出已存在；只有明确允许覆盖时才使用 --force: {output}")
    if report_path == output:
        raise ExportError("JSON 报告路径不能与 DOCX 输出路径相同")
    if report_path and report_path.exists() and not args.force:
        raise ExportError(
            f"JSON 报告已存在；只有明确允许覆盖时才使用 --force: {report_path}"
        )

    input_format = _resolve_input_format(source, args.from_format)
    runtime = resolve_pandoc(args.pandoc)
    reference = (
        _validate_reference_doc(args.reference_doc) if args.reference_doc else None
    )
    resource_directories = _resource_directories(source, args.resource_path)
    resource_path = _resource_path_value(resource_directories)
    image_manifest = _inspect_source_images(
        runtime,
        source,
        input_format,
        resource_directories,
    )

    with tempfile.TemporaryDirectory(prefix="export-math-docx-") as temporary_directory:
        temporary_docx = Path(temporary_directory) / "pandoc-output.docx"
        pandoc_args = [
            f"--from={input_format}",
            "--to=docx",
            "--standalone",
            f"--resource-path={resource_path}",
        ]
        if reference:
            pandoc_args.append(f"--reference-doc={reference}")
        pandoc_args.extend([str(source), f"--output={temporary_docx}"])

        result = _run(runtime.executable, pandoc_args)
        if result.returncode != 0:
            diagnostic = (result.stderr or result.stdout or "Pandoc 未返回诊断").strip()
            raise ExportError(
                f"Pandoc 转换失败（exit {result.returncode}）:\n{diagnostic}"
            )
        if result.stderr and IMAGE_WARNING_RE.search(result.stderr):
            raise ExportError(
                "Pandoc 报告图片资源错误，已停止导出:\n" + result.stderr.strip()
            )
        if not temporary_docx.is_file() or temporary_docx.stat().st_size == 0:
            raise ExportError("Pandoc 没有生成非空 DOCX")

        verification = inspect_docx(
            temporary_docx,
            source=source,
            expected_images=image_manifest.total,
            expected_unique_images=image_manifest.unique,
        )
        if not verification.valid:
            raise ExportError(
                "DOCX 未通过 OMML 验证:\n"
                + json.dumps(asdict(verification), ensure_ascii=False, indent=2)
            )

        _publish_atomically(temporary_docx, output, args.force)

    payload: dict[str, object] = {
        "output": str(output),
        "input": str(source),
        "input_format": input_format,
        "pandoc": asdict(runtime),
        "images": asdict(image_manifest),
        "verification": {**asdict(verification), "docx": str(output)},
    }
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return payload


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description="通过 Pandoc 将 Markdown/LaTeX 数学公式导出为 Word 原生 OMML。"
    )
    parser.add_argument("input", type=Path, nargs="?", help="Markdown 或 LaTeX 输入")
    parser.add_argument("output", type=Path, nargs="?", help="最终 DOCX 输出")
    parser.add_argument("--check", action="store_true", help="只检查 Pandoc 可用性")
    parser.add_argument("--pandoc", type=Path, help="明确指定 Pandoc 可执行文件")
    parser.add_argument("--from-format", help="覆盖自动选择的 Pandoc reader")
    parser.add_argument("--reference-doc", type=Path, help="可选 Word 样式参考 DOCX")
    parser.add_argument(
        "--resource-path",
        type=Path,
        action="append",
        default=[],
        help="额外图片/资源目录，可重复传入",
    )
    parser.add_argument("--report", type=Path, help="可选 JSON 转换报告")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的输出文件")
    return parser


def main() -> int:
    """Run the exporter CLI."""
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.check:
            runtime = resolve_pandoc(args.pandoc)
            print(json.dumps(asdict(runtime), ensure_ascii=False, indent=2))
            return 0
        if args.input is None or args.output is None:
            parser.error("转换时必须同时提供 input 和 output")
        payload = export_docx(args)
    except ExportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
