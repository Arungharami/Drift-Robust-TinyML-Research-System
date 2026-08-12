#!/usr/bin/env python3
"""scripts/portal/export_evidence.py — export real repository artifacts into
research-portal/data/evidence/*.json.

This is the ONLY bridge between the Python research artifacts (results/, artifacts/, configs/,
paper/) and the Next.js research portal. The web app's evidence loader (research-portal/lib/
evidence.ts) reads these files and nothing else — no metric is ever hand-typed in TypeScript.

Absolute rule: this script only ever copies/aggregates values that already exist in a saved
artifact. It never estimates, interpolates, or invents a number. Where an artifact does not
exist, the corresponding JSON field is null and evidence_status is NOT_EXECUTED.

Usage: python scripts/portal/export_evidence.py
"""
from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "research-portal" / "data" / "evidence"


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def _read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _num(v: Any) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _write(name: str, payload: Any) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(REPO_ROOT)}")


# --- dataset -------------------------------------------------------------------------------


def export_dataset() -> dict[str, Any]:
    validation = _read_json(REPO_ROOT / "results" / "reproducibility" / "dataset_validation.json")
    gate = yaml.safe_load((REPO_ROOT / "configs" / "colab.yaml").read_text(encoding="utf-8"))
    payload = {
        "evidence_status": "EXECUTED" if validation else "NOT_EXECUTED",
        "source": "UCI Gas Sensor Array Drift Dataset",
        "source_url": "https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset",
        "validation": validation,
        "artifact_path": "results/reproducibility/dataset_validation.json",
    }
    return payload


# --- experiments -----------------------------------------------------------------------------


def export_experiments() -> list[dict[str, Any]]:
    rows = _read_csv(REPO_ROOT / "results" / "registry" / "experiment_registry.csv")
    return rows


# --- baselines / metrics -----------------------------------------------------------------------


def export_baselines() -> dict[str, Any]:
    fixed_summary = _read_csv(REPO_ROOT / "results" / "baselines" / "fixed_origin_summary.csv")
    fixed_metrics = _read_csv(REPO_ROOT / "results" / "baselines" / "fixed_origin_metrics.csv")
    expanding_metrics = _read_csv(REPO_ROOT / "results" / "baselines" / "expanding_window_metrics.csv")
    iid_metrics = _read_csv(REPO_ROOT / "results" / "baselines" / "iid_diagnostic_metrics.csv")
    iid_gap = _read_csv(REPO_ROOT / "results" / "baselines" / "iid_generalization_gap.csv")
    expand_vs_fixed = _read_csv(REPO_ROOT / "results" / "baselines" / "expanding_vs_fixed.csv")
    complexity = _read_csv(REPO_ROOT / "results" / "baselines" / "model_complexity.csv")
    drift_perf_corr = _read_csv(REPO_ROOT / "results" / "baselines" / "drift_performance_correlations.csv")

    model_names = {row["model"]: row.get("model_name") for row in complexity}

    for row in fixed_summary:
        row["model_name"] = model_names.get(row["model"], row["model"])

    return {
        "evidence_status": "EXECUTED" if fixed_summary else "NOT_EXECUTED",
        "protocol_note": (
            "FIXED_ORIGIN trains once on Batch 1 and evaluates Batches 2-10 without retraining; "
            "EXPANDING_WINDOW retrains using all batches strictly before the test batch; "
            "IID_DIAGNOSTIC is an explicitly diagnostic (not primary) stratified random 80/20 split."
        ),
        "fixed_origin_summary": fixed_summary,
        "fixed_origin_by_batch": fixed_metrics,
        "expanding_window_by_batch": expanding_metrics,
        "iid_diagnostic": iid_metrics,
        "iid_generalization_gap": iid_gap,
        "expanding_vs_fixed": expand_vs_fixed,
        "model_complexity": complexity,
        "drift_performance_correlations": drift_perf_corr,
        "artifact_paths": [
            "results/baselines/fixed_origin_summary.csv",
            "results/baselines/fixed_origin_metrics.csv",
            "results/baselines/expanding_window_metrics.csv",
            "results/baselines/iid_diagnostic_metrics.csv",
            "results/baselines/iid_generalization_gap.csv",
            "results/baselines/expanding_vs_fixed.csv",
            "results/baselines/model_complexity.csv",
        ],
    }


# --- drift ------------------------------------------------------------------------------------


def export_drift() -> dict[str, Any]:
    global_drift = _read_csv(REPO_ROOT / "results" / "drift" / "global_drift_by_batch.csv")
    return {
        "evidence_status": "EXECUTED" if global_drift else "NOT_EXECUTED",
        "global_drift_by_batch": global_drift,
        "artifact_paths": ["results/drift/global_drift_by_batch.csv", "results/drift/feature_drift_by_batch.csv"],
    }


