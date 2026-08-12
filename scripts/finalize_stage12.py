"""Finalize Stage 12 derived evidence without rerunning or altering raw timings."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.loader import batch_number, discover_batches, load_batch  # noqa: E402
from src.xai.local_ablation import SingleFeatureAblationExplainer  # noqa: E402

EID = "EXP-XAI-LATENCY-001"
XD = ROOT / "results/xai"


def _write(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(path, index=False)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_normalized_metrics() -> None:
    baseline = pd.read_csv(XD / "stage12_baseline_inference.csv")
    baseline["median_us_per_sample"] = baseline["median_us"] / baseline["sample_count"]
    baseline["p95_us_per_sample"] = baseline["p95_us"] / baseline["sample_count"]
    baseline["primary_metric"] = "host_inference_latency_us_per_sample"
    _write(XD / "stage12_baseline_inference.csv", baseline)

    global_cost = pd.read_csv(XD / "stage12_global_latency.csv")
    global_cost["global_explanation_total_ms"] = np.where(
        global_cost["phase"].eq("GLOBAL_EXPLANATION_TOTAL"), global_cost["median_us"] / 1000, np.nan
    )
    global_cost["normalized_ms_per_evaluated_sample"] = np.where(
        global_cost["phase"].eq("GLOBAL_EXPLANATION_TOTAL"),
        global_cost["median_us"] / 1000 / global_cost["sample_count"],
        np.nan,
    )
    global_cost["normalization_warning"] = np.where(
        global_cost["phase"].eq("GLOBAL_EXPLANATION_TOTAL"),
        "SECONDARY_DIAGNOSTIC_NOT_LOCAL_EXPLANATION_LATENCY",
        "NOT_APPLICABLE",
    )
    _write(XD / "stage12_global_latency.csv", global_cost)

    local = pd.read_csv(XD / "stage12_local_latency.csv")
    local = local.drop(columns=[
        "baseline_median_us", "baseline_median_us_x", "baseline_median_us_y",
        "explanation_overhead_ratio", "overhead_numerator_us", "overhead_denominator_us", "ratio_scope",
    ], errors="ignore")
    base = baseline[(baseline.scope == "LOCAL") & (baseline.phase == "BASELINE_INFERENCE_END_TO_END")][
        ["model_id", "batch", "median_us"]
    ].rename(columns={"median_us": "baseline_median_us"})
    local = local.merge(base, on=["model_id", "batch"], how="left")
    eligible = local.phase.eq("EXPLANATION_COMPUTE")
    local["explanation_overhead_ratio"] = np.where(eligible, local.median_us / local.baseline_median_us, np.nan)
    local["overhead_numerator_us"] = np.where(eligible, local.median_us, np.nan)
    local["overhead_denominator_us"] = np.where(eligible, local.baseline_median_us, np.nan)
    local["ratio_scope"] = np.where(eligible, "LOCAL_MATCHED_MODEL_BATCH_ONLY", "NOT_APPLICABLE")
    _write(XD / "stage12_local_latency.csv", local)


def validate_ablation_equivalence() -> pd.DataFrame:
    samples = pd.read_csv(XD / "stage09_local_samples.csv")
    samples = samples[samples.batch.isin([2, 6, 10])].sort_values("sample_id").groupby(
        ["model_id", "batch"], as_index=False
    ).first()
    paths = {batch_number(p): p for p in discover_batches(ROOT / "data/raw")}
    data = {b: load_batch(paths[b])[0] for b in [2, 6, 10]}
    records = []
    for row in samples.itertuples():
        model_path = ROOT / f"artifacts/models/BASE-FIXED-{row.model_id.replace('MODEL-', '')}-001.joblib"
        pipe = joblib.load(model_path)
        estimator = pipe.named_steps["model"]
        if hasattr(estimator, "n_jobs"):
            estimator.n_jobs = 1
        x = data[int(row.batch)][int(row.row_index_in_batch)]
        reference = np.asarray(pipe.named_steps["scaler"].mean_)
        vectorized = np.asarray(
            SingleFeatureAblationExplainer(pipe, row.model_id, reference).explain_local(x)["feature_contributions"],
            dtype=float,
        )
        base = pipe.predict_proba(x.reshape(1, -1))[0]
        class_index = int(np.argmax(base))
        naive = []
        for feature in range(128):
            perturbed = x.copy()
            perturbed[feature] = reference[feature]
            naive.append(base[class_index] - pipe.predict_proba(perturbed.reshape(1, -1))[0, class_index])
        naive = np.asarray(naive)
        max_error = float(np.max(np.abs(vectorized - naive)))
        records.append(
            {
                "experiment_id": EID,
                "model_id": row.model_id,
                "batch": int(row.batch),
                "sample_id": row.sample_id,
                "vector_length": len(vectorized),
                "absolute_tolerance": 1e-12,
                "max_absolute_error": max_error,
                "status": "EQUIVALENT" if max_error <= 1e-12 else "FAILED",
            }
        )
    frame = pd.DataFrame(records)
    _write(XD / "stage12_ablation_equivalence.csv", frame)
    if not frame.status.eq("EQUIVALENT").all():
        raise RuntimeError("Vectorized and naive ablation outputs are not equivalent")
    return frame


def evaluate_claims() -> pd.DataFrame:
    local = pd.read_csv(XD / "stage12_local_latency.csv")
    global_cost = pd.read_csv(XD / "stage12_global_latency.csv")
    counts = pd.read_csv(XD / "stage12_operation_counts.csv")
    ci = pd.read_csv(XD / "stage12_bootstrap_ci.csv")

    compute = local[local.phase.eq("EXPLANATION_COMPUTE")]
    ratios = compute.groupby(["model_id", "method"], as_index=False).explanation_overhead_ratio.mean()
    material = False
    for _, group in ratios.groupby("model_id"):
        values = group.explanation_overhead_ratio.dropna().to_numpy()
        if len(values) >= 2 and values.max() / values.min() >= 2:
            material = True

    baseline = pd.read_csv(XD / "stage12_baseline_inference.csv")
    b = baseline[(baseline.scope == "LOCAL") & baseline.phase.eq("BASELINE_INFERENCE_END_TO_END")].groupby("model_id").median_us.mean()
    ab = compute[compute.method.eq("SINGLE_FEATURE_ABLATION_LOCAL_NAIVE_REFERENCE")].groupby("model_id").median_us.mean()
    common = sorted(set(b.index) & set(ab.index))
    rho = float(spearmanr([b[x] for x in common], [ab[x] for x in common]).statistic)
    # With four model-level observations, the preregistered positive bootstrap-CI criterion is not established.
    calls_ok = counts[counts.method.str.contains("ABLATION")].additional_prediction_calls.max() == 128

    intrinsic = global_cost[global_cost.phase.eq("ONE_TIME_GLOBAL_EXTRACTION_COST")].set_index("model_id")
    permutation_raw = pd.read_csv(XD / "stage12_raw_timings.csv")
    permutation_raw = permutation_raw[
        permutation_raw.method.eq("PERMUTATION_IMPORTANCE_MACRO_F1")
        & permutation_raw.phase.eq("GLOBAL_EXPLANATION_TOTAL")
        & permutation_raw.warmup_or_measured.eq("MEASURED")
    ]
    claim3 = all(
        row.median_ns < np.quantile(permutation_raw[permutation_raw.model_id.eq(model)].wall_time_ns, 0.05)
        for model, row in intrinsic.iterrows()
    )

    rows = [
        ("C-XAI-COST-01", "SUPPORTED" if material else "UNSUPPORTED", f"At least one matched local-method overhead ratio differs by >=2x: {material}."),
        ("C-XAI-COST-02", "UNRESOLVED", f"Additional-call criterion={calls_ok}; model-level Spearman rho={rho:.3f}, but positive bootstrap CI is not established with N=4 models."),
        ("C-XAI-COST-03", "SUPPORTED" if claim3 else "UNSUPPORTED", f"Intrinsic extraction is below permutation p05 for both applicable models: {claim3}."),
        ("C-XAI-COST-04", "UNRESOLVED", "Stage-10/11 method coverage is incomplete for a fully matched dominance test; no universal composite score was constructed."),
    ]
    frame = pd.DataFrame(rows, columns=["claim_id", "status", "evidence_summary"])
    frame.insert(0, "experiment_id", EID)
    frame["acceptance_source"] = "configs/xai_latency_protocol.yaml"
    _write(XD / "stage12_claim_evaluation.csv", frame)
    return frame


def refresh_manifest() -> None:
    manifest_path = XD / "stage12_manifest.csv"
    old = pd.read_csv(manifest_path)
    paths = list(old.artifact_path) + [
        "results/xai/stage12_ablation_equivalence.csv",
        "results/xai/stage12_claim_evaluation.csv",
    ]
    records = []
    for rel in dict.fromkeys(paths):
        path = ROOT / rel
        rows = sum(1 for _ in path.open(encoding="utf-8")) - 1 if path.suffix == ".csv" else ""
        records.append({"experiment_id": EID, "artifact_path": rel, "sha256": _sha(path), "rows": rows, "status": "EXECUTED"})
    _write(manifest_path, pd.DataFrame(records))
    artifact_manifest = ROOT / f"artifacts/explanations/{EID}/manifest.json"
    doc = json.loads(artifact_manifest.read_text(encoding="utf-8"))
    doc["outputs"] = records
    artifact_manifest.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    add_normalized_metrics()
    equivalence = validate_ablation_equivalence()
    claims = evaluate_claims()
    refresh_manifest()
    print(f"Stage 12 finalized: {len(equivalence)} equivalence checks; claims={dict(zip(claims.claim_id, claims.status))}")
