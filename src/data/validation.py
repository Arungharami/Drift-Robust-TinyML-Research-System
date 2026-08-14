"""Independent structural validation of the downloaded batch files."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
import numpy as np
from src.data.loader import batch_number, discover_batches, load_batch
from src.utils.hashing import sha256_file, stable_hash

def validate_dataset(raw_dir: Path, json_path: Path, markdown_path: Path) -> dict:
    paths = discover_batches(raw_dir); batch_rows = {}; labels = Counter(); malformed = []
    feature_count = 128; missing_values = 0
    for path in paths:
        try: x, y = load_batch(path, feature_count)
        except ValueError as exc: malformed.append(str(exc)); continue
        batch_rows[str(batch_number(path))] = len(y); labels.update(map(int, y)); missing_values += int(np.isnan(x).sum())
    report = {"status": "COMPLETED" if not malformed else "INVALID", "samples": sum(batch_rows.values()),
              "features": feature_count, "batches": len(paths), "classes": len(labels), "batch_rows": batch_rows,
              "labels": dict(sorted(labels.items())), "missing_values": missing_values, "malformed_rows": malformed,
              "batch_hashes": {p.name: sha256_file(p) for p in paths}}
    report["dataset_hash"] = stable_hash(report["batch_hashes"])
    expected = {"samples": 13910, "features": 128, "batches": 10, "classes": 6}
    report["expectations"] = {key: {"expected": val, "actual": report[key], "matches": report[key] == val} for key, val in expected.items()}
    if not all(item["matches"] for item in report["expectations"].values()): report["status"] = "INVALID"
    json_path.parent.mkdir(parents=True, exist_ok=True); json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Dataset validation", "", f"Status: **{report['status']}**", "", "| Check | Expected | Actual | Match |", "|---|---:|---:|:---:|"]
    lines += [f"| {k} | {v['expected']} | {v['actual']} | {v['matches']} |" for k, v in report["expectations"].items()]
    lines += ["", f"Dataset hash: `{report['dataset_hash']}`", f"Missing values: {missing_values}", f"Malformed rows: {len(malformed)}"]
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report
