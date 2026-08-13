"""Stage-09 provenance manifest construction. No circular provenance: every hash here is
computed from a real, already-on-disk file (source model artifact, config, outputs) — never
from a value this module itself just invented.
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sklearn

from src.utils.hashing import sha256_file, stable_hash

REPO_ROOT = Path(__file__).resolve().parents[2]


def git_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def software_versions() -> dict[str, str]:
    import joblib
    import numpy
    import pandas

    return {
        "python": platform.python_version(),
        "numpy": numpy.__version__,
        "pandas": pandas.__version__,
        "scikit_learn": sklearn.__version__,
        "joblib": joblib.__version__,
    }


def build_manifest(
    *,
    experiment_id: str,
    status: str,
    dataset_hash: str,
    split_protocol: str,
    model_id: str,
    source_model_experiment_id: str,
    model_artifact_path: Path,
    explainer_methods: list[str],
    random_seed: int,
    input_artifacts: list[str],
    output_artifacts: list[str],
    notes: str,
) -> dict[str, Any]:
    return {
        "experiment_id": experiment_id,
        "stage": "09",
        "status": status,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": git_commit(),
        "dataset_hash": dataset_hash,
        "split_protocol": split_protocol,
        "model_id": model_id,
        "source_model_experiment_id": source_model_experiment_id,
        "model_artifact_sha256": sha256_file(model_artifact_path) if model_artifact_path.exists() else None,
        "explainer_methods": explainer_methods,
        "random_seed": random_seed,
        "software_versions": software_versions(),
        "input_artifacts": input_artifacts,
        "output_artifacts": output_artifacts,
        "notes": notes,
    }


def config_hash(config: dict[str, Any]) -> str:
    return stable_hash(config)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
