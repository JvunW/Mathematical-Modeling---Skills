#!/usr/bin/env python3
"""Render PDF pages to PNG with the first available local rasterizer."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--dpi", type=int, default=160)
    return parser.parse_args()


def find_executable(name: str) -> str | None:
    """Locate a tool, resolving common Windows command wrappers when possible."""
    found = shutil.which(name)
    if found is None:
        return None
    path = Path(found)
    if sys.platform == "win32" and path.suffix.lower() in {".cmd", ".bat"}:
        for ancestor in list(path.parents)[:4]:
            candidates = (
                ancestor / "native" / "poppler" / "Library" / "bin" / f"{name}.exe",
                ancestor / "Library" / "bin" / f"{name}.exe",
                ancestor / f"{name}.exe",
            )
            if executable := next((candidate for candidate in candidates if candidate.is_file()), None):
                return str(executable)
    return found


def main() -> int:
    """Select a renderer and rasterize the PDF."""
    args = parse_args()
    pdf = args.pdf.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    if not pdf.is_file() or pdf.stat().st_size == 0:
        print(f"ERROR: PDF is missing or empty: {pdf}", file=sys.stderr)
        return 2
    output_dir.mkdir(parents=True, exist_ok=True)

    if executable := find_executable("pdftoppm"):
        command = [executable, "-png", "-r", str(args.dpi), str(pdf), str(output_dir / "page")]
    elif executable := find_executable("mutool"):
        command = [executable, "draw", "-r", str(args.dpi), "-o", str(output_dir / "page-%03d.png"), str(pdf)]
    elif executable := find_executable("magick"):
        command = [executable, "-density", str(args.dpi), str(pdf), str(output_dir / "page-%03d.png")]
    else:
        print("ERROR: no PDF rasterizer found (pdftoppm, mutool, or magick).", file=sys.stderr)
        return 3

    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        print(f"ERROR: renderer exited with status {completed.returncode}.", file=sys.stderr)
        return completed.returncode
    pages = sorted(output_dir.glob("*.png"))
    if not pages:
        print("ERROR: renderer produced no PNG pages.", file=sys.stderr)
        return 4
    for page in pages:
        print(page)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
