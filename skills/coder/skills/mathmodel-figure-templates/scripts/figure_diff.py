#!/usr/bin/env python3
"""Compare two rendered figures globally and by a 3x3 region grid."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def compare(reference: Path, candidate: Path, output: Path | None) -> dict:
    try:
        import numpy as np
        from PIL import Image, ImageChops
    except ImportError as error:
        raise RuntimeError("figure diff requires numpy and Pillow") from error

    ref = Image.open(reference).convert("RGB")
    cand = Image.open(candidate).convert("RGB").resize(ref.size)
    ref_array = np.asarray(ref, dtype=np.float32) / 255.0
    cand_array = np.asarray(cand, dtype=np.float32) / 255.0
    try:
        from skimage.metrics import structural_similarity
        global_score = float(structural_similarity(ref_array, cand_array, channel_axis=2, data_range=1.0))
    except ImportError:
        global_score = float(1.0 - np.mean(np.abs(ref_array - cand_array)))
    width, height = ref.size
    grid = []
    for row in range(3):
        row_scores = []
        for column in range(3):
            x0, x1 = column * width // 3, (column + 1) * width // 3
            y0, y1 = row * height // 3, (row + 1) * height // 3
            delta = np.abs(ref_array[y0:y1, x0:x1] - cand_array[y0:y1, x0:x1])
            row_scores.append(float(1.0 - np.mean(delta)))
        grid.append(row_scores)
    if output:
        diff = ImageChops.difference(ref, cand)
        diff.save(output)
    return {"reference": str(reference), "candidate": str(candidate), "score": global_score,
            "region_similarity": grid, "diff": str(output) if output else None,
            "note": "Similarity localizes visual change; it does not validate scientific correctness."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference")
    parser.add_argument("candidate")
    parser.add_argument("--output")
    args = parser.parse_args()
    reference, candidate = Path(args.reference), Path(args.candidate)
    if not reference.is_file() or not candidate.is_file():
        print("ERROR: both image paths must exist", file=sys.stderr)
        return 2
    try:
        result = compare(reference, candidate, Path(args.output) if args.output else None)
    except RuntimeError as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        return 3
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
