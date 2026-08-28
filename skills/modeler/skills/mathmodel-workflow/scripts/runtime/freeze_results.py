#!/usr/bin/env python3
"""Freeze a registered result artifact after recording reproducibility inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from .artifact_registry import ArtifactRegistry
except ImportError:
    from artifact_registry import ArtifactRegistry


def freeze_artifact(
    project_root: Path,
    artifact_id: str,
    *,
    source_hashes: dict[str, str],
    randomness_policy: str,
) -> dict[str, Any]:
    registry = ArtifactRegistry(project_root)
    return registry.freeze(
        artifact_id,
        source_hashes=source_hashes,
        randomness_policy=randomness_policy,
    )
