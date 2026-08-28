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
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
OFFICE_REL_NS = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
)
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
VML_NS = "urn:schemas-microsoft-com:vml"
EQUATION_SEQUENCE_RE = re.compile(r"\bSEQ\s+(?:Equation|公式)\b", re.IGNORECASE)

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
MARKDOWN_IMAGE_RE = re.compile(
    r"!\[[^\]]*\]\(\s*(?:<(?P<angle>[^>\n]+)>|"
    r"(?P<plain>(?:\\.|[^\s)])+?))"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)",
    re.MULTILINE,
)
MARKDOWN_REFERENCE_IMAGE_RE = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\[(?P<label>[^\]]*)\]"
)
MARKDOWN_REFERENCE_DEFINITION_RE = re.compile(
    r"(?m)^[ \t]{0,3}\[(?P<label>[^\]]+)\]:[ \t]*"
    r"(?:<(?P<angle>[^>\n]+)>|(?P<plain>\S+))"
)
HTML_IMAGE_RE = re.compile(
    r"<img\b[^>]*\bsrc\s*=\s*(?:([\"'])(.*?)\1|([^\s>]+))",
    re.IGNORECASE | re.DOTALL,
)
LATEX_IMAGE_RE = re.compile(
    r"\\includegraphics(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}"
)


@dataclass(frozen=True)
class SourceMath:
    """Summary of math delimiters detected in a source file."""

    total: int
    dollar_blocks: int
    dollar_inline: int
    bracket_blocks: int
    paren_inline: int
    environments: int

    @property
    def display_total(self) -> int:
        """Return source constructs that should render as numbered display equations."""
        return self.dollar_blocks + self.bracket_blocks + self.environments


@dataclass(frozen=True)
class SourceImages:
    """Summary of image references detected in a source file."""

    total: int
    unique: int
    targets: tuple[str, ...]


@dataclass
class VerificationReport:
    """Machine-readable DOCX verification result."""

    docx: str
    valid: bool = False
    file_size: int = 0
    xml_parts_checked: int = 0
    omml_total: int = 0
    omml_paragraphs: int = 0
    expected_numbered_equations: int = 0
    equation_number_fields: int = 0
    equation_number_values: list[int] = field(default_factory=list)
    mathml_elements: int = 0
    raw_math_markers: int = 0
    expected_source_formulas: int = 0
    expected_source_images: int = 0
    expected_unique_source_images: int = 0
    media_files: int = 0
    image_relationships: int = 0
    image_occurrences: int = 0
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


def detect_image_text(text: str, suffix: str = ".md") -> SourceImages:
    """Count common Markdown, HTML, and LaTeX image references."""
    prepared = _prepare_source_text(text, suffix)
    targets: list[str] = []
    if suffix.lower() in {".md", ".markdown", ".mdown", ".mkd"}:
        for match in MARKDOWN_IMAGE_RE.finditer(prepared):
            target = match.group("angle") or match.group("plain")
            targets.append(target.replace(r"\ ", " ").strip())

        definitions: dict[str, str] = {}
        for match in MARKDOWN_REFERENCE_DEFINITION_RE.finditer(prepared):
            label = " ".join(match.group("label").split()).casefold()
            definitions[label] = (match.group("angle") or match.group("plain")).strip()
        for match in MARKDOWN_REFERENCE_IMAGE_RE.finditer(prepared):
            label_text = match.group("label") or match.group("alt")
            label = " ".join(label_text.split()).casefold()
            if label in definitions:
                targets.append(definitions[label])

        for match in HTML_IMAGE_RE.finditer(prepared):
            targets.append((match.group(2) or match.group(3)).strip())
    elif suffix.lower() in {".tex", ".latex"}:
        targets.extend(match.strip() for match in LATEX_IMAGE_RE.findall(prepared))

    unique_targets = tuple(dict.fromkeys(targets))
    return SourceImages(
        total=len(targets),
        unique=len(unique_targets),
        targets=tuple(targets),
    )


