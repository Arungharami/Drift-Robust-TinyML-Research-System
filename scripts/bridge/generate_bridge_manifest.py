#!/usr/bin/env python3
"""scripts/bridge/generate_bridge_manifest.py — build
results/reproducibility/bridge/platform_manifest.json from real, currently-known state
(Mission 14). Never invents an ID for a platform that hasn't actually produced one.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.colab_control.config import get_value as colab_get, load_config as load_colab_config  # noqa: E402
from src.research_bridge import manifest  # noqa: E402
from src.research_bridge.config import get_value as cfg_get, load_config  # noqa: E402

OUT_PATH = REPO_ROOT / "results" / "reproducibility" / "bridge" / "platform_manifest.json"


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", default="DRAFT")
    args = parser.parse_args()

    bridge_config = load_config()
    colab_config = load_colab_config()
    gate = colab_get(colab_config, "colab.dataset_gate", {})

    git_sha = _git("rev-parse", "HEAD")
    branch = _git("branch", "--show-current")

    m = manifest.build_platform_manifest(
        project="drift-robust-tinyml",
        git_repository=cfg_get(bridge_config, "github.repository"),
        git_branch=branch,
        git_sha=git_sha,
        dataset=manifest.dataset_block(
            source="UCI Gas Sensor Array Drift Dataset",
            archive_sha256=gate.get("archive_sha256", manifest.UNKNOWN),
        ),
        experiment=manifest.experiment_block(),
        github=manifest.github_block(commit=git_sha[:7], workflow_status=manifest.UNKNOWN),
        colab=manifest.colab_block(),  # NOT_EXECUTED until the WSL2 gate passes
        huggingface=manifest.huggingface_block(),  # NOT_CREATED until a repo actually exists
        kaggle=manifest.kaggle_block(),  # NOT_CREATED until a dataset/kernel actually exists
        created_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        status=args.status,
    )
    errors = manifest.validate_platform_manifest(m)
    if errors:
        print("platform manifest failed validation:", errors, file=sys.stderr)
        return 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
