#!/usr/bin/env python3
"""Inspect MathModel Skills runtime dependencies without changing the system."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
import platform
import shutil
import sys


COMMANDS = {
    "typst": ("typst",),
    "xelatex": ("xelatex",),
    "drawio": ("drawio", "draw.io", "draw.io.exe", "drawio.exe"),
    "pdftoppm": ("pdftoppm",),
    "mutool": ("mutool",),
    "magick": ("magick",),
}

PACKAGES = {
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "scipy": "scipy",
    "sklearn": "scikit-learn",
    "openpyxl": "openpyxl",
    "seaborn": "seaborn",
    "pingouin": "pingouin",
    "statsmodels": "statsmodels",
    "pint": "pint",
    "uncertainties": "uncertainties",
    "requests": "requests",
}

CORE_PACKAGES = {"numpy", "pandas", "matplotlib"}


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero when core requirements are missing")
    return parser.parse_args()


def inspect_commands() -> dict[str, dict[str, str | bool | None]]:
    """Locate supported external commands."""
    result: dict[str, dict[str, str | bool | None]] = {}
    for label, candidates in COMMANDS.items():
        path = next((found for name in candidates if (found := shutil.which(name))), None)
        result[label] = {"installed": path is not None, "path": path}
    return result


def inspect_packages() -> dict[str, dict[str, str | bool | None]]:
    """Detect Python modules without importing third-party code."""
    result: dict[str, dict[str, str | bool | None]] = {}
    for module, distribution in PACKAGES.items():
        installed = importlib.util.find_spec(module) is not None
        version = None
        if installed:
            try:
                version = importlib.metadata.version(distribution)
            except importlib.metadata.PackageNotFoundError:
                version = "unknown"
        result[module] = {"installed": installed, "version": version}
    return result


def build_report() -> dict:
    """Build a serializable environment report."""
    commands = inspect_commands()
    packages = inspect_packages()
    python_ok = sys.version_info >= (3, 11)
    compiler_ok = bool(commands["typst"]["installed"] or commands["xelatex"]["installed"])
    core_packages_ok = all(packages[name]["installed"] for name in CORE_PACKAGES)
    rasterizer_ok = any(commands[name]["installed"] for name in ("pdftoppm", "mutool", "magick"))
    openalex_key_configured = bool(os.environ.get("OPENALEX_API_KEY", "").strip())
    return {
        "platform": platform.platform(),
        "python": {"version": platform.python_version(), "executable": sys.executable, "supported": python_ok},
        "commands": commands,
        "packages": packages,
        "credentials": {"openalex_api_key_configured": openalex_key_configured},
        "capabilities": {
            "analysis": True,
            "numerical_modeling": python_ok and core_packages_ok,
            "paper_compilation": compiler_ok,
            "drawio_pdf_export": bool(commands["drawio"]["installed"]),
            "pdf_visual_rendering": rasterizer_ok,
            "openalex_api_access": python_ok and openalex_key_configured,
        },
        "core_ready": python_ok and core_packages_ok and compiler_ok,
    }


def print_text(report: dict) -> None:
    """Print a compact human-readable report."""
    python_info = report["python"]
    print(f"Platform: {report['platform']}")
    print(f"Python:   {python_info['version']} ({python_info['executable']})")
    print("\nCommands")
    for name, item in report["commands"].items():
        status = "OK" if item["installed"] else "MISS"
        detail = f" - {item['path']}" if item["path"] else ""
        print(f"  {status:4} {name}{detail}")
    print("\nPython packages")
    for name, item in report["packages"].items():
        status = "OK" if item["installed"] else "MISS"
        detail = f" {item['version']}" if item["version"] else ""
        print(f"  {status:4} {name}{detail}")
    print("\nCredentials")
    openalex_status = "SET" if report["credentials"]["openalex_api_key_configured"] else "MISS"
    print(f"  {openalex_status:4} OPENALEX_API_KEY (value never displayed)")
    print("\nCapabilities")
    for name, available in report["capabilities"].items():
        print(f"  {'YES' if available else 'NO ':3} {name}")
    print(f"\nCore workflow ready: {'YES' if report['core_ready'] else 'NO'}")


def main() -> int:
    """Inspect and report, optionally failing in strict mode."""
    args = parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report)
    return 1 if args.strict and not report["core_ready"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
