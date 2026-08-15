#!/usr/bin/env python3
"""Verify that a DOCX contains native Word OMML equations."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from xml.etree import ElementTree

OMML_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MATHML_NS = "http://www.w3.org/1998/Math/MathML"

BLOCK_DOLLAR_RE = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$", re.DOTALL)
INLINE_DOLLAR_RE = re.compile(
    r"(?<![\\$])\$(?!\$)(.+?)(?<![\\$])\$(?!\$)", re.DOTALL
)
PAREN_MATH_RE = re.compile(r"\\\((.+?)\\\)", re.DOTALL)
BRACKET_MATH_RE = re.compile(r"\\\[(.+?)\\\]", re.DOTALL)
MATH_ENV_RE = re.compile(
    r"\\begin\{(?P<env>equation\*?|align\*?|alignat\*?|gather\*?|"
    r"multline\*?|displaymath|math)\}.*?\\end\{(?P=env)\}",
    re.DOTALL,
)
FENCED_CODE_RE = re.compile(
    r"(?ms)^[ \t]*(?P<fence>`{3,}|~{3,})[^\n]*\n.*?^[ \t]*(?P=fence)[ \t]*$"
)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


@dataclass(frozen=True)
class SourceMath:
    """Summary of math delimiters detected in a source file."""

    total: int
    dollar_blocks: int
    dollar_inline: int
    bracket_blocks: int
    paren_inline: int
    environments: int


@dataclass
class VerificationReport:
    """Machine-readable DOCX verification result."""

    docx: str
    valid: bool = False
    file_size: int = 0
    xml_parts_checked: int = 0
    omml_total: int = 0
    omml_paragraphs: int = 0
    mathml_elements: int = 0
    raw_math_markers: int = 0
    expected_source_formulas: int = 0
    media_files: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _prepare_source_text(text: str, suffix: str) -> str:
    """Remove regions that should not be interpreted as math source."""
    if suffix.lower() in {".md", ".markdown", ".mdown", ".mkd"}:
        text = FENCED_CODE_RE.sub("", text)
        return INLINE_CODE_RE.sub("", text)
    if suffix.lower() in {".tex", ".latex"}:
        return re.sub(r"(?m)(?<!\\)%.*$", "", text)
    return text


def detect_math_text(text: str, suffix: str = ".md") -> SourceMath:
    """Count common Markdown and LaTeX math constructs in text.

    Args:
        text: Source text to inspect.
        suffix: Source extension used to select code/comment stripping.

    Returns:
        Counts for each supported math delimiter family.
    """
    prepared = _prepare_source_text(text, suffix)
    dollar_blocks = len(BLOCK_DOLLAR_RE.findall(prepared))
    without_dollar_blocks = BLOCK_DOLLAR_RE.sub("", prepared)
    dollar_inline = len(INLINE_DOLLAR_RE.findall(without_dollar_blocks))
    bracket_blocks = len(BRACKET_MATH_RE.findall(prepared))
    paren_inline = len(PAREN_MATH_RE.findall(prepared))
    environments = len(MATH_ENV_RE.findall(prepared))
    total = (
        dollar_blocks
        + dollar_inline
        + bracket_blocks
        + paren_inline
        + environments
    )
    return SourceMath(
        total=total,
        dollar_blocks=dollar_blocks,
        dollar_inline=dollar_inline,
        bracket_blocks=bracket_blocks,
        paren_inline=paren_inline,
        environments=environments,
    )


def detect_source_math(source: Path) -> SourceMath:
    """Read a UTF-8 source file and count its math constructs."""
    text = source.read_text(encoding="utf-8-sig")
    return detect_math_text(text, source.suffix)


def _relevant_word_xml(names: list[str]) -> list[str]:
    """Return WordprocessingML parts that can contain visible equations."""
    pattern = re.compile(
        r"^word/(?:document|footnotes|endnotes|comments|header\d+|footer\d+)\.xml$"
    )
    return [name for name in names if pattern.match(name)]


def inspect_docx(
    docx: Path,
    source: Path | None = None,
    expected_min: int | None = None,
) -> VerificationReport:
    """Inspect DOCX package integrity and native OMML content.

    Args:
        docx: DOCX file to inspect.
        source: Optional Markdown or LaTeX source used for formula-count checks.
        expected_min: Optional minimum number of OMML math objects.

    Returns:
        Structured verification report. Invalid packages are reported, not raised.
    """
    resolved = docx.expanduser().resolve()
    report = VerificationReport(docx=str(resolved))
    if not resolved.is_file():
        report.errors.append(f"DOCX 文件不存在: {resolved}")
        return report

    report.file_size = resolved.stat().st_size
    if report.file_size == 0:
        report.errors.append("DOCX 文件为空")
        return report

    source_math = SourceMath(0, 0, 0, 0, 0, 0)
    if source is not None:
        resolved_source = source.expanduser().resolve()
        if not resolved_source.is_file():
            report.errors.append(f"源文件不存在: {resolved_source}")
        else:
            try:
                source_math = detect_source_math(resolved_source)
            except UnicodeError as exc:
                report.errors.append(f"源文件不是有效 UTF-8: {exc}")

    report.expected_source_formulas = max(expected_min or 0, source_math.total)

    try:
        with zipfile.ZipFile(resolved) as archive:
            bad_member = archive.testzip()
            if bad_member:
                report.errors.append(f"DOCX ZIP CRC 校验失败: {bad_member}")

            names = archive.namelist()
            if "word/document.xml" not in names:
                report.errors.append("DOCX 缺少 word/document.xml")

            report.media_files = sum(
                1
                for name in names
                if name.startswith("word/media/") and not name.endswith("/")
            )
            xml_parts = _relevant_word_xml(names)
            report.xml_parts_checked = len(xml_parts)

            visible_chunks: list[str] = []
            for part in xml_parts:
                try:
                    root = ElementTree.fromstring(archive.read(part))
                except ElementTree.ParseError as exc:
                    report.errors.append(f"XML 无法解析 ({part}): {exc}")
                    continue

                report.omml_total += len(root.findall(f".//{{{OMML_NS}}}oMath"))
                report.omml_paragraphs += len(
                    root.findall(f".//{{{OMML_NS}}}oMathPara")
                )
                report.mathml_elements += len(root.findall(f".//{{{MATHML_NS}}}*"))
                visible_chunks.extend(
                    node.text or "" for node in root.findall(f".//{{{WORD_NS}}}t")
                )

            raw_math = detect_math_text(" ".join(visible_chunks), ".md")
            report.raw_math_markers = raw_math.total
    except (OSError, zipfile.BadZipFile) as exc:
        report.errors.append(f"不是有效的 DOCX ZIP 包: {exc}")
        return report

    if report.expected_source_formulas > report.omml_total:
        report.errors.append(
            "OMML 数量少于源公式数量: "
            f"expected>={report.expected_source_formulas}, actual={report.omml_total}"
        )
    if report.mathml_elements:
        report.errors.append(
            f"发现 {report.mathml_elements} 个 MathML 节点，目标格式应为 Word OMML"
        )
    if report.raw_math_markers:
        report.errors.append(
            f"Word 正文仍包含 {report.raw_math_markers} 个原始 TeX 数学定界结构"
        )
    if report.expected_source_formulas == 0 and report.omml_total == 0:
        report.warnings.append("源文件未检测到公式，DOCX 中也没有 OMML；仅验证了文档结构")

    report.valid = not report.errors
    return report


def _write_report(report: VerificationReport, destination: Path) -> None:
    """Write a JSON verification report."""
    resolved = destination.expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description="验证 DOCX 中的 LaTeX 数学公式是否已转换为 Word 原生 OMML。"
    )
    parser.add_argument("docx", type=Path, help="待验证的 DOCX 文件")
    parser.add_argument("--source", type=Path, help="可选 Markdown/LaTeX 源文件")
    parser.add_argument(
        "--expected-min", type=int, default=None, help="要求的最少 OMML 对象数量"
    )
    parser.add_argument("--report", type=Path, help="可选 JSON 报告输出路径")
    return parser


def main() -> int:
    """Run the verifier CLI."""
    args = build_parser().parse_args()
    if args.expected_min is not None and args.expected_min < 0:
        print("ERROR: --expected-min 不能为负数", file=sys.stderr)
        return 2

    report = inspect_docx(args.docx, args.source, args.expected_min)
    if args.report:
        _write_report(report, args.report)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
