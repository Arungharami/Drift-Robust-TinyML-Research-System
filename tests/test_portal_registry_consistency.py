import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_portal_never_denies_registered_xai():
    with (ROOT / "results/registry/experiment_registry.csv").open(encoding="utf-8-sig") as f:
        has_xai = any(row["experiment_id"].startswith("EXP-XAI") for row in csv.DictReader(f))
    source = (ROOT / "research-portal/app/experiments/page.tsx").read_text(encoding="utf-8").lower()
    forbidden = ("xai experiments are not yet registered", "no xai experiment is registered", "xai experiments are not registered")
    assert not has_xai or not any(text in source for text in forbidden)
