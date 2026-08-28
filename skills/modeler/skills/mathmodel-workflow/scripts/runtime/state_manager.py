#!/usr/bin/env python3
"""Crash-safe workflow state management using only the Python standard library."""

from __future__ import annotations

from contextlib import AbstractContextManager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import time
from typing import Any
from uuid import uuid4


GATE_IDS = (
    "G0_ENVIRONMENT_READY",
    "G1_PROBLEM_PARSED",
    "G2_METHOD_VALIDATED",
    "G3_IMPLEMENTATION_VERIFIED",
    "G4_RESULTS_FROZEN",
    "G5_PAPER_EVIDENCE_COMPLETE",
    "G6_DELIVERY_VERIFIED",
)
GATE_STATUSES = {"not_started", "pass", "fail", "blocked"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class LockTimeoutError(TimeoutError):
    """Raised when a state file remains locked beyond the allowed timeout."""


class FileLock(AbstractContextManager["FileLock"]):
    """Small cross-platform exclusive lock implemented with atomic file creation."""

    def __init__(self, target: Path, timeout: float = 5.0, poll: float = 0.05):
        self.path = Path(f"{target}.lock")
        self.timeout = timeout
        self.poll = poll
        self._acquired = False

    def __enter__(self) -> "FileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.timeout
        payload = f"pid={os.getpid()} acquired_at={utc_now()}\n".encode("utf-8")
        while True:
            try:
                descriptor = os.open(
                    self.path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                )
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())
                self._acquired = True
                return self
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise LockTimeoutError(f"timed out waiting for lock: {self.path}")
                time.sleep(self.poll)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._acquired:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass
            self._acquired = False


def atomic_write_json(path: Path, data: Any) -> None:
    """Write a complete UTF-8 JSON document and atomically replace the target."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(target):
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(data, stream, ensure_ascii=False, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, target)
        finally:
            if temporary.exists():
                temporary.unlink()


def load_json(path: Path, default: Any | None = None) -> Any:
    target = Path(path)
    if not target.is_file():
        if default is not None:
            return default
        raise FileNotFoundError(target)
    with target.open("r", encoding="utf-8-sig") as stream:
        return json.load(stream)


def _state_path(project_root: Path) -> Path:
    return Path(project_root) / "state" / "workflow_state.json"


def _history_path(project_root: Path) -> Path:
    return Path(project_root) / "state" / "gate_history.jsonl"


def initialize_workflow(project_root: Path, *, force: bool = False) -> dict[str, Any]:
    root = Path(project_root).resolve()
    target = _state_path(root)
    if target.is_file() and not force:
        return load_workflow_state(root)
    now = utc_now()
    state = {
        "schema_version": "1.0",
        "current_gate": GATE_IDS[0],
        "status": "active",
        "gates": {gate: "not_started" for gate in GATE_IDS},
        "blocking_reasons": [],
        "waivers": [],
        "transaction_id": str(uuid4()),
        "updated_at": now,
    }
    atomic_write_json(target, state)
    return state


def load_workflow_state(project_root: Path) -> dict[str, Any]:
    state = load_json(_state_path(Path(project_root)))
    if state.get("schema_version") != "1.0":
        raise ValueError("unsupported workflow state schema_version")
    if tuple(state.get("gates", {}).keys()) != GATE_IDS:
        raise ValueError("workflow state has missing or out-of-order gates")
    return state


def _append_history(project_root: Path, record: dict[str, Any]) -> None:
    target = _history_path(Path(project_root))
    target.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
    with FileLock(target):
        with target.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(line)
            stream.flush()
            os.fsync(stream.fileno())


def update_gate(
    project_root: Path,
    gate_id: str,
    status: str,
    *,
    actor: str,
    reasons: list[str] | None = None,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    if gate_id not in GATE_IDS:
        raise ValueError(f"unknown gate: {gate_id}")
    if status not in GATE_STATUSES:
        raise ValueError(f"invalid gate status: {status}")
    if not actor.strip():
        raise ValueError("actor is required")

    root = Path(project_root).resolve()
    state_path = _state_path(root)
    state = initialize_workflow(root) if not state_path.is_file() else load_workflow_state(root)
    gate_index = GATE_IDS.index(gate_id)
    if status == "pass" and gate_index:
        previous = GATE_IDS[gate_index - 1]
        if state["gates"][previous] != "pass":
            raise ValueError(f"cannot pass {gate_id} before {previous}")

    now = utc_now()
    transaction_id = str(uuid4())
    state["gates"][gate_id] = status
    state["current_gate"] = gate_id
    state["blocking_reasons"] = list(reasons or []) if status in {"blocked", "fail"} else []
    state["status"] = "blocked" if status in {"blocked", "fail"} else "active"
    if gate_id == GATE_IDS[-1] and status == "pass":
        state["status"] = "complete"
    state["transaction_id"] = transaction_id
    state["updated_at"] = now
    atomic_write_json(state_path, state)
    _append_history(
        root,
        {
            "schema_version": "1.0",
            "gate_id": gate_id,
            "status": status,
            "actor": actor,
            "reasons": list(reasons or []),
            "evidence": list(evidence or []),
            "transaction_id": transaction_id,
            "checked_at": now,
        },
    )
    return state


def next_actionable_gate(project_root: Path) -> str | None:
    state = load_workflow_state(Path(project_root))
    for gate_id in GATE_IDS:
        if state["gates"][gate_id] != "pass":
            return gate_id
    return None