# --- claims -------------------------------------------------------------------------------------


def export_claims() -> list[dict[str, Any]]:
    return _read_csv(REPO_ROOT / "paper" / "claim_evidence_matrix.csv")


def export_references() -> list[dict[str, Any]]:
    path = REPO_ROOT / "data" / "literature" / "references.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


# --- xai (Stage 09) ------------------------------------------------------------------------------


def export_xai() -> dict[str, Any]:
    xai_dir = REPO_ROOT / "results" / "xai"
    manifest_rows = _read_csv(xai_dir / "stage09_manifest.csv")
    global_rows = _read_csv(xai_dir / "stage09_global_importance.csv")
    local_samples = _read_csv(xai_dir / "stage09_local_samples.csv")
    reduced_rows = _read_csv(xai_dir / "stage09_reduced_explanations.csv")
    fidelity_prep_rows = _read_csv(xai_dir / "stage09_fidelity_prep.csv")
    fidelity_summary = _read_csv(xai_dir / "stage10_fidelity_summary.csv")
    fidelity_ci = _read_csv(xai_dir / "stage10_bootstrap_ci.csv")
    fidelity_manifest = _read_csv(xai_dir / "stage10_manifest.csv")
    stability_summary = _read_csv(xai_dir / "stage11_stability_summary.csv")
    stability_ci = _read_csv(xai_dir / "stage11_bootstrap_ci.csv")
    stability_manifest = _read_csv(xai_dir / "stage11_manifest.csv")
    stability_local = _read_csv(xai_dir / "stage11_local_neighbor_stability.csv")
    fidelity_stability_link = _read_csv(xai_dir / "stage11_fidelity_stability_link.csv")
    latency_summary = _read_csv(xai_dir / "stage12_latency_summary.csv")
    latency_manifest = _read_csv(xai_dir / "stage12_manifest.csv")
    latency_tradeoff = _read_csv(xai_dir / "stage12_fidelity_stability_cost.csv")
    latency_claims = _read_csv(xai_dir / "stage12_claim_evaluation.csv")
    host_environment = _read_json(xai_dir / "stage12_host_environment.json")
    local_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in stability_local:
        local_groups.setdefault((row["model_id"], row["category"]), []).append(row)
    local_category_summary = [{"model_id": key[0], "category": key[1], "n": len(group), "mean_explanation_distance": sum(float(r["explanation_distance"]) for r in group)/len(group), "mean_jaccard_at_10": sum(float(r["jaccard_at_10"]) for r in group)/len(group)} for key, group in sorted(local_groups.items())]

    experiment_manifest_path = REPO_ROOT / "artifacts" / "explanations" / "EXP-XAI-0001" / "manifest.json"
    experiment_manifest = _read_json(experiment_manifest_path)

    category_counts: dict[str, int] = {}
    for row in local_samples:
        for category in row.get("category", "").split(","):
            if category:
                category_counts[category] = category_counts.get(category, 0) + 1

    # Small curated top-3 table (batch 2, every method that ran at batch scope "2" or "ALL") for
    # display without shipping all 4,864 global rows to the client.
    top3: list[dict[str, Any]] = []
    by_model_method: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in global_rows:
        if row.get("batch") not in ("2", "ALL"):
            continue
        key = (row["model_id"], row["method"], row["batch"])
        by_model_method.setdefault(key, []).append(row)
    for (model_id, method, batch), rows in sorted(by_model_method.items()):
        ranked = sorted(rows, key=lambda r: int(r["rank"]))[:3]
        top3.append(
            {
                "model_id": model_id, "method": method, "batch": batch,
                "features": [r["feature_name"] for r in ranked],
            }
        )

    return {
        "evidence_status": "EXECUTED" if experiment_manifest else "NOT_EXECUTED",
        "experiment_id": experiment_manifest.get("experiment_id") if experiment_manifest else None,
        "status": experiment_manifest.get("status") if experiment_manifest else "NOT_EXECUTED",
        "created_at": experiment_manifest.get("created_at") if experiment_manifest else None,
        "per_model_status": experiment_manifest.get("per_model_status") if experiment_manifest else {},
        "applicability_matrix": manifest_rows,
        "n_global_rows": len(global_rows),
        "n_local_samples": len(local_samples),
        "n_reduced_rows": len(reduced_rows),
        "n_fidelity_prep_rows": len(fidelity_prep_rows),
        "local_sample_categories": category_counts,
        "top3_by_model_method_batch": top3,
        "artifact_paths": [
            "results/xai/stage09_global_importance.csv",
            "results/xai/stage09_reduced_explanations.csv",
            "results/xai/stage09_local_samples.csv",
            "results/xai/stage09_local_explanations.csv",
            "results/xai/stage09_fidelity_prep.csv",
            "results/xai/stage09_manifest.csv",
            "results/xai/stage09_feature_map.csv",
            "docs/experiments/STAGE09_RESOURCE_AWARE_XAI.md",
        ],
        # Explicitly not computed by Stage 09 — later stages, still NOT_EXECUTED.
        "fidelity_status": "EXECUTED" if fidelity_manifest else "NOT_EXECUTED",
        "fidelity_experiment_id": "EXP-XAI-FIDELITY-001" if fidelity_manifest else None,
        "fidelity_summary": fidelity_summary,
        "fidelity_ci_count": len(fidelity_ci),
        "fidelity_artifact_paths": [row["artifact_path"] for row in fidelity_manifest],
        "stability_status": "EXECUTED" if stability_manifest else "NOT_EXECUTED",
        "stability_experiment_id": "EXP-XAI-STABILITY-001" if stability_manifest else None,
        "stability_summary": stability_summary,
        "stability_ci_count": len(stability_ci),
        "stability_artifact_paths": [row["artifact_path"] for row in stability_manifest],
        "stability_local_category_summary": local_category_summary,
        "fidelity_stability_link": fidelity_stability_link,
        "latency_status": "EXECUTED" if latency_manifest else "NOT_EXECUTED",
        "latency_experiment_id": "EXP-XAI-LATENCY-001" if latency_manifest else None,
        "latency_summary": latency_summary,
        "latency_tradeoff": latency_tradeoff,
        "latency_claims": latency_claims,
        "latency_environment": host_environment,
        "latency_artifact_paths": [row["artifact_path"] for row in latency_manifest],
        "mcu_cost_status": "NOT_MEASURED",
    }


