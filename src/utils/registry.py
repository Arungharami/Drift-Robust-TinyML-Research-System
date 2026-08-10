"""Append-only experiment registry with fixed provenance fields."""
from __future__ import annotations
import csv
from pathlib import Path

FIELDS = ["experiment_id","timestamp","research_question","protocol","model","representation","train_batches","validation_batches","test_batches","seed","dataset_hash","split_hash","config_hash","git_commit","environment","status","metrics_artifact","model_artifact","notes"]
VALID_STATUSES = {"PLANNED","RUNNING","COMPLETED","FAILED","INVALID","NOT_EXECUTED","SUPERSEDED"}

def append_experiment(path: Path, record: dict[str, object]) -> None:
    if set(record) != set(FIELDS): raise ValueError("Registry record fields do not match schema")
    if record["status"] not in VALID_STATUSES: raise ValueError("Invalid experiment status")
    path.parent.mkdir(parents=True, exist_ok=True); exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if not exists: writer.writeheader()
        writer.writerow(record)
