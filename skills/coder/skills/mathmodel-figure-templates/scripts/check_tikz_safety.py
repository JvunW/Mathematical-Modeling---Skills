#!/usr/bin/env python3
"""Conservative static safety checks for TikZ/LaTeX figure sources."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    line: int | None = None


FORBIDDEN = (
    ("shell-escape", re.compile(r"\\(?:immediate\s*)?\\?write18\b|\\ShellEscape\b", re.I),
     "shell escape is forbidden for figure compilation"),
    ("direct-lua", re.compile(r"\\directlua\b", re.I),
     "embedded Lua execution is forbidden"),
    ("pipe-input", re.compile(r"\\input\s*\{\s*\|", re.I),
     "piped command input is forbidden"),
    ("external-process", re.compile(r"\\usepackage(?:\[[^]]*\])?\{(?:minted|pythontex|sagetex)\}", re.I),
     "package requires or commonly invokes external processes"),
)

EDGE_LABEL = re.compile(r"\\draw\b[^;\n]*--\s*node\s*\{", re.MULTILINE)
LONG_NODE = re.compile(r"\\node(?:\[[^]]*\])?\s*(?:\([^)]*\))?\s*\{([^{}]{90,})\}")
ABSOLUTE_INCLUDE = re.compile(
    r"\\(?:input|include|includegraphics)\s*(?:\[[^]]*\])?\s*\{\s*(?:[A-Za-z]:[\\/]|/|\\\\)",
    re.I,
)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check_text(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for code, pattern, message in FORBIDDEN:
        for match in pattern.finditer(text):
            findings.append(Finding(code, message, line_number(text, match.start())))

    for match in ABSOLUTE_INCLUDE.finditer(text):
        findings.append(
            Finding(
                "absolute-include",
                "absolute include path is not portable; use a workspace-relative asset",
                line_number(text, match.start()),
            )
        )

    if text.count("\\begin{tikzpicture}") != text.count("\\end{tikzpicture}"):
        findings.append(Finding("tikz-balance", "mismatched tikzpicture begin/end count"))
    if "\\begin{document}" in text and "\\documentclass" not in text:
        findings.append(Finding("documentclass", "document body has no documentclass"))

    for match in EDGE_LABEL.finditer(text):
        findings.append(
            Finding(
                "edge-label-position",
                "inline edge label has no explicit above/below/pos placement",
                line_number(text, match.start()),
            )
        )
    for match in LONG_NODE.finditer(text):
        snippet = " ".join(match.group(1).split())[:80]
        findings.append(
            Finding(
                "long-node",
                f"long node text needs text width or an intentional line break: {snippet!r}",
                line_number(text, match.start()),
            )
        )

    for number, line in enumerate(text.splitlines(), start=1):
        if "rotate=90" in line and "anchor=" not in line:
            findings.append(
                Finding("rotated-anchor", "rotated node needs an explicit anchor", number)
            )
    return findings


def check_file(path: Path) -> list[Finding]:
    return check_text(path.read_text(encoding="utf-8", errors="replace"))


def collect_inputs(values: list[str]) -> list[Path]:
    result: list[Path] = []
    for value in values:
        path = Path(value)
        result.extend(sorted(path.rglob("*.tex")) if path.is_dir() else [path])
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="TikZ .tex files or directories")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    report = []
    failed = False
    for path in collect_inputs(args.paths):
        if not path.is_file():
            findings = [Finding("missing", "file does not exist")]
        else:
            findings = check_file(path)
        failed = failed or bool(findings)
        report.append(
            {
                "path": str(path),
                "status": "fail" if findings else "pass",
                "findings": [finding.__dict__ for finding in findings],
            }
        )

    if args.json:
        print(json.dumps({"status": "fail" if failed else "pass", "files": report}, indent=2))
    else:
        for item in report:
            for finding in item["findings"]:
                location = f":{finding['line']}" if finding["line"] else ""
                print(f"ERROR {item['path']}{location} [{finding['code']}] {finding['message']}")
        print(f"{'FAILED' if failed else 'OK'}: {len(report)} file(s) checked")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
