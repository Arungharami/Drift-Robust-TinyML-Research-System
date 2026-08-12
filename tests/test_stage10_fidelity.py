import csv
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]; EID="EXP-XAI-FIDELITY-001"
def rows(path):
    with (ROOT/path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))

def test_executed_stage10_has_all_outputs_and_valid_manifest():
    pipeline=yaml.safe_load((ROOT/"configs/pipeline_stages.yaml").read_text(encoding="utf-8"))["stages"]
    stage=next(s for s in pipeline if s["id"]=="10")
    assert stage["status"]=="EXECUTED"
    assert all((ROOT/path).exists() for path in stage["artifact_paths"])
    assert rows("results/xai/stage10_manifest.csv")

def test_ci_schema_ids_units_and_bounds():
    valid_models={"MODEL-C1","MODEL-C2","MODEL-C3","MODEL-C4"}
    for row in rows("results/xai/stage10_bootstrap_ci.csv"):
        assert row["experiment_id"]==EID and row["model_id"] in valid_models
        assert row["unit"] and int(row["n"])>0
        assert float(row["ci_low"]) <= float(row["estimate"]) <= float(row["ci_high"])

def test_local_samples_trace_to_stage09():
    source={(r["model_id"],r["sample_id"]) for r in rows("results/xai/stage09_local_samples.csv")}
    assert all((r["model_id"],r["sample_id"]) in source for r in rows("results/xai/stage10_fidelity_local.csv"))

def test_reference_is_batch1_only_and_methods_are_applicable():
    protocol=yaml.safe_load((ROOT/"configs/xai_fidelity_protocol.yaml").read_text(encoding="utf-8"))
    assert protocol["reference"]["batch"]==1 and protocol["reference"]["future_statistics_forbidden"] is True
    applicable={(m,model) for m,models in protocol["global_methods"].items() for model in models}
    assert all((r["method"],r["model_id"]) in applicable and r["reference_source"]=="BATCH_1_SAVED_SCALER_MEAN" for r in rows("results/xai/stage10_fidelity_global.csv"))

def test_stage11_cannot_execute_before_stage10_gate():
    pipeline=yaml.safe_load((ROOT/"configs/pipeline_stages.yaml").read_text(encoding="utf-8"))["stages"]
    s10=next(s for s in pipeline if s["id"]=="10"); s11=next(s for s in pipeline if s["id"]=="11")
    if s11["status"]=="EXECUTED":
        assert s10["status"]=="EXECUTED" and (ROOT/"results/xai/stage10_manifest.csv").exists()

def test_portal_stage10_status_comes_from_registry_export():
    exporter=(ROOT/"scripts/portal/export_evidence.py").read_text(encoding="utf-8")
    assert '"fidelity_status": "EXECUTED" if fidelity_manifest' in exporter
