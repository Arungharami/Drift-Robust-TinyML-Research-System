"""Build LAT-01..LAT-09 exclusively from saved Stage 12 evidence CSVs."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/figures"
SRC = OUT / "sources"
EID = "EXP-XAI-LATENCY-001"
OUT.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)
plt.style.use("seaborn-v0_8-whitegrid")


def save(stem: str, data: pd.DataFrame, draw) -> list[Path]:
    source = SRC / f"{stem}.csv"
    data.to_csv(source, index=False)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    draw(ax, data)
    ax.set_title(f"{stem.upper().replace('_', '-')} — HOST MEASURED")
    fig.tight_layout()
    png, svg = OUT / f"{stem}.png", OUT / f"{stem}.svg"
    fig.savefig(png, dpi=180)
    fig.savefig(svg)
    plt.close(fig)
    return [source, png, svg]


def main() -> None:
    baseline = pd.read_csv(ROOT / "results/xai/stage12_baseline_inference.csv")
    local = pd.read_csv(ROOT / "results/xai/stage12_local_latency.csv")
    global_cost = pd.read_csv(ROOT / "results/xai/stage12_global_latency.csv")
    counts = pd.read_csv(ROOT / "results/xai/stage12_operation_counts.csv")
    raw = pd.read_csv(ROOT / "results/xai/stage12_raw_timings.csv")
    trade = pd.read_csv(ROOT / "results/xai/stage12_fidelity_stability_cost.csv")
    created: list[Path] = []

    d = baseline[(baseline.scope == "LOCAL") & baseline.phase.eq("BASELINE_INFERENCE_END_TO_END")].groupby("model_id", as_index=False)[["median_us_per_sample", "p95_us_per_sample"]].mean()
    created += save("lat_01_baseline_host_inference", d, lambda ax, x: (x.set_index("model_id").plot.bar(ax=ax), ax.set_ylabel("µs per sample")))

    d = local[local.phase.eq("EXPLANATION_COMPUTE")].groupby(["model_id", "method"], as_index=False)[["median_us", "p95_us"]].mean()
    created += save("lat_02_local_explanation", d, lambda ax, x: (x.pivot(index="model_id", columns="method", values="median_us").plot.bar(ax=ax), ax.set_yscale("log"), ax.set_ylabel("median µs (log scale)")))

    d = local[local.phase.eq("EXPLANATION_COMPUTE")].groupby(["model_id", "method"], as_index=False).explanation_overhead_ratio.mean()
    created += save("lat_03_local_overhead", d, lambda ax, x: (x.pivot(index="model_id", columns="method", values="explanation_overhead_ratio").plot.bar(ax=ax), ax.set_yscale("log"), ax.set_ylabel("explanation / matched baseline (log)")))

    d = global_cost[global_cost.phase.isin(["ONE_TIME_GLOBAL_EXTRACTION_COST", "GLOBAL_EXPLANATION_TOTAL"])][["model_id", "method", "batch", "median_us", "p95_us"]]
    created += save("lat_04_global_total", d, lambda ax, x: (x.groupby(["model_id", "method"]).median_us.mean().unstack().plot.bar(ax=ax), ax.set_yscale("log"), ax.set_ylabel("total median µs (log scale)")))

    d = counts[["model_id", "method", "scope", "prediction_calls", "perturbed_samples", "feature_count"]].copy()
    d[["prediction_calls", "perturbed_samples", "feature_count"]] = d[["prediction_calls", "perturbed_samples", "feature_count"]].apply(pd.to_numeric)
    created += save("lat_05_computational_counts", d, lambda ax, x: (x.groupby(["scope", "method"])[["prediction_calls", "perturbed_samples"]].max().plot.bar(ax=ax), ax.set_yscale("symlog"), ax.set_ylabel("hardware-independent count")))

    d = raw[(raw.warmup_or_measured == "MEASURED") & raw.phase.isin(["EXPLANATION_COMPUTE", "GLOBAL_EXPLANATION_TOTAL", "ONE_TIME_GLOBAL_EXTRACTION_COST"])][["model_id", "method", "scope", "batch", "wall_time_ns"]]
    created += save("lat_06_host_latency_distribution", d, lambda ax, x: (x.assign(wall_time_us=x.wall_time_ns / 1000).boxplot(column="wall_time_us", by="method", ax=ax, rot=70, showfliers=True), ax.set_yscale("log"), ax.set_ylabel("wall time µs (log scale)"), ax.get_figure().suptitle("")))

    d = trade.dropna(subset=["stage10_fidelity_evidence"])[["model_id", "method", "scope", "median_us", "stage10_fidelity_evidence"]]
    created += save("lat_07_fidelity_vs_host_cost", d, lambda ax, x: (ax.scatter(x.median_us, x.stage10_fidelity_evidence), ax.set_xscale("log"), ax.set_xlabel("median host cost µs (log)"), ax.set_ylabel("Stage 10 continuous fidelity evidence")))

    d = trade.dropna(subset=["stage11_stability_evidence"])[["model_id", "method", "scope", "median_us", "stage11_stability_evidence"]]
    created += save("lat_08_stability_vs_host_cost", d, lambda ax, x: (ax.scatter(x.median_us, x.stage11_stability_evidence), ax.set_xscale("log"), ax.set_xlabel("median host cost µs (log)"), ax.set_ylabel("Stage 11 continuous stability evidence"), ax.text(.5, .5, "No fully matched rows" if x.empty else "", transform=ax.transAxes, ha="center")))

    d = trade[["model_id", "method", "scope", "median_us", "stage10_fidelity_evidence", "stage11_stability_evidence", "mcu_cost"]]
    created += save("lat_09_pre_hardware_evidence_map", d, lambda ax, x: (ax.scatter(range(len(x)), x.median_us), ax.set_yscale("log"), ax.set_xticks(range(len(x)), [f"{a}\n{b}" for a, b in zip(x.model_id, x.scope)], rotation=70, fontsize=7), ax.set_ylabel("host median µs (log); MCU NOT MEASURED")))

    manifest_path = ROOT / "results/xai/stage12_manifest.csv"
    records = pd.read_csv(manifest_path).to_dict("records")
    known = {r["artifact_path"] for r in records}
    for path in created:
        rel = path.relative_to(ROOT).as_posix()
        if rel not in known:
            records.append({"experiment_id": EID, "artifact_path": rel, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "rows": sum(1 for _ in path.open(encoding="utf-8")) - 1 if path.suffix == ".csv" else "", "status": "EXECUTED"})
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["experiment_id", "artifact_path", "sha256", "rows", "status"])
        writer.writeheader(); writer.writerows(records)
    print("Generated LAT-01 through LAT-09 from saved CSV evidence.")


if __name__ == "__main__":
    main()
