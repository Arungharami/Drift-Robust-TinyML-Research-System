"""Configuration loading/validation for configs/research_bridge.yaml.

No secrets are read or written here. GitHub is required to be marked canonical; the loader
refuses to proceed otherwise (Absolute Rule: no platform may silently become the source of
truth).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "research_bridge.yaml"

REQUIRED_TOP_LEVEL_KEYS = ("github", "colab", "huggingface", "kaggle", "drive")


class BridgeConfigError(ValueError):
    """Raised when configs/research_bridge.yaml is missing, unreadable, or malformed."""


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise BridgeConfigError(f"config file not found: {path}")
    with path.open(encoding="utf-8") as f:
        try:
            config = yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            raise BridgeConfigError(f"config file is not valid YAML: {path}: {exc}") from exc
    if not isinstance(config, dict):
        raise BridgeConfigError(f"config file must contain a YAML mapping: {path}")
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in config]
    if missing:
        raise BridgeConfigError(f"configs/research_bridge.yaml missing top-level keys: {missing}")

    github = config["github"]
    if not isinstance(github, dict) or not github.get("canonical", False):
        raise BridgeConfigError(
            "configs/research_bridge.yaml: github.canonical must be true — "
            "no other platform may become the source of truth"
        )
    if not github.get("repository"):
        raise BridgeConfigError("configs/research_bridge.yaml: github.repository is required")

    for platform in ("huggingface", "kaggle"):
        block = config[platform]
        if not isinstance(block, dict):
            raise BridgeConfigError(f"configs/research_bridge.yaml: '{platform}:' must be a mapping")
        if "private_by_default" in block and block["private_by_default"] is not True:
            raise BridgeConfigError(
                f"configs/research_bridge.yaml: {platform}.private_by_default must be true "
                "unless a human has explicitly reviewed and approved public release"
            )


def get_value(config: dict[str, Any], dotted_key: str, default: Any = None) -> Any:
    node: Any = config
    for part in dotted_key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return default
    return node
