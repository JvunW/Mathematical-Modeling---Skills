#!/usr/bin/env python3
"""Aggregate evaluator-authored end-to-end scores and enforce release gates."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from statistics import fmean, pstdev
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent
RUBRIC_PATH = ROOT / "rubrics" / "end_to_end_rubric.json"
EXPECTED_CASES = {
    "regression_prediction",
    "classification_imbalance",
    "time_series",
    "operations_research",
    "multi_criteria_decision",
    "ode_mechanistic",
    "ambiguous_missing_data",
    "official_word_template",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="evaluator score JSON")
    parser.add_argument("--output", required=True, type=Path, help="aggregated report JSON")
    parser.add_argument("--rubric", type=Path, default=RUBRIC_PATH)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def validate_and_score_runs(
    payload: dict[str, Any], rubric: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    dimensions = {item["id"]: item for item in rubric["dimensions"]}
    if sum(item["max_score"] for item in dimensions.values()) != rubric["total_score"]:
        raise ValueError("rubric dimension scores do not sum to total_score")
    runs = payload.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("input must contain a non-empty runs list")

    thresholds = rubric["thresholds"]
    scored: list[dict[str, Any]] = []
    by_case: dict[str, list[dict[str, Any]]] = {}
    seen_run_ids: set[str] = set()
    for index, raw in enumerate(runs):
        if not isinstance(raw, dict):
            raise ValueError(f"run {index} is not an object")
        case_id = str(raw.get("case_id", ""))
        run_id = str(raw.get("run_id", ""))
        if case_id not in EXPECTED_CASES:
            raise ValueError(f"unknown case_id: {case_id}")
        if not run_id or run_id in seen_run_ids:
            raise ValueError(f"missing or duplicate run_id: {run_id}")
        seen_run_ids.add(run_id)
        scores = raw.get("scores")
        if not isinstance(scores, dict) or set(scores) != set(dimensions):
            raise ValueError(f"run {run_id} must score every rubric dimension exactly once")
        normalized: dict[str, float] = {}
        for dimension_id, definition in dimensions.items():
            value = scores[dimension_id]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"run {run_id} has non-numeric score: {dimension_id}")
            value = float(value)
            if not 0 <= value <= float(definition["max_score"]):
                raise ValueError(f"run {run_id} score out of range: {dimension_id}")
            normalized[dimension_id] = value
        fatal_errors = raw.get("fatal_errors", [])
        if not isinstance(fatal_errors, list):
            raise ValueError(f"run {run_id} fatal_errors must be a list")
        core_ok = all(
            normalized[dimension_id] >= definition["max_score"] * thresholds["run_core_fraction"]
            for dimension_id, definition in dimensions.items()
            if definition.get("core")
        )
        item = {
            "case_id": case_id,
            "run_id": run_id,
            "scores": normalized,
            "total_score": sum(normalized.values()),
            "fatal_errors": [str(error) for error in fatal_errors],
            "runtime_seconds": float(raw.get("runtime_seconds", 0)),
            "token_cost_estimate": raw.get("token_cost_estimate"),
        }
        item["passed"] = (
            not item["fatal_errors"]
            and item["total_score"] >= thresholds["run_pass_score"]
            and core_ok
        )
        scored.append(item)
        by_case.setdefault(case_id, []).append(item)

    summaries: dict[str, dict[str, Any]] = {}
    for case_id, items in sorted(by_case.items()):
        totals = [item["total_score"] for item in items]
        summaries[case_id] = {
            "runs": len(items),
            "mean_score": fmean(totals),
            "score_std": pstdev(totals) if len(totals) > 1 else 0.0,
            "pass_rate": fmean(1.0 if item["passed"] else 0.0 for item in items),
            "fatal_error_rate": fmean(1.0 if item["fatal_errors"] else 0.0 for item in items),
            "mean_runtime_seconds": fmean(item["runtime_seconds"] for item in items),
            "dimension_means": {
                dimension_id: fmean(item["scores"][dimension_id] for item in items)
                for dimension_id in dimensions
            },
        }
    return scored, summaries


def reliability_gate(payload: dict[str, Any]) -> dict[str, Any]:
    values = payload.get("reliability")
    thresholds = {
        "fatal_fabrication_rate": ("max", 0.0),
        "stale_propagation_pass_rate": ("min", 1.0),
        "blocked_state_correctness": ("min", 0.95),
        "resume_from_state_success": ("min", 0.95),
    }
    if not isinstance(values, dict):
        return {"passed": False, "status": "not_run", "checks": {}}
    checks: dict[str, dict[str, Any]] = {}
    for name, (operator, threshold) in thresholds.items():
        raw = values.get(name)
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            passed = False
            value = None
        else:
            value = float(raw)
            passed = value <= threshold if operator == "max" else value >= threshold
        checks[name] = {"value": value, "operator": operator, "threshold": threshold, "passed": passed}
    return {
        "passed": all(check["passed"] for check in checks.values()),
        "status": "complete",
        "checks": checks,
    }


def build_report(payload: dict[str, Any], rubric: dict[str, Any]) -> dict[str, Any]:
    scored, cases = validate_and_score_runs(payload, rubric)
    thresholds = rubric["thresholds"]
    reliability = reliability_gate(payload)
    all_cases_present = set(cases) == EXPECTED_CASES
    repeats_complete = all(
        cases.get(case_id, {}).get("runs", 0) >= thresholds["required_repeats_per_case"]
        for case_id in EXPECTED_CASES
    )
    case_passes = sum(
        summary["mean_score"] >= 85
        and summary["pass_rate"] >= 2 / 3
        and summary["fatal_error_rate"] == 0
        for summary in cases.values()
    )
    overall_mean = fmean(item["total_score"] for item in scored)
    dimensions = {item["id"]: item for item in rubric["dimensions"]}
    core_fractions = {
        dimension_id: fmean(item["scores"][dimension_id] for item in scored) / definition["max_score"]
        for dimension_id, definition in dimensions.items()
        if definition.get("core")
    }
    no_fatal_errors = all(not item["fatal_errors"] for item in scored)
    release_eligible = (
        all_cases_present
        and case_passes >= thresholds["release_case_passes"]
        and no_fatal_errors
        and reliability["passed"]
    )
    claim_9_5_eligible = (
        all_cases_present
        and repeats_complete
        and no_fatal_errors
        and case_passes >= thresholds["nine_point_five_case_scores_at_least_85"]
        and overall_mean >= thresholds["nine_point_five_mean_score"]
        and all(
            fraction >= thresholds["nine_point_five_core_fraction"]
            for fraction in core_fractions.values()
        )
        and reliability["passed"]
    )
    return {
        "schema_version": "1.0",
        "status": "pass" if release_eligible else "fail",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rubric": str(RUBRIC_PATH.relative_to(ROOT.parent)).replace("\\", "/"),
        "summary": {
            "run_count": len(scored),
            "case_count": len(cases),
            "case_passes": case_passes,
            "overall_mean_score": overall_mean,
            "all_cases_present": all_cases_present,
            "required_repeats_complete": repeats_complete,
            "no_fatal_errors": no_fatal_errors,
            "core_dimension_fractions": core_fractions,
        },
        "release_eligible": release_eligible,
        "claim_9_0_eligible": release_eligible and case_passes >= thresholds["nine_point_zero_case_passes"],
        "claim_9_5_eligible": claim_9_5_eligible,
        "reliability_gate": reliability,
        "cases": cases,
        "runs": scored,
    }


def main() -> int:
    args = parse_args()
    try:
        rubric = load_json(args.rubric)
        payload = load_json(args.input)
        report = build_report(payload, rubric)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"evaluation input error: {error}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(args.output)}, ensure_ascii=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
