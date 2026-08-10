import csv
from pathlib import Path
from src.utils.registry import FIELDS, append_experiment
def test_registry_schema(tmp_path: Path):
    record=dict.fromkeys(FIELDS,""); record["status"]="PLANNED"; append_experiment(tmp_path/"r.csv",record)
    assert next(csv.DictReader((tmp_path/"r.csv").open()))["status"]=="PLANNED"
