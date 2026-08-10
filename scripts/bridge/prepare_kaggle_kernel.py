#!/usr/bin/env python3
"""scripts/bridge/prepare_kaggle_kernel.py — assemble platforms/kaggle/kernel/ (Mission 12).

Writes kernel-metadata.json referencing the reproduction notebook. PRIVATE (`is_private: true`)
by default; GPU/internet are off by default since the reproduction notebook only needs CPU and
the bundled dataset.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.research_bridge.config import get_value, load_config  # noqa: E402

KERNEL_DIR = REPO_ROOT / "platforms" / "kaggle" / "kernel"
NOTEBOOK_NAME = "drift_tinyml_reproduction.ipynb"


def main() -> int:
    config = load_config()
    slug = get_value(config, "kaggle.kernel_slug", "drift-robust-tinyml-reproduction")
    username = get_value(config, "kaggle.username") or "USERNAME_NOT_DISCOVERED"

    KERNEL_DIR.mkdir(parents=True, exist_ok=True)
    notebook_path = KERNEL_DIR / NOTEBOOK_NAME
    if not notebook_path.exists():
        print(f"missing {notebook_path} — create it before pushing (see docs)", file=sys.stderr)
        return 1

    metadata = {
        "id": f"{username}/{slug}",
        "title": "Drift-Robust TinyML Reproduction",
        "code_file": NOTEBOOK_NAME,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": False,
        "enable_internet": False,
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
    }
    (KERNEL_DIR / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {KERNEL_DIR}. Kernel is PRIVATE by default (is_private: true).")
    print("Push explicitly with: kaggle kernels push -p platforms/kaggle/kernel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
