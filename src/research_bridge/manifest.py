"""Cross-platform manifest schema (Mission 14) — results/reproducibility/bridge/platform_manifest.json.

Fields for platforms that have not run/been created must use one of the three explicit
placeholder statuses below — never a guessed or invented ID.
"""
from __future__ import annotations

from typing import Any

NOT_EXECUTED = "NOT_EXECUTED"
NOT_CREATED = "NOT_CREATED"
UNKNOWN = "UNKNOWN"
PLACEHOLDER_STATUSES = frozenset({NOT_EXECUTED, NOT_CREATED, UNKNOWN})

REQUIRED_TOP_KEYS = (
    "project",
    "git_repository",
    "git_branch",
    "git_sha",
    "dataset",
    "experiment",
    "github",
    "colab",
    "huggingface",
    "kaggle",
    "created_at",
    "status",
)


def dataset_block(source: str, archive_sha256: str, processed_hash: str = NOT_EXECUTED) -> dict[str, Any]:
    return {"source": source, "archive_sha256": archive_sha256, "processed_hash": processed_hash}


def experiment_block(
    experiment_id: str = NOT_EXECUTED, config_sha: str = NOT_EXECUTED, split_sha: str = NOT_EXECUTED
) -> dict[str, Any]:
    return {"experiment_id": experiment_id, "config_sha": config_sha, "split_sha": split_sha}


def github_block(commit: str, workflow_status: str = UNKNOWN) -> dict[str, Any]:
    return {"commit": commit, "workflow_status": workflow_status}


def colab_block(
    run_id: str = NOT_EXECUTED, environment: str = NOT_EXECUTED, status: str = NOT_EXECUTED
) -> dict[str, Any]:
    return {"run_id": run_id, "environment": environment, "status": status}


def huggingface_block(
    dataset_repo: str = NOT_CREATED,
    dataset_revision: str = NOT_EXECUTED,
    model_repo: str = NOT_CREATED,
    model_revision: str = NOT_EXECUTED,
) -> dict[str, Any]:
    return {
        "dataset_repo": dataset_repo,
        "dataset_revision": dataset_revision,
        "model_repo": model_repo,
        "model_revision": model_revision,
    }


def kaggle_block(
    dataset: str = NOT_CREATED,
    dataset_version: str = NOT_EXECUTED,
    kernel: str = NOT_CREATED,
    kernel_version: str = NOT_EXECUTED,
) -> dict[str, Any]:
    return {
        "dataset": dataset,
        "dataset_version": dataset_version,
        "kernel": kernel,
        "kernel_version": kernel_version,
    }


def build_platform_manifest(**fields: Any) -> dict[str, Any]:
    missing = [f for f in REQUIRED_TOP_KEYS if f not in fields]
    if missing:
        raise ValueError(f"platform manifest missing required fields: {missing}")
    return dict(fields)


def validate_platform_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return a list of validation errors (empty == valid). Never raises."""
    errors = [f"missing: {f}" for f in REQUIRED_TOP_KEYS if f not in manifest]
    for nested_key, sub_keys in (
        ("dataset", ("source", "archive_sha256", "processed_hash")),
        ("experiment", ("experiment_id", "config_sha", "split_sha")),
        ("github", ("commit", "workflow_status")),
        ("colab", ("run_id", "environment", "status")),
        ("huggingface", ("dataset_repo", "dataset_revision", "model_repo", "model_revision")),
        ("kaggle", ("dataset", "dataset_version", "kernel", "kernel_version")),
    ):
        block = manifest.get(nested_key)
        if not isinstance(block, dict):
            errors.append(f"missing or invalid block: {nested_key}")
            continue
        errors += [f"missing: {nested_key}.{k}" for k in sub_keys if k not in block]
    return errors
