from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RUNTIME = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "modeler"
    / "skills"
    / "mathmodel-workflow"
    / "scripts"
    / "runtime"
)
sys.path.insert(0, str(RUNTIME))


class RuntimeContracts(unittest.TestCase):
    def test_runtime_cli_initializes_a_portable_workspace(self) -> None:
        script = RUNTIME.parent / "workflow_runtime.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            completed = subprocess.run(
                [sys.executable, str(script), "init", str(root)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            state = json.loads(
                (root / "state" / "workflow_state.json").read_text(encoding="utf-8")
            )
            self.assertEqual(state["current_gate"], "G0_ENVIRONMENT_READY")

    def test_atomic_json_write_replaces_complete_document(self) -> None:
        from state_manager import atomic_write_json, load_json

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "state" / "workflow_state.json"
            atomic_write_json(target, {"schema_version": "1.0", "value": 1})
            atomic_write_json(target, {"schema_version": "1.0", "value": 2})
            self.assertEqual(load_json(target)["value"], 2)
            self.assertEqual(list(target.parent.glob("*.tmp")), [])

    def test_artifact_lifecycle_and_validity_are_orthogonal(self) -> None:
        from artifact_registry import ArtifactRegistry

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = root / "results.json"
            result.write_text('{"score": 1}', encoding="utf-8")
            registry = ArtifactRegistry(root)
            record = registry.register(
                "Q1.results.main",
                result,
                artifact_type="result",
                required=True,
            )
            frozen = registry.freeze(
                record["artifact_id"],
                source_hashes={
                    "code": "code-hash",
                    "data": "data-hash",
                    "config": "config-hash",
                    "environment": "environment-hash",
                },
                randomness_policy="deterministic",
            )
            self.assertEqual(frozen["lifecycle"], "frozen")
            self.assertEqual(frozen["validity"], "fresh")

    def test_upstream_change_propagates_stale_to_dependents(self) -> None:
        from artifact_registry import ArtifactRegistry

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "data.csv"
            result = root / "result.json"
            claim = root / "claim.md"
            data.write_text("x\n1\n", encoding="utf-8")
            result.write_text('{"score": 1}', encoding="utf-8")
            claim.write_text("score is 1", encoding="utf-8")
            registry = ArtifactRegistry(root)
            upstream = registry.register("DATA.cleaned", data, "data")
            middle = registry.register(
                "Q1.results.main",
                result,
                "result",
                dependencies=[{"artifact_id": "DATA.cleaned", "version": 1}],
            )
            registry.register(
                "CLAIM.Q1.001",
                claim,
                "claim",
                dependencies=[
                    {"artifact_id": "Q1.results.main", "version": middle["version"]}
                ],
            )
            data.write_text("x\n2\n", encoding="utf-8")

            changed = registry.refresh()

            self.assertIn("DATA.cleaned", changed)
            self.assertEqual(registry.get("DATA.cleaned")["validity"], "stale")
            self.assertEqual(registry.get("Q1.results.main")["validity"], "stale")
            self.assertEqual(registry.get("CLAIM.Q1.001")["validity"], "stale")
            self.assertEqual(upstream["artifact_id"], "DATA.cleaned")

    def test_results_gate_rejects_stale_and_accepts_frozen_fresh(self) -> None:
        from artifact_registry import ArtifactRegistry
        from gate_runner import run_gate
        from state_manager import initialize_workflow, load_workflow_state, update_gate

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initialize_workflow(root)
            for gate_id in (
                "G0_ENVIRONMENT_READY",
                "G1_PROBLEM_PARSED",
                "G2_METHOD_VALIDATED",
                "G3_IMPLEMENTATION_VERIFIED",
            ):
                update_gate(root, gate_id, "pass", actor="test")
            result = root / "result.json"
            result.write_text('{"score": 1}', encoding="utf-8")
            registry = ArtifactRegistry(root)
            registry.register("Q1.results.main", result, "result", required=True)

            blocked = run_gate(root, "G4_RESULTS_FROZEN")
            self.assertEqual(blocked["status"], "blocked")

            registry.freeze(
                "Q1.results.main",
                source_hashes={
                    "code": "c",
                    "data": "d",
                    "config": "p",
                    "environment": "e",
                },
                randomness_policy="seed=42",
            )
            passed = run_gate(root, "G4_RESULTS_FROZEN")
            self.assertEqual(passed["status"], "pass")
            state = load_workflow_state(root)
            self.assertEqual(passed["transaction_id"], state["transaction_id"])
            self.assertEqual(passed["checked_at"], state["updated_at"])

    def test_resume_selects_first_gate_not_passed(self) -> None:
        from state_manager import initialize_workflow, next_actionable_gate, update_gate

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initialize_workflow(root)
            update_gate(root, "G0_ENVIRONMENT_READY", "pass", actor="test")
            update_gate(root, "G1_PROBLEM_PARSED", "pass", actor="test")
            self.assertEqual(next_actionable_gate(root), "G2_METHOD_VALIDATED")


if __name__ == "__main__":
    unittest.main()
