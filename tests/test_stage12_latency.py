from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
XD = ROOT / "results/xai"


def test_raw_timing_traceability_units_and_timer() -> None:
    raw = pd.read_csv(XD / "stage12_raw_timings.csv")
    assert len(raw) > 0
    assert raw[["experiment_id", "run_id", "model_id", "method", "scope", "phase", "wall_time_ns", "unit"]].notna().all().all()
    assert set(raw.unit) == {"nanoseconds"}
    assert set(raw.timer) == {"time.perf_counter_ns"}
    assert set(raw.hardware_scope) == {"HOST"}
    assert (raw.wall_time_ns >= 0).all()


def test_summary_regenerates_from_measured_raw() -> None:
    raw = pd.read_csv(XD / "stage12_raw_timings.csv")
    summary = pd.read_csv(XD / "stage12_latency_summary.csv")
    measured = raw[raw.warmup_or_measured.eq("MEASURED")]
    keys = ["model_id", "method", "scope", "batch", "phase", "feature_count", "sample_count", "prediction_calls", "batch_size", "environment_id"]
    rebuilt = measured.groupby(keys, dropna=False).wall_time_ns.agg(
        n="size", median_ns="median", p95_ns=lambda values: np.quantile(values, .95)
    ).reset_index()
    merged = summary.merge(rebuilt, on=keys, suffixes=("_saved", "_rebuilt"))
    assert len(merged) == len(summary) == len(rebuilt)
    assert (merged.n_saved == merged.n_rebuilt).all()
    assert np.allclose(merged.median_ns_saved, merged.median_ns_rebuilt)
    assert np.allclose(merged.p95_ns_saved, merged.p95_ns_rebuilt)


def test_timing_boundaries_do_not_hide_model_load_or_io() -> None:
    raw = pd.read_csv(XD / "stage12_raw_timings.csv")
    assert "MODEL_LOAD" in set(raw.phase)
    steady = raw[raw.phase.isin(["EXPLANATION_COMPUTE", "GLOBAL_EXPLANATION_TOTAL", "ONE_TIME_GLOBAL_EXTRACTION_COST"])]
    assert not steady.phase.eq("MODEL_LOAD").any()
    assert not steady.phase.str.contains(r"(^|_)(FILE|WRITE|IO)($|_)", case=False, regex=True).any()


def test_thread_control_is_effective_and_permutation_n_jobs_is_one() -> None:
    env = json.loads((XD / "stage12_thread_environment.json").read_text(encoding="utf-8"))
    assert all(int(v) == 1 for v in env["requested_environment"].values())
    assert env["effective_max_threads"] == 1
    assert all(pool["num_threads"] == 1 for pool in env["effective_threadpools"])
    assert env["sklearn_n_jobs"] == 1
    protocol = yaml.safe_load((ROOT / "configs/xai_latency_protocol.yaml").read_text(encoding="utf-8"))
    assert protocol["permutation_n_jobs"] == 1


def test_global_and_local_scopes_are_not_universal_leaderboard() -> None:
    trade = pd.read_csv(XD / "stage12_fidelity_stability_cost.csv")
    assert set(trade.scope) == {"GLOBAL", "LOCAL"}
    assert set(trade.interpretation) == {"CONTINUOUS_EVIDENCE_NO_COMPOSITE_SCORE"}
    report = (ROOT / "docs/experiments/STAGE12_XAI_LATENCY.md").read_text(encoding="utf-8")
    assert "universal" in report.lower() and "leaderboard" in report.lower()


def test_operation_counts_and_ablation_equivalence() -> None:
    counts = pd.read_csv(XD / "stage12_operation_counts.csv")
    ablation = counts[counts.method.str.contains("ABLATION")]
    assert len(ablation) == 8
    assert (ablation.feature_count == 128).all()
    assert (ablation.perturbed_samples == 129).all()
    assert set(ablation.prediction_calls) == {2, 129}
    equivalence = pd.read_csv(XD / "stage12_ablation_equivalence.csv")
    assert len(equivalence) == 12
    assert equivalence.status.eq("EQUIVALENT").all()
    assert (equivalence.max_absolute_error <= equivalence.absolute_tolerance).all()


def test_stage09_to_11_inputs_remain_hash_verified() -> None:
    inputs = pd.read_csv(XD / "stage12_input_manifest.csv")
    assert len(inputs) >= 12
    assert inputs.verification_status.eq("VERIFIED").all()
    for row in inputs.itertuples():
        assert hashlib.sha256((ROOT / row.path).read_bytes()).hexdigest() == row.sha256


def test_no_physical_or_mcu_measurement_claim_and_stage13_not_executed() -> None:
    manifest = json.loads((ROOT / "artifacts/explanations/EXP-XAI-LATENCY-001/manifest.json").read_text(encoding="utf-8"))
    assert manifest["scientific_scope"] == "HOST_MEASURED"
    assert manifest["mcu_latency"] == "NOT_MEASURED"
    assert manifest["physical_energy"] == "NOT_MEASURED"
    host = json.loads((XD / "stage12_host_environment.json").read_text(encoding="utf-8"))
    assert host["mcu_latency"] == "NOT_MEASURED"
    assert host["physical_energy"] == "NOT_MEASURED"
    pipeline = yaml.safe_load((ROOT / "configs/pipeline_stages.yaml").read_text(encoding="utf-8"))["stages"]
    assert next(stage for stage in pipeline if stage["id"] == "12")["status"] == "EXECUTED"
    assert next(stage for stage in pipeline if stage["id"] == "13")["status"] in {"NOT_EXECUTED", "PROTOCOL_FROZEN"}


def test_stage12_manifest_hashes_and_figure_sources() -> None:
    manifest = pd.read_csv(XD / "stage12_manifest.csv")
    for row in manifest.itertuples():
        path = ROOT / row.artifact_path
        assert path.exists()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row.sha256
    figure_sources = manifest[manifest.artifact_path.str.match(r"results/figures/sources/lat_\d{2}")]
    assert len(figure_sources) == 9
