#!/usr/bin/env python3
"""Execute deterministic workflow gates and persist structured evidence."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

try:
    from .artifact_registry import ArtifactRegistry
    from .state_manager import GATE_IDS, load_workflow_state, update_gate
except ImportError:
    from artifact_registry import ArtifactRegistry
    from state_manager import GATE_IDS, load_workflow_state, update_gate


def _results_frozen(project_root: Path) -> tuple[list[str], list[str], list[str]]:
    registry = ArtifactRegistry(project_root)
    registry.refresh()
    required = [
        record
        for record in registry.current().values()
        if record.get("required") and record.get("artifact_type") == "result"
    ]
    errors: list[str] = []
    evidence: list[str] = []
    if not required:
        errors.append("no required result artifacts are registered")
    for record in required:
        reference = f"{record['artifact_id']}@{record['version']}"
        if record["lifecycle"] != "frozen":
            errors.append(f"{reference} is not frozen")
        if record["validity"] != "fresh":
            errors.append(f"{reference} is {record['validity']}")
        if record["lifecycle"] == "frozen" and record["validity"] == "fresh":
            evidence.append(reference)
    return evidence, [], errors


VALIDATORS: dict[str, Callable[[Path], tuple[list[str], list[str], list[str]]]] = {
    "G4_RESULTS_FROZEN": _results_frozen,
}


def run_gate(project_root: Path, gate_id: str, *, actor: str = "gate_runner") -> dict[str, Any]:
    root = Path(project_root).resolve()
    if gate_id not in GATE_IDS:
        raise ValueError(f"unknown gate: {gate_id}")
    state = load_workflow_state(root)
    index = GATE_IDS.index(gate_id)
    errors: list[str] = []
    warnings: list[str] = []
    evidence: list[str] = []
    if index and state["gates"][GATE_IDS[index - 1]] != "pass":
        errors.append(f"previous gate has not passed: {GATE_IDS[index - 1]}")
    validator = VALIDATORS.get(gate_id)
    if validator is None:
        warnings.append("no deterministic validator registered; explicit evidence is required")
    else:
        found, validator_warnings, validator_errors = validator(root)
        evidence.extend(found)
        warnings.extend(validator_warnings)
        errors.extend(validator_errors)

    status = "blocked" if errors else "pass"
    updated_state = update_gate(
        root,
        gate_id,
        status,
        actor=actor,
        reasons=errors,
        evidence=evidence,
    )
    return {
        "schema_version": "1.0",
        "gate_id": gate_id,
        "status": status,
        "validator": "gate_runner:2.0",
        "actor": actor,
        "evidence": evidence,
        "warnings": warnings,
        "errors": errors,
        "transaction_id": updated_state["transaction_id"],
        "checked_at": updated_state["updated_at"],
    }
