"""Execute checkpoint-1 fixed-origin feature drift and publication figures."""
from __future__ import annotations
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from src.drift.feature_drift import compute_drift
from src.utils.hashing import stable_hash
from src.utils.registry import FIELDS, append_experiment

def save_figure(fig: plt.Figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf", "svg"): fig.savefig(stem.with_suffix(f".{suffix}"), bbox_inches="tight", dpi=300)
    plt.close(fig)

def main() -> None:
    validation = json.loads(Path("results/reproducibility/dataset_validation.json").read_text(encoding="utf-8"))
    if validation["status"] != "COMPLETED": raise SystemExit("Validated dataset required")
    feature, global_drift, chronology = compute_drift(Path("data/raw"))
    drift_dir = Path("results/drift"); figure_sources = Path("results/figures/sources")
    drift_dir.mkdir(parents=True, exist_ok=True); figure_sources.mkdir(parents=True, exist_ok=True)
    feature.to_csv(drift_dir / "feature_drift_by_batch.csv", index=False)
    global_drift.to_csv(drift_dir / "global_drift_by_batch.csv", index=False)
    chronology.to_csv(figure_sources / "dataset_timeline.csv", index=False)
    metric = feature[feature.metric == "normalized_wasserstein"]
    matrix = metric.pivot(index="feature", columns="comparison_batch", values="value")
    matrix.to_csv(figure_sources / "feature_batch_drift_heatmap.csv")
    mean_rank = metric.groupby("feature", as_index=False).value.mean().sort_values("value", ascending=False)
    top = mean_rank.head(20); stable = mean_rank.tail(20).sort_values("value")
    top.to_csv(figure_sources / "top20_drifting_features.csv", index=False); stable.to_csv(figure_sources / "top20_stable_features.csv", index=False)
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(8, 4)); ax.bar(chronology.batch.astype(str), chronology.sample_count); ax.set(xlabel="Chronological batch", ylabel="Samples", title="Dataset chronology"); save_figure(fig, Path("results/figures/dataset_timeline"))
    fig, ax = plt.subplots(figsize=(9, 6)); image = ax.imshow(matrix, aspect="auto", cmap="magma"); fig.colorbar(image, ax=ax, label="Normalized Wasserstein distance"); ax.set(xlabel="Comparison batch", ylabel="Feature", title="Feature drift from batch 1"); ax.set_xticks(range(len(matrix.columns)), matrix.columns); save_figure(fig, Path("results/figures/feature_batch_drift_heatmap"))
    for frame, name, title in ((top, "top20_drifting_features", "Top 20 drifting features"), (stable, "top20_stable_features", "Top 20 stable features")):
        fig, ax = plt.subplots(figsize=(8, 5)); ax.barh(frame.feature.astype(str), frame.value); ax.invert_yaxis(); ax.set(xlabel="Mean normalized Wasserstein distance", ylabel="Feature", title=title); save_figure(fig, Path("results/figures") / name)
    trajectory = global_drift[global_drift.metric == "normalized_wasserstein"]; trajectory.to_csv(figure_sources / "global_drift_trajectory.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 4)); ax.plot(trajectory.comparison_batch, trajectory.median_feature_drift, marker="o"); ax.set(xlabel="Comparison batch", ylabel="Median normalized Wasserstein distance", title="Global feature drift from batch 1"); save_figure(fig, Path("results/figures/global_drift_trajectory"))
    experiment_id = "DRIFT-FIXED-B1-001"; now = datetime.now(timezone.utc).isoformat()
    commit = subprocess.run(["git","rev-parse","HEAD"], capture_output=True, text=True).stdout.strip()
    record = dict.fromkeys(FIELDS, ""); record.update({"experiment_id":experiment_id,"timestamp":now,"research_question":"How does feature drift evolve from batch 1?","protocol":"FIXED_ORIGIN","model":"NONE","representation":"RAW_128D","train_batches":"1","test_batches":"2-10","seed":"NOT_APPLICABLE","dataset_hash":validation["dataset_hash"],"split_hash":stable_hash({"train":[1],"test":list(range(2,11))}),"config_hash":stable_hash(Path("configs/experiments.yaml").read_text()),"git_commit":commit,"environment":"results/reproducibility/environment.json","status":"COMPLETED","metrics_artifact":"results/drift/feature_drift_by_batch.csv","notes":"Univariate normalized Wasserstein and standardized mean shift; median aggregation."})
    append_experiment(Path("results/registry/experiment_registry.csv"), record)
    print(f"Completed {experiment_id}: {len(feature)} feature-metric rows")

if __name__ == "__main__": main()
