#!/usr/bin/env python3
"""Validate the complete Mathematical-Modeling---Skills repository."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILL_FILE = re.compile(r"^---\n(?P<frontmatter>.*?)\n---\n", re.DOTALL)
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")
FORBIDDEN_REFERENCES = ("superpowers:", "statistical-power", "parallel-cli")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="run portable checks")
    mode.add_argument("--full", action="store_true", help="also inspect optional toolchains")
    parser.add_argument("--skip-tests", action="store_true", help="skip executable tests")
    parser.add_argument("--json", type=Path, help="write a machine-readable report")
    return parser.parse_args()


def record(checks: list[dict[str, Any]], name: str, errors: list[str], *, details=None) -> None:
    checks.append(
        {
            "name": name,
            "status": "fail" if errors else "pass",
            "errors": errors,
            "details": details or {},
        }
    )


def discover_skills() -> list[Path]:
    return sorted(ROOT.glob("skills/*/skills/*/SKILL.md"))


def check_skill_structure(checks: list[dict[str, Any]], skills: list[Path]) -> None:
    errors: list[str] = []
    names: set[str] = set()
    for skill_file in skills:
        text = skill_file.read_text(encoding="utf-8-sig")
        match = SKILL_FILE.match(text)
        if not match:
            errors.append(f"missing YAML frontmatter: {skill_file.relative_to(ROOT)}")
            continue
        frontmatter = match.group("frontmatter")
        name_match = re.search(r"(?m)^name:\s*[\"']?([^\"'\n]+)", frontmatter)
        description_match = re.search(r"(?m)^description:\s*(.+)$", frontmatter)
        expected = skill_file.parent.name
        if not name_match or name_match.group(1).strip() != expected:
            errors.append(f"name mismatch: {skill_file.relative_to(ROOT)}")
        elif expected in names:
            errors.append(f"duplicate skill name: {expected}")
        else:
            names.add(expected)
        if not description_match or len(description_match.group(1).strip(" \"'")) < 20:
            errors.append(f"missing or weak description: {skill_file.relative_to(ROOT)}")
        metadata = skill_file.parent / "agents" / "openai.yaml"
        if not metadata.is_file():
            errors.append(f"missing agents/openai.yaml: {skill_file.parent.relative_to(ROOT)}")
        else:
            metadata_text = metadata.read_text(encoding="utf-8-sig")
            for field in ("display_name:", "short_description:", "default_prompt:"):
                if field not in metadata_text:
                    errors.append(f"missing {field} in {metadata.relative_to(ROOT)}")
    if len(skills) != 22:
        errors.append(f"expected 22 skills, found {len(skills)}")
    record(checks, "skill_structure", errors, details={"count": len(skills)})


def check_plugins(checks: list[dict[str, Any]], skills: list[Path]) -> int:
    errors: list[str] = []
    manifests = sorted(ROOT.glob("skills/*/.codex-plugin/plugin.json"))
    counts: dict[str, int] = {}
    for skill in skills:
        role = skill.parents[2].name
        counts[role] = counts.get(role, 0) + 1
    for manifest in manifests:
        role = manifest.parents[1].name
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid JSON {manifest.relative_to(ROOT)}: {error}")
            continue
        if data.get("name") != role:
            errors.append(f"plugin name mismatch: {manifest.relative_to(ROOT)}")
        if data.get("skills") != "./skills/":
            errors.append(f"plugin skill path mismatch: {manifest.relative_to(ROOT)}")
        if not re.fullmatch(r"2\.0\.0(?:\+codex\..+)?", str(data.get("version", ""))):
            errors.append(f"unexpected plugin version: {manifest.relative_to(ROOT)}")
        if counts.get(role, 0) == 0:
            errors.append(f"plugin has no discovered skills: {role}")
    if len(manifests) != 3:
        errors.append(f"expected 3 plugin manifests, found {len(manifests)}")
    record(checks, "plugin_manifests", errors, details={"count": len(manifests)})
    return len(manifests)


def check_references_and_links(checks: list[dict[str, Any]], skills: list[Path]) -> None:
    errors: list[str] = []
    markdown_files = [ROOT / "README.md", *skills]
    markdown_files.extend(sorted(ROOT.glob("skills/*/ROLE.md")))
    for source in markdown_files:
        text = source.read_text(encoding="utf-8-sig")
        for token in FORBIDDEN_REFERENCES:
            if token in text:
                errors.append(f"legacy reference {token}: {source.relative_to(ROOT)}")
        link_text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for raw_target in MARKDOWN_LINK.findall(link_text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or re.match(r"^(?:https?://|mailto:|codex:)", target):
                continue
            target = target.strip("<>")
            if not (source.parent / target).resolve().exists():
                errors.append(f"broken link {raw_target}: {source.relative_to(ROOT)}")
    record(checks, "references_and_links", errors)


def check_json_contracts(checks: list[dict[str, Any]]) -> None:
    errors: list[str] = []
    expected = {
        "model_manifest.schema.json",
        "results_manifest.schema.json",
        "paper_evidence_map.schema.json",
        "verification_report.schema.json",
    }
    found = {path.name for path in (ROOT / "schemas").glob("*.schema.json")}
    if found != expected:
        errors.append(f"schema set mismatch: {sorted(found)}")
    for source in sorted((ROOT / "schemas").glob("*.json")) + [ROOT / "RELEASE_MANIFEST.json"]:
        try:
            json.loads(source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid JSON {source.relative_to(ROOT)}: {error}")
    record(checks, "json_contracts", errors, details={"count": len(found)})


def check_python_syntax(checks: list[dict[str, Any]]) -> int:
    errors: list[str] = []
    sources = sorted(
        path
        for path in ROOT.rglob("*.py")
        if ".git" not in path.parts and "__pycache__" not in path.parts
    )
    for source in sources:
        try:
            compile(source.read_text(encoding="utf-8-sig"), str(source), "exec")
        except (OSError, SyntaxError, UnicodeError) as error:
            errors.append(f"{source.relative_to(ROOT)}: {error}")
    record(checks, "python_syntax", errors, details={"count": len(sources)})
    return len(sources)


def run_command(command: list[str]) -> tuple[int, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        env=env,
    )
    return completed.returncode, completed.stdout + completed.stderr


def print_console_safe(text: str) -> None:
    """Print without letting a legacy Windows console codec abort validation."""

    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    safe_text = text.encode(encoding, errors="backslashreplace").decode(encoding)
    print(safe_text)


def check_tests(checks: list[dict[str, Any]]) -> None:
    errors: list[str] = []
    commands = [[sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]]
    commands.extend(
        [sys.executable, str(test.relative_to(ROOT))]
        for test in sorted(ROOT.glob("skills/*/skills/*/tests/test_*.py"))
    )
    outputs: list[str] = []
    for command in commands:
        code, output = run_command(command)
        outputs.append(output[-4000:])
        if code:
            errors.append(f"command failed ({code}): {' '.join(command)}\n{output[-2000:]}")
    record(checks, "tests", errors, details={"commands": len(commands), "outputs": outputs})


def check_optional_toolchains(checks: list[dict[str, Any]]) -> None:
    tools = {name: shutil.which(name) for name in ("pandoc", "typst", "xelatex")}
    checks.append(
        {
            "name": "optional_toolchains",
            "status": "pass",
            "errors": [],
            "details": {
                name: {"status": "available" if path else "skipped", "path": path}
                for name, path in tools.items()
            },
        }
    )


def main() -> int:
    args = parse_args()
    checks: list[dict[str, Any]] = []
    skills = discover_skills()
    check_skill_structure(checks, skills)
    plugin_count = check_plugins(checks, skills)
    check_references_and_links(checks, skills)
    check_json_contracts(checks)
    python_count = check_python_syntax(checks)
    if not args.skip_tests:
        check_tests(checks)
    if args.full:
        check_optional_toolchains(checks)

    errors = [error for check in checks for error in check["errors"]]
    report = {
        "schema_version": "1.0",
        "status": "fail" if errors else "pass",
        "mode": "full" if args.full else "quick",
        "skill_count": len(skills),
        "plugin_count": plugin_count,
        "python_file_count": python_count,
        "checks": checks,
        "error_count": len(errors),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.json:
        output = args.json if args.json.is_absolute() else ROOT / args.json
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print_console_safe(rendered)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