def detect_source_images(source: Path) -> SourceImages:
    """Read a UTF-8 source file and count its image references."""
    text = source.read_text(encoding="utf-8-sig")
    return detect_image_text(text, source.suffix)


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
    expected_images: int | None = None,
    expected_unique_images: int | None = None,
    expected_numbered: int | None = None,
) -> VerificationReport:
    """Inspect DOCX package integrity and native OMML content.

    Args:
        docx: DOCX file to inspect.
        source: Optional Markdown or LaTeX source used for formula-count checks.
        expected_min: Optional minimum number of OMML math objects.
        expected_images: Optional minimum number of embedded image occurrences.
        expected_unique_images: Optional minimum number of packaged media files.
        expected_numbered: Optional minimum number of numbered display equations.

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
    source_images = SourceImages(0, 0, ())
    if source is not None:
        resolved_source = source.expanduser().resolve()
        if not resolved_source.is_file():
            report.errors.append(f"源文件不存在: {resolved_source}")
        else:
            try:
                source_math = detect_source_math(resolved_source)
                source_images = detect_source_images(resolved_source)
            except UnicodeError as exc:
                report.errors.append(f"源文件不是有效 UTF-8: {exc}")

    report.expected_source_formulas = max(expected_min or 0, source_math.total)
    report.expected_numbered_equations = max(
        expected_numbered or 0, source_math.display_total
    )
    report.expected_source_images = max(expected_images or 0, source_images.total)
    report.expected_unique_source_images = max(
        expected_unique_images or 0, source_images.unique
    )

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
            relationship_parts = [
                name
                for name in names
                if name.startswith("word/")
                and "/_rels/" in name
                and name.endswith(".rels")
            ]
            for part in relationship_parts:
                try:
                    root = ElementTree.fromstring(archive.read(part))
                except ElementTree.ParseError as exc:
                    report.errors.append(f"XML 无法解析 ({part}): {exc}")
                    continue
                report.image_relationships += sum(
                    1
                    for node in root.findall(f".//{{{PACKAGE_REL_NS}}}Relationship")
                    if node.attrib.get("Type", "").endswith("/image")
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
                simple_fields = root.findall(f".//{{{WORD_NS}}}fldSimple")
                for field in simple_fields:
                    instruction = field.attrib.get(f"{{{WORD_NS}}}instr", "")
                    if not EQUATION_SEQUENCE_RE.search(instruction):
                        continue
                    report.equation_number_fields += 1
                    value = "".join(
                        node.text or ""
                        for node in field.findall(f".//{{{WORD_NS}}}t")
                    ).strip()
                    if value.isdigit():
                        report.equation_number_values.append(int(value))
                report.equation_number_fields += sum(
                    1
                    for node in root.findall(f".//{{{WORD_NS}}}instrText")
                    if EQUATION_SEQUENCE_RE.search(node.text or "")
                )
                report.image_occurrences += sum(
                    1
                    for node in root.findall(f".//{{{DRAWING_NS}}}blip")
                    if node.attrib.get(f"{{{OFFICE_REL_NS}}}embed")
                    or node.attrib.get(f"{{{OFFICE_REL_NS}}}link")
                )
                report.image_occurrences += sum(
                    1
                    for node in root.findall(f".//{{{VML_NS}}}imagedata")
                    if node.attrib.get(f"{{{OFFICE_REL_NS}}}id")
                )
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
    if report.expected_numbered_equations > report.equation_number_fields:
        report.errors.append(
            "Word 公式编号字段少于源行间公式数量: "
            f"expected>={report.expected_numbered_equations}, "
            f"actual={report.equation_number_fields}"
        )
    if report.equation_number_values:
        expected_values = list(range(1, len(report.equation_number_values) + 1))
        if report.equation_number_values != expected_values:
            report.errors.append(
                "Word 公式编号不连续或顺序错误: "
                f"actual={report.equation_number_values}"
            )
    if report.mathml_elements:
        report.errors.append(
            f"发现 {report.mathml_elements} 个 MathML 节点，目标格式应为 Word OMML"
        )
    if report.raw_math_markers:
        report.errors.append(
            f"Word 正文仍包含 {report.raw_math_markers} 个原始 TeX 数学定界结构"
        )
    if report.expected_source_images > report.image_occurrences:
        report.errors.append(
            "Word 图片节点少于源图片引用数量: "
            f"expected>={report.expected_source_images}, "
            f"actual={report.image_occurrences}"
        )
    if report.expected_unique_source_images > report.media_files:
        report.errors.append(
            "DOCX 媒体文件少于源文件的唯一图片数量: "
            f"expected>={report.expected_unique_source_images}, "
            f"actual={report.media_files}"
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
    parser.add_argument(
        "--expected-images", type=int, default=None, help="要求的最少图片节点数量"
    )
    parser.add_argument(
        "--expected-unique-images",
        type=int,
        default=None,
        help="要求的最少唯一媒体文件数量",
    )
    parser.add_argument(
        "--expected-numbered",
        type=int,
        default=None,
        help="要求的最少已编号行间公式数量",
    )
    parser.add_argument("--report", type=Path, help="可选 JSON 报告输出路径")
    return parser


def main() -> int:
    """Run the verifier CLI."""
    args = build_parser().parse_args()
    for option, value in (
        ("--expected-min", args.expected_min),
        ("--expected-images", args.expected_images),
        ("--expected-unique-images", args.expected_unique_images),
        ("--expected-numbered", args.expected_numbered),
    ):
        if value is not None and value < 0:
            print(f"ERROR: {option} 不能为负数", file=sys.stderr)
            return 2

    report = inspect_docx(
        args.docx,
        args.source,
        args.expected_min,
        args.expected_images,
        args.expected_unique_images,
        args.expected_numbered,
    )
    if args.report:
        _write_report(report, args.report)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
