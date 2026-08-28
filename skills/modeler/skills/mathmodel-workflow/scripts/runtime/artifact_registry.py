#!/usr/bin/env python3
"""Versioned Artifact Registry with content hashes and dependency invalidation."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Any

try:
    from .state_manager import atomic_write_json, load_json, utc_now
    from .stale_propagation import current_records, propagate_stale
except ImportError:  # Direct script/test import.
    from state_manager import atomic_write_json, load_json, utc_now
    from stale_propagation import current_records, propagate_stale


LIFECYCLES = {"draft", "frozen", "superseded"}
VALIDITIES = {"fresh", "stale", "missing", "blocked"}
REQUIRED_SOURCE_HASHES = {"code", "data", "config", "environment"}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class ArtifactRegistry:
    def __init__(self, project_root: Path):
        self.root = Path(project_root).resolve()
        self.path = self.root / "state" / "artifact_registry.json"
        self.data = load_json(
            self.path,
            default={"schema_version": "1.0", "artifacts": {}, "updated_at": utc_now()},
        )
        if self.data.get("schema_version") != "1.0":
            raise ValueError("unsupported artifact registry schema_version")

    def _save(self) -> None:
        self.data["updated_at"] = utc_now()
        atomic_write_json(self.path, self.data)

    def _stored_path(self, path: Path) -> tuple[str, bool]:
        resolved = Path(path).resolve()
        try:
            return resolved.relative_to(self.root).as_posix(), False
        except ValueError:
            return str(resolved), True

    def _resolved_path(self, record: dict[str, Any]) -> Path:
        path = Path(record["path"])
        return path if record.get("external") else self.root / path

    def register(
        self,
        artifact_id: str,
        path: Path,
        artifact_type: str,
        *,
        dependencies: list[dict[str, Any]] | None = None,
        required: bool = False,
        producer: str | None = None,
    ) -> dict[str, Any]:
        if not artifact_id or "@" in artifact_id:
            raise ValueError("artifact_id must be stable and must not contain a version suffix")
        source = Path(path).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        versions = self.data["artifacts"].setdefault(artifact_id, [])
        if versions:
            current = max(versions, key=lambda item: item["version"])
            current["lifecycle"] = "superseded"
            version = current["version"] + 1
            supersedes = f"{artifact_id}@{current['version']}"
        else:
            version = 1
            supersedes = None

        normalized_dependencies: list[dict[str, Any]] = []
        for dependency in dependencies or []:
            dependency_id = dependency["artifact_id"]
            dependency_record = self.get(dependency_id)
            normalized_dependencies.append(
                {
                    "artifact_id": dependency_id,
                    "version": dependency.get("version", dependency_record["version"]),
                    "content_hash": dependency.get(
                        "content_hash", dependency_record["content_hash"]
                    ),
                }
            )

        stored_path, external = self._stored_path(source)
        record = {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "version": version,
            "path": stored_path,
            "external": external,
            "content_hash": sha256_path(source),
            "lifecycle": "draft",
            "validity": "fresh",
            "required": bool(required),
            "producer": producer,
            "dependencies": normalized_dependencies,
            "created_at": utc_now(),
            "supersedes": supersedes,
        }
        versions.append(record)
        self._save()
        return deepcopy(record)

    def get(self, artifact_id: str, version: int | None = None) -> dict[str, Any]:
        versions = self.data.get("artifacts", {}).get(artifact_id)
        if not versions:
            raise KeyError(artifact_id)
        if version is None:
            return max(versions, key=lambda item: item["version"])
        for record in versions:
            if record["version"] == version:
                return record
        raise KeyError(f"{artifact_id}@{version}")

    def freeze(
        self,
        artifact_id: str,
        *,
        source_hashes: dict[str, str],
        randomness_policy: str,
    ) -> dict[str, Any]:
        missing = REQUIRED_SOURCE_HASHES - set(source_hashes)
        empty = sorted(key for key in REQUIRED_SOURCE_HASHES if not source_hashes.get(key))
        if missing or empty:
            fields = sorted(missing | set(empty))
            raise ValueError("missing source hashes: " + ", ".join(fields))
        if not randomness_policy.strip():
            raise ValueError("randomness_policy is required")
        record = self.get(artifact_id)
        path = self._resolved_path(record)
        if not path.is_file():
            record["validity"] = "missing"
            self._save()
            raise FileNotFoundError(path)
        current_hash = sha256_path(path)
        if current_hash != record["content_hash"]:
            propagate_stale(self.data, [artifact_id])
            self._save()
            raise ValueError(f"artifact changed after registration: {artifact_id}")
        record["lifecycle"] = "frozen"
        record["validity"] = "fresh"
        record["source_hashes"] = dict(source_hashes)
        record["randomness_policy"] = randomness_policy
        record["frozen_at"] = utc_now()
        self._save()
        return deepcopy(record)

    def refresh(self) -> list[str]:
        changed: list[str] = []
        for artifact_id, record in current_records(self.data).items():
            path = self._resolved_path(record)
            if not path.is_file():
                record["validity"] = "missing"
                changed.append(artifact_id)
            elif sha256_path(path) != record["content_hash"]:
                changed.append(artifact_id)
        if changed:
            affected = propagate_stale(self.data, changed)
            for artifact_id in changed:
                record = self.get(artifact_id)
                if not self._resolved_path(record).is_file():
                    record["validity"] = "missing"
            self._save()
            return affected
        return []

    def current(self) -> dict[str, dict[str, Any]]:
        return current_records(self.data)