# --- pipeline -----------------------------------------------------------------------------------


def export_pipeline() -> list[dict[str, Any]]:
    doc = yaml.safe_load((REPO_ROOT / "configs" / "pipeline_stages.yaml").read_text(encoding="utf-8"))
    return doc["stages"]


# --- figures/tables index ------------------------------------------------------------------------


def export_figures() -> list[dict[str, Any]]:
    figures_dir = REPO_ROOT / "results" / "figures"
    if not figures_dir.exists():
        return []
    out = []
    for svg in sorted(figures_dir.glob("*.svg")):
        stem = svg.stem
        source_csv = figures_dir / "sources" / f"{stem}.csv"
        out.append(
            {
                "id": stem,
                "svg_path": f"results/figures/{svg.name}",
                "png_path": f"results/figures/{stem}.png",
                "source_csv": f"results/figures/sources/{stem}.csv" if source_csv.exists() else None,
            }
        )
    return out


def export_tables() -> list[dict[str, Any]]:
    tables_dir = REPO_ROOT / "results" / "tables"
    if not tables_dir.exists():
        return []
    out = []
    for md in sorted(tables_dir.glob("*.md")):
        stem = md.stem
        out.append(
            {
                "id": stem,
                "markdown_path": f"results/tables/{md.name}",
                "csv_path": f"results/tables/{stem}.csv",
            }
        )
    return out


# --- platform bridge (copy-through from the already-real bridge artifacts) ---------------------


def export_platform() -> dict[str, Any]:
    bridge_dir = REPO_ROOT / "results" / "reproducibility" / "bridge"
    return {
        "github": _read_json(bridge_dir / "github_status.json"),
        "huggingface": _read_json(bridge_dir / "huggingface_status.json"),
        "kaggle": _read_json(bridge_dir / "kaggle_status.json"),
        "platform_manifest": _read_json(bridge_dir / "platform_manifest.json"),
    }


# --- environment ----------------------------------------------------------------------------------


def export_environment() -> dict[str, Any] | None:
    return _read_json(REPO_ROOT / "results" / "reproducibility" / "environment.json")


def export_embedded() -> dict[str, Any]:
    embedded = REPO_ROOT / "results" / "embedded"
    budget = yaml.safe_load((REPO_ROOT / "configs/nrf52840_resource_budget.yaml").read_text(encoding="utf-8"))
    decision = _read_csv(embedded / "stage13_decision.csv")
    stage14_summary = _read_json(embedded / "stage14_summary.json")
    return {
        "gate_id": "GATE-EMBED-EXPORT-001",
        "protocol_status": "PROTOCOL_FROZEN" if decision else "NOT_EXECUTED",
        "target": budget["target"],
        "model_inventory": _read_csv(embedded / "stage13_model_inventory.csv"),
        "candidates": _read_csv(embedded / "stage13_candidate_matrix.csv"),
        "analytical_memory": _read_csv(embedded / "stage13_analytical_memory.csv"),
        "decision": decision,
        "fp32_summary": stage14_summary,
        "fp32_claims": _read_csv(embedded / "stage14_claim_evaluation.csv"),
        "fp32_storage": _read_csv(embedded / "stage14_export_storage.csv"),
        "fp32_manifest": _read_csv(embedded / "stage14_manifest.csv"),
        "statuses": {"model_export": "NOT_EXECUTED", "quantization": "NOT_EXECUTED", "firmware": "NOT_EXECUTED", "compiled_flash": "NOT_MEASURED", "sram": "NOT_MEASURED", "mcu_latency": "NOT_MEASURED", "energy": "NOT_MEASURED"},
        "artifact_paths": ["docs/embedded/STAGE13_EMBEDDED_EXPORT_PROTOCOL.md", "configs/embedded_equivalence_protocol.yaml", "results/embedded/stage13_candidate_matrix.csv", "data/manifests/embedded_golden_vectors.csv", "docs/embedded/STAGE14_FP32_EXPORT_EQUIVALENCE.md", "results/embedded/stage14_summary.json", "results/embedded/stage14_manifest.csv"],
    }


