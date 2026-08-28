#!/usr/bin/env python3
"""Propagate stale validity through explicit Artifact Registry dependencies."""

from __future__ import annotations

from collections import deque
from typing import Any


def current_records(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for artifact_id, versions in registry.get("artifacts", {}).items():
        if versions:
            records[artifact_id] = max(versions, key=lambda item: item["version"])
    return records


def propagate_stale(
    registry: dict[str, Any], changed_ids: list[str] | set[str]
) -> list[str]:
    """Mark changed artifacts and all current dependents stale."""
    records = current_records(registry)
    reverse: dict[str, set[str]] = {}
    for artifact_id, record in records.items():
        for dependency in record.get("dependencies", []):
            reverse.setdefault(dependency["artifact_id"], set()).add(artifact_id)

    queue = deque(changed_ids)
    affected: list[str] = []
    seen: set[str] = set()
    while queue:
        artifact_id = queue.popleft()
        if artifact_id in seen:
            continue
        seen.add(artifact_id)
        record = records.get(artifact_id)
        if record is not None:
            record["validity"] = "stale"
            affected.append(artifact_id)
        queue.extend(sorted(reverse.get(artifact_id, set())))
    return affected
