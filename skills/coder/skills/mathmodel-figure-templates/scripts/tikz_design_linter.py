#!/usr/bin/env python3
"""Advisory design metrics for TikZ figures; complexity is never mandatory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


PRESETS = {
    "simple": {"elements": 5, "zones": 0, "embedded": 0},
    "pipeline": {"elements": 12, "zones": 2, "embedded": 0},
    "rich": {"elements": 24, "zones": 2, "embedded": 1},
}


def metrics(text: str) -> dict[str, int | bool]:
    nodes = len(re.findall(r"\\node\b", text))
    paths = len(re.findall(r"\\(?:draw|path)\b", text))
    fills = len(re.findall(r"\\fill\b", text))
    zones = len(re.findall(r"\bfit\s*=|on background layer|zone", text, re.I))
    embedded = len(re.findall(r"heatmap|bar\s*chart|line\s*chart|addplot|matrix of nodes|pgfplots", text, re.I))
    hero = bool(re.search(r"hero|visual\s*center|minimum width\s*=\s*(?:[5-9]|\d{2,})", text, re.I))
    return {"nodes": nodes, "paths": paths, "fills": fills, "elements": nodes + paths + fills,
            "zones": zones, "embedded": embedded, "hero": hero}


def infer_type(values: dict[str, int | bool]) -> str:
    if int(values["embedded"]) > 0 or int(values["elements"]) >= 24:
        return "rich"
    if int(values["elements"]) >= 12:
        return "pipeline"
    return "simple"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex")
    parser.add_argument("--type", choices=("auto", "simple", "pipeline", "rich"), default="auto")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = Path(args.tex)
    if not path.is_file():
        print(f"ERROR: {path} does not exist")
        return 2
    values = metrics(path.read_text(encoding="utf-8", errors="replace"))
    kind = infer_type(values) if args.type == "auto" else args.type
    threshold = PRESETS[kind]
    warnings = []
    for key in ("elements", "zones", "embedded"):
        if int(values[key]) < threshold[key]:
            warnings.append(f"{key}={values[key]} below {kind} advisory baseline {threshold[key]}")
    if kind == "rich" and not values["hero"]:
        warnings.append("rich figure has no detectable visual centre; verify the Figure Contract manually")
    report = {"path": str(path), "type": kind, "metrics": values, "warnings": warnings,
              "status": "fail" if args.strict and warnings else "advisory" if warnings else "pass"}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(json.dumps(report, indent=2))
    return 2 if args.strict and warnings else 1 if warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
