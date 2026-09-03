#!/usr/bin/env python3
"""Safely compile a standalone TikZ file and render a PNG preview."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

from check_tikz_safety import check_file


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def nonblank_png(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 200:
        return False
    try:
        from PIL import Image, ImageChops
    except ImportError:
        return path.stat().st_size > 1000
    with Image.open(path).convert("RGB") as image:
        background = Image.new("RGB", image.size, "white")
        return ImageChops.difference(image, background).getbbox() is not None


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex", help="standalone .tex file")
    parser.add_argument("--engine", default="xelatex", choices=("xelatex", "pdflatex", "lualatex"))
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument("--output-dir", help="default: the source directory")
    parser.add_argument("--report", help="default: <stem>.compile.json")
    parser.add_argument("--skip-safety", action="store_true", help="only for an already-audited source")
    args = parser.parse_args(argv)

    tex = Path(args.tex).expanduser().resolve()
    if not tex.is_file():
        print(f"ERROR: source does not exist: {tex}", file=sys.stderr)
        return 2
    if tex.suffix.lower() != ".tex":
        print(f"ERROR: expected a .tex source: {tex}", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else tex.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = Path(args.report).expanduser().resolve() if args.report else output_dir / f"{tex.stem}.compile.json"
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "source": str(tex),
        "engine": args.engine,
        "dpi": args.dpi,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "checks": [],
    }

    if not args.skip_safety:
        findings = check_file(tex)
        report["checks"].append(
            {"name": "tikz_safety", "status": "fail" if findings else "pass",
             "findings": [finding.__dict__ for finding in findings]}
        )
        if findings:
            report["status"] = "fail"
            write_report(report_path, report)
            for finding in findings:
                print(f"ERROR [{finding.code}] {finding.message}", file=sys.stderr)
            return 1

    engine = shutil.which(args.engine)
    renderer = shutil.which("pdftoppm")
    missing = [name for name, value in ((args.engine, engine), ("pdftoppm", renderer)) if not value]
    if missing:
        report.update({"status": "blocked", "missing_tools": missing})
        write_report(report_path, report)
        print("BLOCKED: missing tool(s): " + ", ".join(missing), file=sys.stderr)
        return 3

    compile_command = [
        engine,
        "-no-shell-escape",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        f"-output-directory={output_dir}",
        tex.name,
    ]
    completed = run(compile_command, tex.parent)
    report["checks"].append(
        {
            "name": "latex_compile",
            "status": "pass" if completed.returncode == 0 else "fail",
            "command": compile_command,
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
        }
    )
    pdf = output_dir / f"{tex.stem}.pdf"
    log = output_dir / f"{tex.stem}.log"
    if completed.returncode or not pdf.is_file():
        report["status"] = "fail"
        write_report(report_path, report)
        print((completed.stdout + completed.stderr)[-4000:], file=sys.stderr)
        return 1

    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        page_info = run([pdfinfo, str(pdf)], output_dir)
        page_match = re.search(r"(?m)^Pages:\s+(\d+)\s*$", page_info.stdout)
        page_count = int(page_match.group(1)) if page_match else None
        page_status = "pass" if page_count == 1 else "fail"
        report["checks"].append(
            {"name": "single_page", "status": page_status, "pages": page_count,
             "command": [pdfinfo, str(pdf)]}
        )
        if page_count != 1:
            report["status"] = "fail"
            write_report(report_path, report)
            print(f"ERROR: standalone figure must be single-page; found {page_count}", file=sys.stderr)
            return 1
    else:
        report["checks"].append(
            {"name": "single_page", "status": "skipped", "reason": "pdfinfo is unavailable"}
        )

    log_text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    missing_glyphs = [line for line in log_text.splitlines() if "Missing character" in line]
    report["checks"].append(
        {"name": "missing_glyphs", "status": "fail" if missing_glyphs else "pass", "lines": missing_glyphs[:50]}
    )
    if missing_glyphs:
        report["status"] = "fail"
        write_report(report_path, report)
        print("ERROR: LaTeX log reports missing characters", file=sys.stderr)
        return 1

    prefix = output_dir / tex.stem
    render_command = [renderer, "-png", "-r", str(args.dpi), "-singlefile", str(pdf), str(prefix)]
    rendered = run(render_command, output_dir)
    png = output_dir / f"{tex.stem}.png"
    render_ok = rendered.returncode == 0 and nonblank_png(png)
    report["checks"].append(
        {"name": "png_render", "status": "pass" if render_ok else "fail",
         "command": render_command, "returncode": rendered.returncode}
    )
    report.update({"status": "pass" if render_ok else "fail", "pdf": str(pdf), "png": str(png)})
    write_report(report_path, report)
    if not render_ok:
        print((rendered.stdout + rendered.stderr)[-4000:], file=sys.stderr)
        print(f"ERROR: PNG is missing or blank: {png}", file=sys.stderr)
        return 1

    print(f"OK: {tex}")
    print(f"PDF: {pdf}")
    print(f"PNG: {png}")
    print(f"REPORT: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
