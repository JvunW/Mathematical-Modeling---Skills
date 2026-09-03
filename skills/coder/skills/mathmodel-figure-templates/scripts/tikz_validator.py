#!/usr/bin/env python3
"""Static geometry and structure checks for common TikZ authoring mistakes."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import re


@dataclass(frozen=True)
class Issue:
    level: str
    code: str
    line: int | None
    message: str


NODE_NAME = re.compile(r"\\node(?:\[[^]]*\])?\s*\(([^)]+)\)")
COORD = re.compile(r"\((-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\)")
DRAW = re.compile(r"\\draw(?:\[[^]]*\])?([^;]*);")


def strip_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in text.splitlines())


def validate(text: str) -> list[Issue]:
    source = strip_comments(text)
    issues: list[Issue] = []
    if source.count("\\begin{tikzpicture}") != source.count("\\end{tikzpicture}"):
        issues.append(Issue("ERROR", "tikz-balance", None, "tikzpicture begin/end count differs"))

    names: dict[str, int] = {}
    for number, line in enumerate(source.splitlines(), start=1):
        for name in NODE_NAME.findall(line):
            if name in names:
                issues.append(Issue("ERROR", "duplicate-node", number, f"node {name!r} already declared on line {names[name]}"))
            names[name] = number

    for match in DRAW.finditer(source):
        body = match.group(1)
        line = source.count("\n", 0, match.start()) + 1
        points = [(float(x), float(y)) for x, y in COORD.findall(body)]
        for first, second in zip(points, points[1:]):
            dx, dy = second[0] - first[0], second[1] - first[1]
            if math.isclose(dx, 0.0, abs_tol=1e-9) and math.isclose(dy, 0.0, abs_tol=1e-9):
                issues.append(Issue("ERROR", "zero-segment", line, f"zero-length path segment at {first}"))
            elif min(abs(dx), abs(dy)) > 0 and min(abs(dx), abs(dy)) < 0.08 and max(abs(dx), abs(dy)) > 0.5:
                issues.append(
                    Issue("WARN", "micro-slope", line, f"near-orthogonal segment {first} -> {second}; align it or make the diagonal intentional")
                )

    explicit_nodes: dict[tuple[float, float], list[str]] = {}
    node_at = re.compile(r"\\node(?:\[[^]]*\])?\s*\(([^)]+)\)\s*at\s*" + COORD.pattern)
    for match in node_at.finditer(source):
        position = (float(match.group(2)), float(match.group(3)))
        explicit_nodes.setdefault(position, []).append(match.group(1))
    for position, colocated in explicit_nodes.items():
        if len(colocated) > 1:
            issues.append(Issue("WARN", "colocated-nodes", None, f"nodes {colocated} share coordinate {position}"))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = Path(args.tex)
    if not path.is_file():
        print(f"ERROR: {path} does not exist")
        return 2
    issues = validate(path.read_text(encoding="utf-8", errors="replace"))
    if args.json:
        print(json.dumps({"path": str(path), "issues": [asdict(item) for item in issues]}, indent=2))
    else:
        for item in issues:
            location = f":{item.line}" if item.line else ""
            print(f"{item.level} {path}{location} [{item.code}] {item.message}")
        print(f"{'PASS' if not issues else 'CHECK'}: {len(issues)} issue(s)")
    if any(item.level == "ERROR" for item in issues):
        return 2
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
