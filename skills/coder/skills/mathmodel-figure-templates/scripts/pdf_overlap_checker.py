#!/usr/bin/env python3
"""Detect obvious text and drawing overlaps in a rendered figure PDF."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys


@dataclass(frozen=True)
class Finding:
    level: str
    category: str
    page: int
    message: str
    bbox: tuple[float, float, float, float] | None = None


def intersection(a, b) -> tuple[float, float]:
    return min(a.x1, b.x1) - max(a.x0, b.x0), min(a.y1, b.y1) - max(a.y0, b.y0)


def analyze(pdf: Path) -> list[Finding]:
    try:
        import fitz
    except ImportError as error:
        raise RuntimeError("PyMuPDF is required for PDF geometry QA; install pymupdf") from error

    findings: list[Finding] = []
    document = fitz.open(pdf)
    for page_index, page in enumerate(document, start=1):
        words = page.get_text("words")
        word_boxes = [(fitz.Rect(item[:4]), item[4]) for item in words if item[4].strip()]
        for index, (first, first_text) in enumerate(word_boxes):
            for second, second_text in word_boxes[index + 1:]:
                ox, oy = intersection(first, second)
                if ox > 1.0 and oy > 1.0:
                    findings.append(
                        Finding("ERROR", "text-overlap", page_index,
                                f"{first_text!r} overlaps {second_text!r}", tuple(first | second))
                    )

        drawings = page.get_drawings()
        filled_rects = [item["rect"] for item in drawings if item.get("fill") is not None and item["rect"].get_area() > 16]
        for index, first in enumerate(filled_rects):
            for second in filled_rects[index + 1:]:
                ox, oy = intersection(first, second)
                if ox > 2 and oy > 2:
                    smaller = min(first.get_area(), second.get_area())
                    overlap_area = ox * oy
                    if overlap_area / max(smaller, 1) > 0.18 and not (first.contains(second) or second.contains(first)):
                        findings.append(
                            Finding("WARN", "node-overlap", page_index,
                                    "filled rectangles overlap; triage intended nesting versus collision", tuple(first | second))
                        )

        page_rect = page.rect
        for rect, text in word_boxes:
            if not page_rect.contains(rect):
                findings.append(Finding("ERROR", "text-overflow", page_index, f"{text!r} lies outside page", tuple(rect)))
    document.close()
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    path = Path(args.pdf)
    if not path.is_file():
        print(f"ERROR: {path} does not exist", file=sys.stderr)
        return 2
    try:
        findings = analyze(path)
    except RuntimeError as error:
        payload = {"status": "skipped", "reason": str(error), "path": str(path)}
        print(json.dumps(payload, indent=2) if args.json else f"SKIPPED: {error}")
        return 3
    payload = {"status": "fail" if any(item.level == "ERROR" for item in findings) else "warn" if findings else "pass",
               "path": str(path), "findings": [asdict(item) for item in findings]}
    print(json.dumps(payload, indent=2))
    if any(item.level == "ERROR" for item in findings):
        return 2
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
