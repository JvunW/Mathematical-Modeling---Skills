#!/usr/bin/env python3
"""Run portable baseline checks on a Typst or LaTeX paper project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


PLACEHOLDERS = re.compile(r"TODO|FIXME|TBD|PLACEHOLDER|待补充|待续写|示例数据", re.IGNORECASE)
INTERNAL_MARKERS = re.compile(
    r"ANALYSIS_MODELING_REPORT|RESULTS_REPORT|DRAWIO_REPORT|VERIFY_REPORT|(?:^|[\\/])reports[\\/]",
    re.IGNORECASE,
)
TYPST_INCLUDE = re.compile(r'#include\s*\(\s*["\']([^"\']+)["\']')
LATEX_INCLUDE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
TYPST_IMAGE = re.compile(r'image\s*\(\s*["\']([^"\']+)["\']')
LATEX_IMAGE = re.compile(r"\\includegraphics(?:\[[^]]*\])?\s*\{([^}]+)\}")


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

    for source in sources:
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"Source is not valid UTF-8: {source}")
            continue
        for match in PLACEHOLDERS.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"Placeholder {match.group(0)!r}: {source}:{line}")
        for match in INTERNAL_MARKERS.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            warnings.append(f"Possible internal workflow leakage: {source}:{line}")

    main_text = main.read_text(encoding="utf-8")
    include_pattern = LATEX_INCLUDE if latex else TYPST_INCLUDE
    includes = include_pattern.findall(main_text)
    if not includes:
        warnings.append("Main file has no explicit include/input; verify that a single-file paper is intentional")
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
