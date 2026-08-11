"""Stage 09 headless runner — resource-aware explainability.

Usage:
    python -m src.xai.run_stage09 --config configs/xai/stage09_resource_aware_xai_v1.yaml

Loads the frozen, already-fitted FIXED_ORIGIN model artifacts (no retraining), generates
intrinsic / permutation / local-ablation explanations per the frozen protocol, and saves every
artifact the mission's Stage 09 spec requires. A missing model or an inapplicable method never
aborts the whole run — see FAILURE RULE in docs/experiments/STAGE09_RESOURCE_AWARE_XAI.md.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.data.loader import load_batch  # noqa: E402
from src.utils.reproducibility import capture_environment  # noqa: E402
from src.utils.registry import append_experiment  # noqa: E402
from src.xai import feature_map as feature_map_mod  # noqa: E402
from src.xai import manifest as manifest_mod  # noqa: E402
from src.xai import schema  # noqa: E402
from src.xai.base import NotApplicableError  # noqa: E402
from src.xai.intrinsic import build_intrinsic_explainers  # noqa: E402
from src.xai.local_ablation import SingleFeatureAblationExplainer  # noqa: E402
from src.xai.permutation import PermutationImportanceExplainer  # noqa: E402
from src.xai.sampling import select_local_samples  # noqa: E402


def next_experiment_id(artifact_root: Path) -> str:
    existing = sorted(p.name for p in artifact_root.glob("EXP-XAI-*") if p.is_dir()) if artifact_root.exists() else []
    numbers = [int(m.group(1)) for name in existing if (m := re.match(r"EXP-XAI-(\d+)$", name))]
    return f"EXP-XAI-{(max(numbers) + 1) if numbers else 1:04d}"


def load_config(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_all_batches(batch_ids: list[int]) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    raw_dir = REPO_ROOT / "data" / "raw"
    from src.data.loader import batch_number, discover_batches

    all_paths = {batch_number(p): p for p in discover_batches(raw_dir)}
    return {b: load_batch(all_paths[b]) for b in batch_ids if b in all_paths}


def run_stage09(config_path: Path, dry_run: bool = False) -> dict[str, Any]:
    config = load_config(config_path)
    artifact_root = REPO_ROOT / config["output_paths"]["artifact_root"]
    results_root = REPO_ROOT / config["output_paths"]["results_root"]
    experiment_id = next_experiment_id(artifact_root)
    experiment_dir = artifact_root / experiment_id
    seed = int(config["random_seed"])
    top_k_values = tuple(config["top_k_values"])

    print(f"[stage09] experiment_id={experiment_id}")
    if dry_run:
        return {"experiment_id": experiment_id, "status": "DRY_RUN", "models": {}}

    experiment_dir.mkdir(parents=True, exist_ok=True)
    (experiment_dir / "logs").mkdir(exist_ok=True)
    (experiment_dir / "global").mkdir(exist_ok=True)
    (experiment_dir / "local").mkdir(exist_ok=True)
    (experiment_dir / "reduced").mkdir(exist_ok=True)

    manifest_mod.write_json(experiment_dir / "config.json", config)
    (experiment_dir / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    environment = capture_environment(experiment_dir / "environment.json", seed=seed)

    feature_rows = feature_map_mod.write_feature_map(results_root / "stage09_feature_map.csv")
    (experiment_dir / "feature_map.csv").write_bytes((results_root / "stage09_feature_map.csv").read_bytes())
    feature_names = feature_map_mod.display_names(feature_rows)
    n_features = len(feature_names)

    train_batches = config["train_batches"]
    eval_batches = config["evaluation_batches"]
    local_sample_batches = config["sample_policy"]["local_sample_batches"]
    needed_batches = sorted(set(train_batches) | set(eval_batches) | set(local_sample_batches))
    data = load_all_batches(needed_batches)
    x_train, y_train = data[train_batches[0]]  # FIXED_ORIGIN trains on batch 1 only
    ablation_baseline = x_train.mean(axis=0)  # legitimate baseline: training-split statistics only

    global_rows: list[dict[str, Any]] = []
    reduced_rows: list[dict[str, Any]] = []
    local_sample_rows: list[dict[str, Any]] = []
    local_explanation_rows: list[dict[str, Any]] = []
    fidelity_prep_rows: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    per_model_status: dict[str, Any] = {}
    logs: list[str] = []

    for model_id in config["eligible_model_ids"]:
        artifact_path = REPO_ROOT / config["model_artifact_paths"][model_id]
        log = lambda msg: (logs.append(f"[{model_id}] {msg}"), print(f"[stage09][{model_id}] {msg}"))  # noqa: E731

        if not artifact_path.exists():
            log(f"FAILED: model artifact not found at {artifact_path}")
            per_model_status[model_id] = {"status": "FAILED", "reason": f"missing artifact {artifact_path}"}
            continue

        try:
            pipeline = joblib.load(artifact_path)
        except Exception as exc:  # noqa: BLE001 — a load failure here must not abort the whole run
            log(f"FAILED: could not load artifact: {exc}")
            per_model_status[model_id] = {"status": "FAILED", "reason": str(exc)}
            continue

        (experiment_dir / "global" / model_id).mkdir(parents=True, exist_ok=True)
        (experiment_dir / "local" / model_id).mkdir(parents=True, exist_ok=True)
        (experiment_dir / "reduced" / model_id).mkdir(parents=True, exist_ok=True)

        model_global_rows: list[dict[str, Any]] = []

        # --- intrinsic (global + local where applicable) ---------------------------------
        intrinsic_explainers = build_intrinsic_explainers(pipeline, model_id)
        for explainer in intrinsic_explainers:
            if explainer.supports_global:
                try:
                    result = explainer.explain_global()
                    rows = schema.build_global_importance_rows(
                        experiment_id=experiment_id, model_id=model_id, method=explainer.method_name,
                        batch="ALL", importance=result["importance"], importance_std=None,
                        feature_names=feature_names,
                    )
                    model_global_rows.extend(rows)
                    manifest_rows.append({"experiment_id": experiment_id, "model_id": model_id, "method": explainer.method_name, "scope": "global", "status": "EXECUTED", "reason": ""})
                    log(f"{explainer.method_name} global: EXECUTED")
                except NotApplicableError as exc:
                    manifest_rows.append({"experiment_id": experiment_id, "model_id": model_id, "method": explainer.method_name, "scope": "global", "status": "NOT_APPLICABLE", "reason": str(exc)})
            else:
                manifest_rows.append({"experiment_id": experiment_id, "model_id": model_id, "method": explainer.method_name, "scope": "global", "status": "NOT_APPLICABLE", "reason": "capability not detected"})

        applied_methods = {e.method_name for e in intrinsic_explainers}
        for missing_method in ("INTRINSIC_COEFFICIENT", "INTRINSIC_IMPURITY"):
            if missing_method not in applied_methods:
                manifest_rows.append({"experiment_id": experiment_id, "model_id": model_id, "method": missing_method, "scope": "global", "status": "NOT_APPLICABLE", "reason": "capability not detected on fitted estimator"})

        # --- permutation importance (global, per batch) -----------------------------------
        n_repeats = int(config["permutation_repeats"])
        for batch_id in eval_batches:
            if batch_id not in data:
                continue
            x_batch, y_batch = data[batch_id]
            explainer = PermutationImportanceExplainer(pipeline, model_id, n_repeats=n_repeats, seed=seed)
            result = explainer.explain_global(x=x_batch, y=y_batch)
            rows = schema.build_global_importance_rows(
                experiment_id=experiment_id, model_id=model_id, method=explainer.method_name,
                batch=str(batch_id), importance=result["importance"], importance_std=result["importance_std"],
                feature_names=feature_names,
            )
            model_global_rows.extend(rows)
            batch_csv = experiment_dir / "global" / model_id / f"batch_{batch_id:02d}_importance.csv"
            _write_csv(batch_csv, rows, schema.GLOBAL_IMPORTANCE_COLUMNS)
        manifest_rows.append({"experiment_id": experiment_id, "model_id": model_id, "method": "PERMUTATION_IMPORTANCE_MACRO_F1", "scope": "global", "status": "EXECUTED", "reason": ""})
        log(f"PERMUTATION_IMPORTANCE_MACRO_F1 global: EXECUTED ({len(eval_batches)} batches, {n_repeats} repeats)")

        global_rows.extend(model_global_rows)
        _write_csv(experiment_dir / "global" / model_id / "global_importance.csv", model_global_rows, schema.GLOBAL_IMPORTANCE_COLUMNS)

        # --- reduced (resource-aware top-k) representations --------------------------------
        for (method, batch), group in _group_by(model_global_rows, ("method", "batch")):
            importance = [0.0] * n_features
            for row in group:
                importance[row["feature_index"] - 1] = row["importance"]
            rows = schema.build_reduced_rows(
                experiment_id=experiment_id, model_id=model_id, method=method, batch=batch,
                importance=importance, feature_names=feature_names, top_k_values=top_k_values,
            )
            reduced_rows.extend(rows)
            for k in top_k_values:
                k_rows = [r for r in rows if r["top_k"] == k]
                if not k_rows:
                    continue
                out = experiment_dir / "reduced" / model_id / f"top_{k}.json" if batch == "ALL" else experiment_dir / "reduced" / model_id / f"batch_{batch}_top_{k}.json"
                manifest_mod.write_json(out, k_rows)

        # --- local explanations -------------------------------------------------------------
        predictions = _predict_frame(pipeline, data, local_sample_batches)
        samples = select_local_samples(
            predictions, seed=config["sample_policy"]["seed"],
            per_class_correct=config["sample_policy"]["per_class_correct"],
            max_misclassified=config["sample_policy"]["max_misclassified"],
            max_near_boundary=config["sample_policy"]["max_near_boundary"],
        )
        sample_records = []
        for _, row in samples.iterrows():
            sample_id = f"B{int(row['batch'])}:{int(row['row_index'])}"
            sample_records.append({
                "experiment_id": experiment_id, "sample_id": sample_id, "model_id": model_id,
                "batch": int(row["batch"]), "row_index_in_batch": int(row["row_index"]),
                "true_label": int(row["true_label"]), "predicted_label": int(row["predicted_label"]),
                "correct": bool(row["correct"]), "prediction_margin": float(row["prediction_margin"]) if pd.notna(row["prediction_margin"]) else None,
                "category": row["category"],
            })
        local_sample_rows.extend(sample_records)
        _write_csv(experiment_dir / "local" / model_id / "selected_samples.csv", sample_records, schema.LOCAL_SAMPLE_COLUMNS)

        ablation = SingleFeatureAblationExplainer(pipeline, model_id, baseline=ablation_baseline)
        coefficient_local = next((e for e in intrinsic_explainers if e.method_name == "INTRINSIC_COEFFICIENT" and e.supports_local), None)

        model_local_rows: list[dict[str, Any]] = []
        for record, (_, row) in zip(sample_records, samples.iterrows()):
            batch_id = int(row["batch"])
            x_row = data[batch_id][0][int(row["row_index"])]

            ablation_result = ablation.explain_local(x_row)
            ranks = schema.rank_from_importance([abs(c) for c in ablation_result["feature_contributions"]])
            for i, contribution in enumerate(ablation_result["feature_contributions"]):
                model_local_rows.append({
                    "experiment_id": experiment_id, "sample_id": record["sample_id"], "model_id": model_id,
                    "method": ablation.method_name, "feature_index": i + 1, "feature_name": feature_names[i],
                    "contribution": contribution, "rank": ranks[i],
                })

            reference_ranked = [i + 1 for i in sorted(range(n_features), key=lambda i: -abs(ablation_result["feature_contributions"][i]))]
            if coefficient_local is not None:
                coef_result = coefficient_local.explain_local(x_row)
                coef_ranked = [i + 1 for i in sorted(range(n_features), key=lambda i: -abs(coef_result["feature_contributions"][i]))]
                for i, contribution in enumerate(coef_result["feature_contributions"]):
                    model_local_rows.append({
                        "experiment_id": experiment_id, "sample_id": record["sample_id"], "model_id": model_id,
                        "method": coefficient_local.method_name, "feature_index": i + 1, "feature_name": feature_names[i],
                        "contribution": contribution, "rank": schema.rank_from_importance([abs(c) for c in coef_result["feature_contributions"]])[i],
                    })
                candidate_method, candidate_full = coefficient_local.method_name, coef_ranked
            else:
                candidate_method, candidate_full = ablation.method_name, reference_ranked

            # reference_features is the FULL reference ranking (never truncated to k) so Stage 10
            # can measure how much a top-k CANDIDATE actually loses relative to the complete
            # explanation — truncating both to the same k would make every row trivially identical.
            for k in top_k_values:
                fidelity_prep_rows.append({
                    "experiment_id": experiment_id, "sample_id": record["sample_id"], "model_id": model_id,
                    "reference_method": ablation.method_name, "candidate_method": candidate_method, "top_k": k,
                    "reference_features": json.dumps(reference_ranked), "candidate_features": json.dumps(candidate_full[:k]),
                })

        local_explanation_rows.extend(model_local_rows)
        _write_csv(experiment_dir / "local" / model_id / "explanations.csv", model_local_rows, schema.LOCAL_EXPLANATION_COLUMNS)
        manifest_rows.append({"experiment_id": experiment_id, "model_id": model_id, "method": "SINGLE_FEATURE_ABLATION_LOCAL", "scope": "local", "status": "EXECUTED" if sample_records else "NOT_EXECUTED", "reason": "" if sample_records else "no local samples selected"})
        if coefficient_local is None:
            manifest_rows.append({"experiment_id": experiment_id, "model_id": model_id, "method": "INTRINSIC_COEFFICIENT", "scope": "local", "status": "NOT_APPLICABLE", "reason": "capability not detected on fitted estimator"})
        else:
            manifest_rows.append({"experiment_id": experiment_id, "model_id": model_id, "method": "INTRINSIC_COEFFICIENT", "scope": "local", "status": "EXECUTED", "reason": ""})

        log(f"local explanations: {len(sample_records)} samples")
        per_model_status[model_id] = {"status": "EXECUTED", "n_local_samples": len(sample_records), "n_global_rows": len(model_global_rows)}

        model_manifest = manifest_mod.build_manifest(
            experiment_id=f"{experiment_id}-{model_id}", status="EXECUTED",
            dataset_hash=config["dataset_hash"], split_protocol=config["split_protocol"], model_id=model_id,
            source_model_experiment_id=config["source_experiment_ids"][model_id], model_artifact_path=artifact_path,
            explainer_methods=sorted({r["method"] for r in manifest_rows if r["model_id"] == model_id}),
            random_seed=seed,
            input_artifacts=[str(artifact_path.relative_to(REPO_ROOT)), config["dataset_manifest"]],
            output_artifacts=[str((experiment_dir / "global" / model_id).relative_to(REPO_ROOT)), str((experiment_dir / "local" / model_id).relative_to(REPO_ROOT)), str((experiment_dir / "reduced" / model_id).relative_to(REPO_ROOT))],
            notes=f"Stage 09 explanations for {model_id}, loaded from frozen FIXED_ORIGIN artifact; no retraining.",
        )
        manifest_mod.write_json(experiment_dir / "logs" / f"{model_id}_manifest.json", model_manifest)

    overall_status = "EXECUTED" if any(v.get("status") == "EXECUTED" for v in per_model_status.values()) else "FAILED"

    _write_csv(results_root / "stage09_global_importance.csv", global_rows, schema.GLOBAL_IMPORTANCE_COLUMNS)
    _write_csv(results_root / "stage09_reduced_explanations.csv", reduced_rows, schema.REDUCED_EXPLANATION_COLUMNS)
    _write_csv(results_root / "stage09_local_samples.csv", local_sample_rows, schema.LOCAL_SAMPLE_COLUMNS)
    _write_csv(results_root / "stage09_local_explanations.csv", local_explanation_rows, schema.LOCAL_EXPLANATION_COLUMNS)
    _write_csv(results_root / "stage09_fidelity_prep.csv", fidelity_prep_rows, schema.FIDELITY_PREP_COLUMNS)
    _write_csv(results_root / "stage09_manifest.csv", manifest_rows, schema.MANIFEST_ROW_COLUMNS)
    (experiment_dir / "logs" / "run.log").write_text("\n".join(logs) + "\n", encoding="utf-8")

    top_level_manifest = {
        "experiment_id": experiment_id,
        "stage": "09",
        "status": overall_status,
        "created_at": environment["timestamp_utc"],
        "git_commit": environment["git_commit"],
        "config_path": str(config_path.relative_to(REPO_ROOT)),
        "config_hash": manifest_mod.config_hash(config),
        "per_model_status": per_model_status,
        "n_global_rows": len(global_rows),
        "n_reduced_rows": len(reduced_rows),
        "n_local_samples": len(local_sample_rows),
        "n_local_explanation_rows": len(local_explanation_rows),
        "n_fidelity_prep_rows": len(fidelity_prep_rows),
        "output_artifacts": [str(results_root.relative_to(REPO_ROOT) / f) for f in (
            "stage09_feature_map.csv", "stage09_global_importance.csv", "stage09_reduced_explanations.csv",
            "stage09_local_samples.csv", "stage09_local_explanations.csv", "stage09_fidelity_prep.csv", "stage09_manifest.csv",
        )],
    }
    manifest_mod.write_json(experiment_dir / "manifest.json", top_level_manifest)
    print(f"[stage09] status={overall_status} experiment_id={experiment_id}")
    return top_level_manifest


def _predict_frame(pipeline: Any, data: dict[int, tuple[np.ndarray, np.ndarray]], batches: list[int]) -> pd.DataFrame:
    rows = []
    for batch_id in batches:
        if batch_id not in data:
            continue
        x, y = data[batch_id]
        predicted = pipeline.predict(x)
        proba = pipeline.predict_proba(x) if hasattr(pipeline, "predict_proba") else None
        for i in range(len(y)):
            record = {
                "batch": batch_id, "row_index": i, "true_label": int(y[i]), "predicted_label": int(predicted[i]),
                "correct": bool(predicted[i] == y[i]),
            }
            if proba is not None:
                for class_index, label in enumerate(pipeline.classes_):
                    record[f"probability_class_{label}"] = float(proba[i, class_index])
            rows.append(record)
    return pd.DataFrame(rows)


def _group_by(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> list[tuple[tuple[str, ...], list[dict[str, Any]]]]:
    groups: dict[tuple, list[dict[str, Any]]] = {}
    for row in rows:
        key = tuple(row[k] for k in keys)
        groups.setdefault(key, []).append(row)
    return list(groups.items())


def _write_csv(path: Path, rows: list[dict[str, Any]], columns: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "configs/xai/stage09_resource_aware_xai_v1.yaml")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run_stage09(args.config.resolve(), dry_run=args.dry_run)
    return 0 if result["status"] in ("EXECUTED", "DRY_RUN") else 1


if __name__ == "__main__":
    raise SystemExit(main())
