"""Fail on broken provenance, invalid states, or status/artifact disagreement."""
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID = {"MEASURED", "DERIVED", "EXECUTED", "PLANNED", "BLOCKED", "FAILED", "NOT_APPLICABLE"}

def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))

errors = []
experiments = {r["experiment_id"]: r for r in read(ROOT / "results/registry/experiments.csv")}
artifacts = {r["artifact_id"]: r for r in read(ROOT / "results/registry/artifacts.csv")}
for r in experiments.values():
    if r["status"] not in VALID: errors.append(f"invalid experiment state: {r['experiment_id']}={r['status']}")
for r in read(ROOT / "results/registry/measurements.csv"):
    if r["experiment_id"] not in experiments: errors.append(f"orphan measurement: {r['experiment_id']}")
    if r["measurement_type"] not in VALID: errors.append(f"invalid measurement state: {r}")
    if r["measurement_type"] in {"MEASURED", "DERIVED", "EXECUTED"} and not r["unit"]: errors.append(f"metric lacks unit: {r}")
    if r["artifact_id"] not in artifacts: errors.append(f"measurement artifact missing: {r['artifact_id']}")
for r in artifacts.values():
    path = ROOT / r["path"]
    if not path.is_file(): errors.append(f"artifact path missing: {r['path']}"); continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != r["sha256"]: errors.append(f"artifact hash mismatch: {r['path']}")
for r in read(ROOT / "results/registry/claims.csv"):
    if r["status"] == "SUPPORTED" and (not r["supporting_artifacts"] or not (ROOT / r["supporting_artifacts"]).exists()): errors.append(f"supported claim lacks evidence: {r['claim_id']}")
if errors:
    print("\n".join(errors)); sys.exit(1)
print(f"Evidence validation passed: {len(experiments)} experiments, {len(artifacts)} artifacts.")
