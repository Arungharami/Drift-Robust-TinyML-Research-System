"""Configuration loading/validation for the Colab CLI control plane (configs/colab.yaml).

No secrets are read or written here. configs/colab.yaml is the single source of truth for
session names, remote paths, workspace rules, and the dataset gate (Mission 39) — scripts and
tests both read through this module rather than duplicating constants.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "colab.yaml"

REQUIRED_TOP_LEVEL_KEYS = ("output_root", "seed", "colab")
REQUIRED_COLAB_KEYS = (
    "cli_tool",
    "auth_provider",
    "sessions",
    "remote_workspace",
    "drive_root",
    "workspace_include",
    "workspace_exclude_patterns",
    "dataset_gate",
)
REQUIRED_DATASET_GATE_KEYS = ("samples", "features", "batches", "classes", "archive_sha256")


class ColabConfigError(ValueError):
    """Raised when configs/colab.yaml is missing, unreadable, or malformed."""


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load and validate configs/colab.yaml. Raises ColabConfigError on any problem."""
    path = Path(path)
    if not path.exists():
        raise ColabConfigError(f"config file not found: {path}")
    with path.open(encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            raise ColabConfigError(f"config file is not valid YAML: {path}: {exc}") from exc
    if not isinstance(config, dict):
        raise ColabConfigError(f"config file must contain a YAML mapping: {path}")
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in config]
    if missing:
        raise ColabConfigError(f"configs/colab.yaml missing top-level keys: {missing}")

    colab = config["colab"]
    if not isinstance(colab, dict):
        raise ColabConfigError("configs/colab.yaml 'colab:' section must be a mapping")
    missing_colab = [k for k in REQUIRED_COLAB_KEYS if k not in colab]
    if missing_colab:
        raise ColabConfigError(f"configs/colab.yaml 'colab:' section missing keys: {missing_colab}")

    sessions = colab["sessions"]
    for role in ("cpu", "gpu"):
        if role not in sessions:
            raise ColabConfigError(f"configs/colab.yaml colab.sessions missing '{role}'")
        if "name" not in sessions[role]:
            raise ColabConfigError(f"configs/colab.yaml colab.sessions.{role} missing 'name'")

    gate = colab["dataset_gate"]
    missing_gate = [k for k in REQUIRED_DATASET_GATE_KEYS if k not in gate]
    if missing_gate:
        raise ColabConfigError(f"configs/colab.yaml colab.dataset_gate missing keys: {missing_gate}")


def get_value(config: dict[str, Any], dotted_key: str, default: Any = None) -> Any:
    """Fetch a nested value by dotted path, e.g. get_value(cfg, 'colab.sessions.cpu.name')."""
    node: Any = config
    for part in dotted_key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return default
    return node
