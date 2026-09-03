#!/usr/bin/env python3
"""Run the deterministic TikZ Figure QA gates and write one JSON report."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys


SCRIPT_ROOT = Path(__file__).resolve().parent


def execute(name: str, command: list[str], allowed: set[int]) -> dict:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode == 3:
        status = "skipped"
    elif completed.returncode == 1 and 1 in allowed:
        status = "advisory"
    elif completed.returncode in allowed:
        status = "pass"
    else:
        status = "fail"
    return {
        "name": name,
        "status": status,
        "returncode": completed.returncode,
        "command": command,
        "stdout": completed.stdout[-6000:],
        "stderr": completed.stderr[-6000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex")
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--type", choices=("auto", "simple", "pipeline", "rich"), default="auto")
    parser.add_argument("--reference", help="optional reference PNG for visual diff")
    parser.add_argument("--report", help="default: <stem>.figure-qa.json")
    args = parser.parse_args()

    tex = Path(args.tex).expanduser().resolve()
    if not tex.is_file():
        print(f"ERROR: {tex} does not exist", file=sys.stderr)
        return 2
    report_path = Path(args.report).expanduser().resolve() if args.report else tex.with_name(f"{tex.stem}.figure-qa.json")
    python = sys.executable
    checks = [
        execute("tikz_safety", [python, str(SCRIPT_ROOT / "check_tikz_safety.py"), str(tex), "--json"], {0}),
        execute("tikz_geometry", [python, str(SCRIPT_ROOT / "tikz_validator.py"), str(tex), "--json"], {0, 1}),
        execute("design_metrics", [python, str(SCRIPT_ROOT / "tikz_design_linter.py"), str(tex), "--type", args.type, "--json"], {0, 1}),
    ]
    if not any(item["status"] == "fail" for item in checks):
        checks.append(
            execute("compile_render", [python, str(SCRIPT_ROOT / "compile_render.py"), str(tex), "--dpi", str(args.dpi)], {0})
        )
    pdf = tex.with_suffix(".pdf")
    png = tex.with_suffix(".png")
    if pdf.is_file() and not any(item["status"] == "fail" for item in checks):
        checks.append(
            execute("pdf_geometry", [python, str(SCRIPT_ROOT / "pdf_overlap_checker.py"), str(pdf), "--json"], {0, 1, 3})
        )
    if args.reference and png.is_file() and not any(item["status"] == "fail" for item in checks):
        diff_path = tex.with_name(f"{tex.stem}.diff.png")
        checks.append(
            execute(
                "figure_diff",
                [python, str(SCRIPT_ROOT / "figure_diff.py"), str(Path(args.reference).resolve()), str(png), "--output", str(diff_path)],
                {0},
            )
        )

    failed = any(item["status"] == "fail" for item in checks)
    skipped = any(item["status"] == "skipped" for item in checks)
    advisory = any(item["status"] == "advisory" for item in checks)
    if failed:
        status = "fail"
    elif skipped:
        status = "pass_with_skips"
    elif advisory:
        status = "pass_with_advisories"
    else:
        status = "pass"
    report = {
        "schema_version": "1.0",
        "status": status,
        "source": str(tex),
        "pdf": str(pdf) if pdf.is_file() else None,
        "png": str(png) if png.is_file() else None,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "checks": checks,
        "manual_visual_qa_required": True,
        "paper_integration_qa_required": True,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "report": str(report_path)}, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
