#!/usr/bin/env python3
"""Manage recoverable mathematical-modeling workflow state and artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from runtime.artifact_registry import ArtifactRegistry
from runtime.gate_runner import run_gate
from runtime.state_manager import initialize_workflow, next_actionable_gate, update_gate


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="initialize workflow state")
    init.add_argument("project_root", type=Path)

    register = commands.add_parser("register", help="register a file artifact")
    register.add_argument("project_root", type=Path)
    register.add_argument("artifact_id")
    register.add_argument("path", type=Path)
    register.add_argument("artifact_type")
    register.add_argument("--required", action="store_true")
    register.add_argument("--producer")

    freeze = commands.add_parser("freeze", help="freeze a registered artifact")
    freeze.add_argument("project_root", type=Path)
    freeze.add_argument("artifact_id")
    for name in ("code", "data", "config", "environment"):
        freeze.add_argument(f"--{name}-hash", required=True)
    freeze.add_argument("--randomness-policy", required=True)

    refresh = commands.add_parser("refresh", help="refresh hashes and propagate stale state")
    refresh.add_argument("project_root", type=Path)

    gate = commands.add_parser("gate", help="run a deterministic workflow gate")
    gate.add_argument("project_root", type=Path)
    gate.add_argument("gate_id")
    gate.add_argument("--actor", default="workflow_runtime_cli")

    update = commands.add_parser("update-gate", help="record externally verified gate evidence")
    update.add_argument("project_root", type=Path)
    update.add_argument("gate_id")
    update.add_argument("status", choices=("not_started", "pass", "fail", "blocked"))
    update.add_argument("--actor", required=True)
    update.add_argument("--reason", action="append", default=[])
    update.add_argument("--evidence", action="append", default=[])

    resume = commands.add_parser("next", help="print the first gate requiring work")
    resume.add_argument("project_root", type=Path)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    result: Any
    if args.command == "init":
        result = initialize_workflow(args.project_root)
    elif args.command == "register":
        result = ArtifactRegistry(args.project_root).register(
            args.artifact_id,
            args.path,
            args.artifact_type,
            required=args.required,
            producer=args.producer,
        )
    elif args.command == "freeze":
        result = ArtifactRegistry(args.project_root).freeze(
            args.artifact_id,
            source_hashes={
                "code": args.code_hash,
                "data": args.data_hash,
                "config": args.config_hash,
                "environment": args.environment_hash,
            },
            randomness_policy=args.randomness_policy,
        )
    elif args.command == "refresh":
        result = {"stale_or_missing": ArtifactRegistry(args.project_root).refresh()}
    elif args.command == "gate":
        result = run_gate(args.project_root, args.gate_id, actor=args.actor)
    elif args.command == "update-gate":
        result = update_gate(
            args.project_root,
            args.gate_id,
            args.status,
            actor=args.actor,
            reasons=args.reason,
            evidence=args.evidence,
        )
    else:
        result = {"next_gate": next_actionable_gate(args.project_root)}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if isinstance(result, dict) and result.get("status") == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
