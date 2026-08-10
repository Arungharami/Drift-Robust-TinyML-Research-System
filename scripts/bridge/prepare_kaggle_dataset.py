#!/usr/bin/env python3
"""scripts/bridge/prepare_kaggle_dataset.py — assemble platforms/kaggle/dataset/ (Mission 11).

Copies research-safe evidence only and writes dataset-metadata.json. PRIVATE by default. This
script only stages files locally for review — it does not call the kaggle CLI itself, so a
human reviews the staged contents before `kaggle datasets create` actually uploads anything.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.research_bridge.config import get_value, load_config  # noqa: E402
from src.research_bridge.secrets import scan_path  # noqa: E402

DATASET_DIR = REPO_ROOT / "platforms" / "kaggle" / "dataset"

CANDIDATE_FILES = [
    "results/reproducibility/dataset_validation.json",
    "results/reproducibility/dataset_validation.md",
    "results/reproducibility/environment.json",
    "results/reproducibility/bridge/platform_manifest.json",
]


def main() -> int:
    config = load_config()
    slug = get_value(config, "kaggle.dataset_slug", "drift-robust-tinyml-research-evidence")
    username = get_value(config, "kaggle.username") or "USERNAME_NOT_DISCOVERED"

    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    copied = []
    for rel in CANDIDATE_FILES:
        src = REPO_ROOT / rel
        if src.exists():
            dest = DATASET_DIR / Path(rel).name
            shutil.copy2(src, dest)
            copied.append(dest.name)
        else:
            print(f"skip (not yet generated): {rel}")

    metadata = {
        "title": "Drift-Robust TinyML Research Evidence",
        "id": f"{username}/{slug}",
        "licenses": [{"name": "CC0-1.0"}],
    }
    (DATASET_DIR / "dataset-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    findings = scan_path(DATASET_DIR)
    if findings:
        for f in findings:
            print(f"SECRET_FINDING: {f.category} in {f.location}", file=sys.stderr)
        return 1

    print(f"Prepared {DATASET_DIR} with {len(copied)} evidence file(s): {copied}")
    print("Dataset is PRIVATE by default. Push explicitly with: kaggle datasets create -p platforms/kaggle/dataset")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
