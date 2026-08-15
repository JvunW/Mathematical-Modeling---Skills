#!/usr/bin/env python3
"""Export a Draw.io source file with a locally installed Draw.io CLI."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


def find_drawio(explicit: str | None) -> str | None:
    """Return an available Draw.io executable path."""
    candidates = [explicit, os.environ.get("DRAWIO_BIN")]
    for name in ("drawio", "draw.io", "draw.io.exe", "drawio.exe"):
        candidates.append(shutil.which(name))

    if sys.platform == "win32":
        for root_name in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
            root = os.environ.get(root_name)
            if root:
                candidates.extend(
                    [
                        str(Path(root) / "draw.io" / "draw.io.exe"),
                        str(Path(root) / "Programs" / "draw.io" / "draw.io.exe"),
                    ]
                )
    elif sys.platform == "darwin":
        candidates.append("/Applications/draw.io.app/Contents/MacOS/draw.io")

    for candidate in candidates:
        if candidate and Path(candidate).expanduser().is_file():
            return str(Path(candidate).expanduser())
    return None


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Input .drawio file")
    parser.add_argument("--output", type=Path, help="Output file (default: source.pdf)")
    parser.add_argument("--format", default="pdf", help="Draw.io output format (default: pdf)")
    parser.add_argument("--drawio-bin", help="Explicit path to Draw.io executable")
    parser.add_argument("--no-crop", action="store_true", help="Disable Draw.io --crop")
    return parser.parse_args()


def main() -> int:
    """Validate inputs, locate Draw.io, and export the diagram."""
    args = parse_args()
    source = args.source.expanduser().resolve()
    if not source.is_file():
        print(f"ERROR: source file does not exist: {source}", file=sys.stderr)
        return 2

    executable = find_drawio(args.drawio_bin)
    if executable is None:
        print(
            "ERROR: Draw.io CLI was not found. Install Draw.io Desktop, add it to PATH, "
            "or pass --drawio-bin / set DRAWIO_BIN.",
            file=sys.stderr,
        )
        return 3

    output = (args.output or source.with_suffix(f".{args.format}")).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [executable, "--export", "--format", args.format]
    if not args.no_crop:
        command.append("--crop")
    command.extend(["--output", str(output), str(source)])

    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        print(f"ERROR: Draw.io exited with status {completed.returncode}.", file=sys.stderr)
        return completed.returncode
    if not output.is_file() or output.stat().st_size == 0:
        print(f"ERROR: export did not create a non-empty file: {output}", file=sys.stderr)
        return 4

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
