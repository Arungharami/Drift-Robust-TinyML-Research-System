from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]

def test_normalized_evidence_validation():
    subprocess.run([sys.executable, "scripts/build_research_intelligence.py"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "scripts/validate_research_evidence.py"], cwd=ROOT, check=True)

def test_feature_metadata_is_16_by_8():
    import csv
    with (ROOT / "research/feature_metadata.csv").open() as f: rows = list(csv.DictReader(f))
    assert len(rows) == 128
    assert len({r["sensor_id"] for r in rows}) == 16
    assert all(sum(r["sensor_id"] == f"S{i}" for r in rows) == 8 for i in range(1, 17))
