#!/usr/bin/env python3
"""Run portable baseline checks on a Typst or LaTeX paper project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


PLACEHOLDERS = re.compile(r"TODO|FIXME|TBD|PLACEHOLDER|待补充|待续写|示例数据", re.IGNORECASE)
SAMPLE_CONTENT = re.compile(
    r"论文标题|中文摘要内容：问题概述|关键词1|数学建模是解决实际问题的重要工具|"
    r"对给定数据集进行分析和预测，要求模型具有泛化能力|"
    r"考虑多因素影响，改进和优化模型，提高预测精度|"
    r"结合实际约束条件，设计最优策略方案|"
    r"采用多元线性回归作为基础模型|"
    r"随机森林的测试集\s*\$?R\^?2\$?\s*达到\s*0\.896|"
    r"采用遗传算法（种群规模\s*200|data\s*=\s*pd\.read_csv\(['\"]data\.csv",
    re.IGNORECASE,
)
INTERNAL_MARKERS = re.compile(
    r"ANALYSIS_MODELING_REPORT|RESULTS_REPORT|DRAWIO_REPORT|VERIFY_REPORT|(?:^|[\\/])reports[\\/]",
    re.IGNORECASE,
)
TYPST_INCLUDE = re.compile(r'#include\s*\(\s*["\']([^"\']+)["\']')
LATEX_INCLUDE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
TYPST_IMAGE = re.compile(r'image\s*\(\s*["\']([^"\']+)["\']')
LATEX_IMAGE = re.compile(r"\\includegraphics(?:\[[^]]*\])?\s*\{([^}]+)\}")
PROBLEM_FILE = re.compile(r"(?:^|[\\/])(?:\d+_)?problem[^\\/]*\.(?:tex|typ)$", re.IGNORECASE)
FORMULA = re.compile(r"\\begin\s*\{(?:equation|align|gather|multline)\}|\\\[|\$[^$\n]+\$|#math\.equation", re.IGNORECASE)
EVIDENCE = re.compile(r"\\begin\s*\{(?:table|figure)\}|#figure\s*\(", re.IGNORECASE)
VALIDATION = re.compile(r"验证|检验|敏感性|稳定性|交叉验证|残差|显著性|误差|AUC|\bR\^?2\b|灵敏度|特异度|局限|不足", re.IGNORECASE)
CODE_LISTING = re.compile(r"\\lstinputlisting|\\begin\s*\{lstlisting\}|#raw\s*\(", re.IGNORECASE)
LATEX_TABLE = re.compile(r"\\begin\s*\{table\}", re.IGNORECASE)
LATEX_FIGURE = re.compile(r"\\begin\s*\{figure\}", re.IGNORECASE)
LATEX_SUBSECTION = re.compile(r"\\subsection\*?\s*\{", re.IGNORECASE)
TYPST_SUBSECTION = re.compile(r"^==\s+", re.MULTILINE)
LATEX_CONTENT_BLOCK = re.compile(
    r"\\begin\s*\{(?:table|figure|equation|equation\*|align|align\*|gather|gather\*)\}.*?"
    r"\\end\s*\{(?:table|figure|equation|equation\*|align|align\*|gather|gather\*)\}",
    re.IGNORECASE | re.DOTALL,
)
LATEX_COMMAND = re.compile(r"\\[A-Za-z@]+\*?(?:\s*\[[^]]*\])?")


def visible_content_chars(text: str, *, latex: bool) -> int:
    """Approximate prose length without counting LaTeX/Typst scaffolding."""
    cleaned = re.sub(r"(?m)^\s*%.*$", "", text) if latex else text
    if latex:
        cleaned = LATEX_CONTENT_BLOCK.sub(" ", cleaned)
        cleaned = LATEX_COMMAND.sub(" ", cleaned)
    cleaned = re.sub(r"[{}\\$#*_`~]", "", cleaned)
    return len(re.sub(r"\s+", "", cleaned))


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-dir", required=True, type=Path)
    parser.add_argument("--main", required=True, type=Path)
    parser.add_argument("--sections-dir", type=Path)
    parser.add_argument("--references", type=Path)
    parser.add_argument("--figures-dir", type=Path)
    parser.add_argument("--results-file", type=Path)
    parser.add_argument("--problem-analysis", type=Path)
    parser.add_argument("--all-results", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--output", type=Path, help="Also write the report to a file")
    return parser.parse_args()


def resolve_path(path: Path | None, base: Path) -> Path | None:
    """Resolve an optional path relative to a base directory."""
    if path is None:
        return None
    return (path if path.is_absolute() else base / path).resolve()


def candidate_exists(path: Path, *, latex: bool) -> bool:
    """Check a referenced file, including common omitted LaTeX extensions."""
    if path.is_file():
        return True
    suffixes = (".tex",) if latex else ()
    if latex and path.suffix == "":
        suffixes = (".pdf", ".png", ".jpg", ".jpeg", ".svg", ".tex")
    return any(path.with_suffix(suffix).is_file() for suffix in suffixes)


def scan(args: argparse.Namespace) -> dict:
    """Inspect paper sources and return errors, warnings, and facts."""
    paper_dir = args.paper_dir.expanduser().resolve()
    main = resolve_path(args.main, paper_dir)
    errors: list[str] = []
    warnings: list[str] = []
    facts: list[str] = []

    if not paper_dir.is_dir():
        errors.append(f"Paper directory does not exist: {paper_dir}")
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "facts": facts}
    if main is None or not main.is_file():
        errors.append(f"Main file does not exist: {main}")
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "facts": facts}
    if main.suffix.lower() not in {".typ", ".tex"}:
        errors.append("Main file must use .typ or .tex")
        return {"status": "FAIL", "errors": errors, "warnings": warnings, "facts": facts}

    latex = main.suffix.lower() == ".tex"
    extension = ".tex" if latex else ".typ"
    sources = sorted(paper_dir.rglob(f"*{extension}"))
    facts.append(f"Scanned {len(sources)} {extension} source file(s)")
    table_count = 0
    figure_count = 0

    content_plan = paper_dir.parent / "reports" / "PAPER_CONTENT_PLAN.md"
    content_plan_text = ""
    if not content_plan.is_file():
        errors.append(f"Missing content plan: {content_plan}")
    else:
        content_plan_text = content_plan.read_text(encoding="utf-8", errors="replace")
        required_plan_fields = ("目标小节", "核心论点", "证据文件", "预期表/图", "状态")
        missing_plan_fields = [field for field in required_plan_fields if field not in content_plan_text]
        if missing_plan_fields:
            errors.append(
                "Content plan is missing fields: " + ", ".join(missing_plan_fields)
            )

    for source in sources:
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"Source is not valid UTF-8: {source}")
            continue
        for match in PLACEHOLDERS.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"Placeholder {match.group(0)!r}: {source}:{line}")
        for match in SAMPLE_CONTENT.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"Template sample content {match.group(0)!r}: {source}:{line}")
        for match in INTERNAL_MARKERS.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            warnings.append(f"Possible internal workflow leakage: {source}:{line}")
        if PROBLEM_FILE.search(str(source)):
            missing = []
            if not FORMULA.search(text):
                missing.append("model formula/objective")
            if not EVIDENCE.search(text):
                missing.append("result table/figure")
            if not VALIDATION.search(text):
                missing.append("validation, stability, or boundary discussion")
            if missing:
                errors.append(f"Incomplete problem section {source.name}: missing {', '.join(missing)}")
            subsection_count = len(LATEX_SUBSECTION.findall(text)) if latex else len(TYPST_SUBSECTION.findall(text))
            content_chars = visible_content_chars(text, latex=latex)
            if subsection_count < 3:
                errors.append(
                    f"Incomplete problem section {source.name}: {subsection_count} subsection(s), "
                    "expected at least 3 (model, algorithm/parameters, results/validation)"
                )
            if content_chars < 900:
                errors.append(
                    f"Incomplete problem section {source.name}: about {content_chars} visible characters, "
                    "expected at least 900 before visual/page review"
                )
        if latex:
            table_count += len(LATEX_TABLE.findall(text))
            figure_count += len(LATEX_FIGURE.findall(text))

    appendix = next((source for source in sources if source.name.lower() in {"a_code.tex", "a_code.typ"}), None)
    if appendix is not None and not CODE_LISTING.search(appendix.read_text(encoding="utf-8", errors="replace")):
        warnings.append("Code appendix has no embedded source listing")
    if latex:
        facts.append(f"Found {table_count} table(s) and {figure_count} figure(s)")
        if table_count > 10:
            warnings.append(f"正文表格数量偏多: {table_count} (建议不超过 10)")
        if figure_count > 8:
            warnings.append(f"正文图片数量偏多: {figure_count} (建议不超过 8)")

    if "EVIDENCE_GAP" in content_plan_text:
        body_sources = "\n".join(
            source.read_text(encoding="utf-8", errors="replace")
            for source in sources
            if source.name.lower() not in {"a_code.tex", "a_code.typ"}
        )
        if not re.search(r"局限|限制|缺少|不足|无法|未能|证据", body_sources):
            warnings.append("Content plan contains EVIDENCE_GAP but body has no limitation statement")

    main_text = main.read_text(encoding="utf-8")
    include_pattern = LATEX_INCLUDE if latex else TYPST_INCLUDE
    includes = include_pattern.findall(main_text)
    if not includes:
        warnings.append("Main file has no explicit include/input; verify that a single-file paper is intentional")
    problem_sources = [source for source in sources if PROBLEM_FILE.search(str(source))]
    problem_includes = [value for value in includes if re.search(r"problem", value, re.IGNORECASE)]
    if problem_sources and not problem_includes:
        errors.append("Main file does not include any problem section")
    for value in includes:
        target = (main.parent / value).resolve()
        if not candidate_exists(target, latex=latex):
            errors.append(f"Missing included source: {value} (from {main})")

    image_pattern = LATEX_IMAGE if latex else TYPST_IMAGE
    for source in sources:
        text = source.read_text(encoding="utf-8", errors="replace")
        for value in image_pattern.findall(text):
            target = (source.parent / value).resolve()
            if not candidate_exists(target, latex=latex):
                errors.append(f"Missing referenced image: {value} (from {source})")

    sections_dir = resolve_path(args.sections_dir, paper_dir)
    if sections_dir is not None and not sections_dir.is_dir():
        warnings.append(f"Sections directory does not exist: {sections_dir}")
    references = resolve_path(args.references, paper_dir)
    if references is not None and not references.is_file():
        errors.append(f"References file does not exist: {references}")
    figures_dir = resolve_path(args.figures_dir, paper_dir)
    if figures_dir is not None and not figures_dir.is_dir():
        warnings.append(f"Figures directory does not exist: {figures_dir}")

    for label, value in (
        ("results", args.results_file),
        ("problem analysis", args.problem_analysis),
        ("all results", args.all_results),
    ):
        path = resolve_path(value, paper_dir)
        if path is not None and not path.is_file():
            warnings.append(f"Declared {label} file does not exist: {path}")

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    return {"status": status, "errors": errors, "warnings": warnings, "facts": facts}


def format_text(report: dict) -> str:
    """Format a readable report."""
    lines = [f"STATUS: {report['status']}"]
    for heading, key in (("ERRORS", "errors"), ("WARNINGS", "warnings"), ("FACTS", "facts")):
        lines.append(f"\n{heading}")
        values = report[key]
        lines.extend(f"- {value}" for value in values) if values else lines.append("- none")
    return "\n".join(lines) + "\n"


def main() -> int:
    """Run checks, print the report, and return failure on hard errors."""
    args = parse_args()
    report = scan(args)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.json else format_text(report)
    print(rendered, end="")
    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
