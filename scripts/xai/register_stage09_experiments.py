#!/usr/bin/env python3
"""One-off script: append the four Stage-09 rows to results/registry/experiment_registry.csv
using the project's own append_experiment() so the schema/status enum is enforced identically
to every other registered experiment. Reads real values only (manifest.json, environment.json,
the frozen config) — nothing here is invented.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
import sys

sys.path.insert(0, str(REPO_ROOT))

from src.utils.registry import append_experiment  # noqa: E402

manifest = json.loads((REPO_ROOT / "artifacts/explanations/EXP-XAI-0001/manifest.json").read_text())
environment = json.loads((REPO_ROOT / "artifacts/explanations/EXP-XAI-0001/environment.json").read_text())
config_hash = manifest["config_hash"]
git_commit = manifest["git_commit"]
timestamp = manifest["created_at"]

MODELS = ["MODEL-C1", "MODEL-C2", "MODEL-C3", "MODEL-C4"]
RESEARCH_QUESTION = (
    "What lightweight explanation representations can be generated for the existing "
    "drift-robust model candidates, and which representations are practical enough to "
    "evaluate later for fidelity, stability, latency, and TinyML deployment?"
)

registry_path = REPO_ROOT / "results/registry/experiment_registry.csv"
for model_id in MODELS:
    status = manifest["per_model_status"].get(model_id, {}).get("status")
    registry_status = "COMPLETED" if status == "EXECUTED" else "FAILED"
    record = {
        "experiment_id": f"EXP-XAI-0001-{model_id[-2:]}",
        "timestamp": timestamp,
        "research_question": RESEARCH_QUESTION,
        "protocol": "FIXED_ORIGIN",
        "model": model_id,
        "representation": "RAW_128D_STANDARDIZED",
        "train_batches": "1",
        "validation_batches": "",
        "test_batches": "2-10",
        "seed": 42,
        "dataset_hash": "dc9dbcfc4c8eedceae4418d8f2096605ccb2b3bd554a3134f84c46d22b0615e6",
        "split_hash": "5f3ceed0e1c14ff404d9167517b124493d2df882f179fa953c67d5483246a8ae",
        "config_hash": config_hash,
        "git_commit": git_commit,
        "environment": "artifacts/explanations/EXP-XAI-0001/environment.json",
        "status": registry_status,
        "metrics_artifact": "results/xai/stage09_global_importance.csv",
        "model_artifact": f"artifacts/models/BASE-FIXED-{model_id[-2:]}-001.joblib",
        "notes": (
            "Stage 09 resource-aware XAI. No retraining; loads frozen FIXED_ORIGIN model "
            f"artifact. Explanations saved under artifacts/explanations/EXP-XAI-0001/. "
            f"Method applicability: results/xai/stage09_manifest.csv."
        ),
    }
    append_experiment(registry_path, record)
    print(f"registered {record['experiment_id']} status={registry_status}")
