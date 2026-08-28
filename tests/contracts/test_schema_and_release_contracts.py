from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SchemaAndReleaseContracts(unittest.TestCase):
    def test_four_versioned_schemas_are_present(self) -> None:
        expected = {
            "model_manifest.schema.json",
            "results_manifest.schema.json",
            "paper_evidence_map.schema.json",
            "verification_report.schema.json",
        }
        actual = {path.name for path in (ROOT / "schemas").glob("*.schema.json")}
        self.assertEqual(actual, expected)
        for name in sorted(expected):
            schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertIn("schema_version", schema["properties"])
            self.assertIn("schema_version", schema["required"])
            self.assertFalse(schema.get("additionalProperties", True), name)

    def test_release_manifest_pins_plugins_schemas_and_evaluation(self) -> None:
        release = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(release["release"], "2.0.0")
        self.assertEqual(
            release["plugins"],
            {"modeler": "2.0.0", "coder": "2.0.0", "writer": "2.0.0"},
        )
        self.assertEqual(set(release["schemas"].values()), {"1.0"})
        self.assertIn("evaluation_baseline", release)
        self.assertIn("rollback_target", release)

    def test_evaluation_layout_separates_public_and_holdout_material(self) -> None:
        public = ROOT / "evals" / "public"
        cases = {path.name for path in public.iterdir() if path.is_dir()}
        self.assertEqual(
            cases,
            {
                "regression_prediction",
                "classification_imbalance",
                "time_series",
                "operations_research",
                "multi_criteria_decision",
                "ode_mechanistic",
                "ambiguous_missing_data",
                "official_word_template",
            },
        )
        holdout = (ROOT / "evals" / "HOLDOUT_POLICY.md").read_text(encoding="utf-8")
        self.assertIn("evaluator-only", holdout)
        self.assertIn("不得放入被评 Agent 的工作区", holdout)

    def test_end_to_end_rubric_and_runner_enforce_the_9_5_gate(self) -> None:
        rubric_path = ROOT / "evals" / "rubrics" / "end_to_end_rubric.json"
        rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
        dimensions = rubric["dimensions"]
        self.assertEqual(sum(item["max_score"] for item in dimensions), 100)
        self.assertEqual(len(dimensions), 7)

        case_ids = sorted(path.name for path in (ROOT / "evals" / "public").iterdir())
        perfect_scores = {item["id"]: item["max_score"] for item in dimensions}
        runs = [
            {
                "case_id": case_id,
                "run_id": f"{case_id}-{repeat}",
                "scores": perfect_scores,
                "fatal_errors": [],
                "runtime_seconds": 1.0,
            }
            for case_id in case_ids
            for repeat in range(1, 4)
        ]
        payload = {
            "schema_version": "1.0",
            "runs": runs,
            "reliability": {
                "fatal_fabrication_rate": 0,
                "stale_propagation_pass_rate": 1,
                "blocked_state_correctness": 1,
                "resume_from_state_success": 1,
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            input_path = Path(temporary) / "scores.json"
            output_path = Path(temporary) / "report.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "evals" / "run_evals.py"),
                    "--input",
                    str(input_path),
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            report = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertTrue(report["claim_9_5_eligible"])
        self.assertTrue(report["reliability_gate"]["passed"])
        self.assertEqual(report["summary"]["case_count"], 8)


if __name__ == "__main__":
    unittest.main()
