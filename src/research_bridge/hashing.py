"""SHA-256 artifact hashing and local-vs-remote comparison (Missions 15-16).

Every artifact exported to another platform gets a SHA-256 computed locally before upload and
recomputed on the downloaded copy after — a successful upload is never trusted on its own.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_artifact_index_row(
    *,
    artifact_id: str,
    experiment_id: str,
    local_path: str,
    sha256: str,
    size_bytes: int,
    git_sha: str,
    platform: str,
    remote_identifier: str,
    remote_revision: str,
    upload_timestamp: str,
    verification_status: str = "NOT_EXECUTED",
) -> dict[str, Any]:
    """Build one row for results/reproducibility/bridge/artifact_index.csv."""
    return {
        "artifact_id": artifact_id,
        "experiment_id": experiment_id,
        "local_path": local_path,
        "sha256": sha256,
        "size_bytes": size_bytes,
        "git_sha": git_sha,
        "platform": platform,
        "remote_identifier": remote_identifier,
        "remote_revision": remote_revision,
        "upload_timestamp": upload_timestamp,
        "verification_status": verification_status,
    }


ARTIFACT_INDEX_COLUMNS = (
    "artifact_id",
    "experiment_id",
    "local_path",
    "sha256",
    "size_bytes",
    "git_sha",
    "platform",
    "remote_identifier",
    "remote_revision",
    "upload_timestamp",
    "verification_status",
)


def compare_hashes(local_sha256: str, remote_sha256: str) -> str:
    """Return MATCH or MISMATCH — never anything that could be read as a silent pass."""
    if not local_sha256 or not remote_sha256:
        return "MISMATCH"
    return "MATCH" if local_sha256.lower() == remote_sha256.lower() else "MISMATCH"
