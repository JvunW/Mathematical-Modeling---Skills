#!/usr/bin/env python3
"""Compare protected mathematical-paper tokens before and after prose editing."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
from typing import Callable


NUMBER_PATTERN = r"(?<![\w])[-+−]?(?:\d+(?:[.,]\d+)*|\.\d+)(?:[eE][-+]?\d+)?(?:[%％])?"
UNIT_PATTERN = (
    r"(?:%|％|mm|cm|dm|km|m|μm|nm|kg|mg|g|s|min|h|Hz|kHz|MHz|GHz|"
    r"Pa|kPa|MPa|W|kW|MW|V|mV|A|mA|K|°C|℃|mol|L|mL|个|次|组|条|"
    r"年|月|日|小时|分钟|秒|米|千米|克|千克|摄氏度)"
)


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def find(pattern: str, text: str, *, flags: int = 0, normalize: bool = False) -> list[str]:
    values = [match.group(0) for match in re.finditer(pattern, text, flags)]
    return [normalize_space(value) for value in values] if normalize else values


def extract_math(text: str) -> list[str]:
    environments = find(
        r"\\begin\{(?:equation\*?|align\*?|aligned|gather\*?|multline\*?|cases)\}.*?"
        r"\\end\{(?:equation\*?|align\*?|aligned|gather\*?|multline\*?|cases)\}",
        text,
        flags=re.DOTALL,
        normalize=True,
    )
    display = find(r"\$\$.*?\$\$", text, flags=re.DOTALL, normalize=True)
    inline = find(r"(?<!\$)\$(?!\$).*?(?<!\$)\$(?!\$)", text, flags=re.DOTALL, normalize=True)
    return environments + display + inline


def extract_code(text: str) -> list[str]:
    fenced = find(r"```.*?```", text, flags=re.DOTALL)
    latex = find(
        r"\\begin\{(?:lstlisting|verbatim|minted)\}.*?\\end\{(?:lstlisting|verbatim|minted)\}",
        text,
        flags=re.DOTALL,
    )
    return fenced + latex


EXTRACTORS: dict[str, Callable[[str], list[str]]] = {
    "numbers": lambda text: find(NUMBER_PATTERN, text),
    "measurements": lambda text: find(
        rf"{NUMBER_PATTERN}\s*{UNIT_PATTERN}(?![A-Za-z])", text
    ),
    "math": extract_math,
    "citations": lambda text: find(
        r"\\(?:cite|citep|citet|parencite|textcite)[A-Za-z*]*\{[^{}]+\}|"
        r"\[@[^\]]+\]|(?<!\w)\[(?:\d+(?:\s*[-,，]\s*\d+)*)\]",
        text,
        normalize=True,
    ),
    "references": lambda text: find(
        r"\\(?:label|ref|eqref|autoref|pageref)\{[^{}]+\}|"
        r"(?<![\w])@[A-Za-z][\w:.-]*|<[A-Za-z][\w:.-]*>",
        text,
    ),
    "images": lambda text: find(
        r"!\[[^\]]*\]\([^)]+\)|"
        r"\\includegraphics(?:\[[^\]]*\])?\{[^{}]+\}|"
        r"#?image\([^)]*\)",
        text,
        normalize=True,
    ),
    "latex_commands": lambda text: find(r"\\[A-Za-z@]+\*?", text),
    "code": extract_code,
}


def compare(before_text: str, after_text: str) -> dict:
    differences: list[dict] = []
    checks: dict[str, dict[str, int]] = {}
    for category, extractor in EXTRACTORS.items():
        before = Counter(extractor(before_text))
        after = Counter(extractor(after_text))
        checks[category] = {"before": sum(before.values()), "after": sum(after.values())}
        removed = sorted((before - after).elements())
        added = sorted((after - before).elements())
        if removed or added:
            differences.append(
                {
                    "category": category,
                    "removed": removed,
                    "added": added,
                }
            )
    return {
        "schema_version": "1.0",
        "status": "fail" if differences else "pass",
        "checks": checks,
        "differences": differences,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, help="source file before language editing")
    parser.add_argument("after", type=Path, help="source file after language editing")
    parser.add_argument("--json", type=Path, help="optional JSON report path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        before_text = args.before.read_text(encoding="utf-8-sig")
        after_text = args.after.read_text(encoding="utf-8-sig")
        report = compare(before_text, after_text)
        report["before"] = str(args.before)
        report["after"] = str(args.after)
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0 if report["status"] == "pass" else 1
    except (OSError, UnicodeError) as error:
        print(f"protected-content check error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