def export_research_intelligence() -> dict[str, Any]:
    """Copy only generated/registered evidence into cockpit-facing JSON."""
    registry = REPO_ROOT / "results" / "registry"
    feature_rows = _read_csv(REPO_ROOT / "research" / "feature_metadata.csv")
    decisions = _read_csv(REPO_ROOT / "results" / "decisions" / "research_decisions.csv")
    experiments = _read_csv(registry / "experiments.csv")
    measurements = _read_csv(registry / "measurements.csv")
    artifacts = _read_csv(registry / "artifacts.csv")
    claims = _read_csv(registry / "claims.csv")
    fixed = _read_csv(REPO_ROOT / "results" / "baselines" / "fixed_origin_metrics.csv")
    class_perf = _read_csv(REPO_ROOT / "results" / "baselines" / "class_performance_by_batch.csv")
    return {
        "evidence_status": "EXECUTED" if experiments and artifacts else "BLOCKED",
        "registries": {"experiments": experiments, "measurements": measurements, "artifacts": artifacts, "claims": claims, "decisions": decisions},
        "feature_structure": {"physical_sensors": len({r.get('sensor_id') for r in feature_rows}), "features_per_sensor": 8 if len(feature_rows) == 128 else None, "feature_count": len(feature_rows), "metadata_artifact": "research/feature_metadata.csv"},
        "failure_rows": fixed,
        "class_failure_rows": class_perf,
        "hardware_blocker": "No nRF52840 firmware measurement or PPK2 trace is registered.",
        "next_experiment": "EMBEDDED_EXPORT_PROTOCOL_PREREGISTRATION" if (REPO_ROOT / "results/xai/stage12_manifest.csv").exists() else "EXP-XAI-LATENCY-001" if (REPO_ROOT / "results/xai/stage11_manifest.csv").exists() else "EXP-XAI-STABILITY-001" if (REPO_ROOT / "results/xai/stage10_manifest.csv").exists() else "EXP-XAI-FIDELITY-001",
    }


# --- project status rollup (feeds /api/project-status) ---------------------------------------------


def export_project_status(pipeline: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for stage in pipeline:
        counts[stage["status"]] = counts.get(stage["status"], 0) + 1
    return {
        "project": "Drift-Robust Explainable TinyML for Electronic-Nose Sensing",
        "repository": "Arungharami/Drift-Robust-TinyML-Research-System",
        "branch": _git("branch", "--show-current"),
        "git_commit": _git("rev-parse", "HEAD"),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pipeline_stage_counts": counts,
        "pipeline_total_stages": len(pipeline),
        "hardware_state": "NOT_EXECUTED",
        "paper_state": "DRAFT_EVIDENCE_ONLY",
    }


def main() -> int:
    dataset = export_dataset()
    experiments = export_experiments()
    baselines = export_baselines()
    drift = export_drift()
    claims = export_claims()
    references = export_references()
    xai = export_xai()
    pipeline = export_pipeline()
    figures = export_figures()
    tables = export_tables()
    platform = export_platform()
    environment = export_environment()
    project_status = export_project_status(pipeline)
    intelligence = export_research_intelligence()
    embedded = export_embedded()

    _write("dataset.json", dataset)
    _write("experiments.json", experiments)
    _write("baselines.json", baselines)
    _write("drift.json", drift)
    _write("claims.json", claims)
    _write("references.json", references)
    _write("xai.json", xai)
    _write("pipeline.json", pipeline)
    _write("figures.json", figures)
    _write("tables.json", tables)
    _write("platform.json", platform)
    _write("environment.json", environment)
    _write("project-status.json", project_status)
    _write("research-intelligence.json", intelligence)
    _write("embedded.json", embedded)

    print(f"\nExported {len(list(OUT_DIR.glob('*.json')))} evidence files to {OUT_DIR.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
