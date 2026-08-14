"""Stage 10 headless runner: behavioral fidelity of Stage 09 top-k explanations.

Usage:
    python -m src.xai.run_stage10 --config configs/xai/stage10_fidelity_v1.yaml
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.data.loader import batch_number, discover_batches, load_batch  # noqa: E402
from src.utils.hashing import sha256_file, stable_hash  # noqa: E402
from src.utils.reproducibility import capture_environment  # noqa: E402
from src.xai.fidelity import evaluate_fidelity  # noqa: E402
from src.xai.manifest import write_json  # noqa: E402

IDENTITY_COLUMNS = [
    "experiment_id",
    "source_experiment_id",
    "sample_id",
    "batch",
    "row_index_in_batch",
    "model_id",
    "reference_method",
    "candidate_method",
]
METRIC_COLUMNS = [
    "top_k",
    "rank_overlap_at_k",
    "full_predicted_class",
    "full_target_probability",
    "candidate_prediction_preserved",
    "candidate_keep_predicted_class",
    "candidate_delete_predicted_class",
    "candidate_keep_target_probability",
    "candidate_delete_target_probability",
    "candidate_probability_closeness",
    "candidate_sufficiency_gap",
    "candidate_absolute_sufficiency_gap",
    "candidate_comprehensiveness_drop",
    "reference_prediction_preserved",
    "reference_keep_predicted_class",
    "reference_delete_predicted_class",
    "reference_keep_target_probability",
    "reference_delete_target_probability",
    "reference_probability_closeness",
    "reference_sufficiency_gap",
    "reference_absolute_sufficiency_gap",
    "reference_comprehensiveness_drop",
    "candidate_minus_reference_probability_closeness",
    "candidate_minus_reference_absolute_sufficiency_gap",
    "candidate_minus_reference_comprehensiveness_drop",
]
PER_SAMPLE_COLUMNS = IDENTITY_COLUMNS + METRIC_COLUMNS
SUMMARY_COLUMNS = [
    "experiment_id",
    "source_experiment_id",
    "model_id",
    "candidate_method",
    "reference_method",
    "top_k",
    "n_samples",
    "mean_rank_overlap_at_k",
    "candidate_prediction_preservation_rate",
    "reference_prediction_preservation_rate",
    "mean_candidate_probability_closeness",
    "std_candidate_probability_closeness",
    "mean_reference_probability_closeness",
    "mean_candidate_absolute_sufficiency_gap",
    "std_candidate_absolute_sufficiency_gap",
    "mean_reference_absolute_sufficiency_gap",
    "mean_candidate_comprehensiveness_drop",
    "std_candidate_comprehensiveness_drop",
    "mean_reference_comprehensiveness_drop",
    "mean_candidate_minus_reference_probability_closeness",
    "mean_candidate_minus_reference_absolute_sufficiency_gap",
    "mean_candidate_minus_reference_comprehensiveness_drop",
]


def _load_config(path: Path) -> dict[str, Any]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    required = {
        "protocol_version",
        "experiment_id",
        "source_experiment_id",
        "dataset_hash",
        "split_protocol",
        "train_batch",
        "top_k_values",
        "eligible_model_ids",
        "model_artifact_paths",
        "input_paths",
        "output_paths",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Stage 10 config is missing keys: {missing}")
    if sorted(int(value) for value in config["top_k_values"]) != sorted({int(value) for value in config["top_k_values"]}):
        raise ValueError("top_k_values must be unique")
    return config


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def _parse_sample_id(sample_id: str) -> tuple[int, int]:
    try:
        batch_text, row_text = sample_id.removeprefix("B").split(":", 1)
        batch_id, row_index = int(batch_text), int(row_text)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"Invalid Stage 09 sample_id: {sample_id!r}") from exc
    if batch_id <= 0 or row_index < 0:
        raise ValueError(f"Invalid Stage 09 sample_id: {sample_id!r}")
    return batch_id, row_index


def _parse_features(value: str, field: str) -> list[int]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field} is not valid JSON") from exc
    if not isinstance(parsed, list):
        raise ValueError(f"{field} must be a JSON list")
    return [int(item) for item in parsed]


def _load_batches(batch_ids: set[int]) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    raw_dir = REPO_ROOT / "data" / "raw"
    available = {batch_number(path): path for path in discover_batches(raw_dir)}
    missing = sorted(batch_ids - set(available))
    if missing:
        raise FileNotFoundError(f"Missing chronological dataset batches: {missing}")
    return {batch_id: load_batch(available[batch_id]) for batch_id in sorted(batch_ids)}


def summarize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []
    frame = pd.DataFrame(rows)
    group_columns = [
        "experiment_id",
        "source_experiment_id",
        "model_id",
        "candidate_method",
        "reference_method",
        "top_k",
    ]
    summary: list[dict[str, Any]] = []
    for keys, group in frame.groupby(group_columns, sort=True, dropna=False):
        values = dict(zip(group_columns, keys))
        std = lambda column: float(group[column].std(ddof=1)) if len(group) > 1 else 0.0  # noqa: E731
        values.update(
            {
                "n_samples": int(len(group)),
                "mean_rank_overlap_at_k": float(group["rank_overlap_at_k"].mean()),
                "candidate_prediction_preservation_rate": float(group["candidate_prediction_preserved"].mean()),
                "reference_prediction_preservation_rate": float(group["reference_prediction_preserved"].mean()),
                "mean_candidate_probability_closeness": float(group["candidate_probability_closeness"].mean()),
                "std_candidate_probability_closeness": std("candidate_probability_closeness"),
                "mean_reference_probability_closeness": float(group["reference_probability_closeness"].mean()),
                "mean_candidate_absolute_sufficiency_gap": float(group["candidate_absolute_sufficiency_gap"].mean()),
                "std_candidate_absolute_sufficiency_gap": std("candidate_absolute_sufficiency_gap"),
                "mean_reference_absolute_sufficiency_gap": float(group["reference_absolute_sufficiency_gap"].mean()),
                "mean_candidate_comprehensiveness_drop": float(group["candidate_comprehensiveness_drop"].mean()),
                "std_candidate_comprehensiveness_drop": std("candidate_comprehensiveness_drop"),
                "mean_reference_comprehensiveness_drop": float(group["reference_comprehensiveness_drop"].mean()),
                "mean_candidate_minus_reference_probability_closeness": float(
                    group["candidate_minus_reference_probability_closeness"].mean()
                ),
                "mean_candidate_minus_reference_absolute_sufficiency_gap": float(
                    group["candidate_minus_reference_absolute_sufficiency_gap"].mean()
                ),
                "mean_candidate_minus_reference_comprehensiveness_drop": float(
                    group["candidate_minus_reference_comprehensiveness_drop"].mean()
                ),
            }
        )
        summary.append(values)
    return summary


def run_stage10(config_path: Path) -> dict[str, Any]:
    config = _load_config(config_path)
    experiment_id = str(config["experiment_id"])
    source_experiment_id = str(config["source_experiment_id"])
    artifact_dir = REPO_ROOT / config["output_paths"]["artifact_dir"]
    per_sample_path = REPO_ROOT / config["output_paths"]["per_sample"]
    summary_path = REPO_ROOT / config["output_paths"]["summary"]
    prep_path = REPO_ROOT / config["input_paths"]["fidelity_prep"]
    expected_top_k = {int(value) for value in config["top_k_values"]}
    expected_models = set(config["eligible_model_ids"])

    prep_rows = _read_csv(prep_path)
    if not prep_rows:
        raise ValueError("Stage 09 fidelity preparation artifact is empty")
    observed_models = {row["model_id"] for row in prep_rows}
    observed_top_k = {int(row["top_k"]) for row in prep_rows}
    if observed_models != expected_models:
        raise ValueError(f"Stage 09 model set mismatch: {sorted(observed_models)}")
    if observed_top_k != expected_top_k:
        raise ValueError(f"Stage 09 top-k set mismatch: {sorted(observed_top_k)}")
    expected_rows = config.get("expected_per_sample_rows")
    if expected_rows is not None and len(prep_rows) != int(expected_rows):
        raise ValueError(f"Expected {expected_rows} Stage 09 rows, found {len(prep_rows)}")

    sample_locations = {_parse_sample_id(row["sample_id"]) for row in prep_rows}
    needed_batches = {int(config["train_batch"])} | {batch_id for batch_id, _ in sample_locations}
    batches = _load_batches(needed_batches)
    baseline = batches[int(config["train_batch"])][0].mean(axis=0)

    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifact_dir / "config.json", config)
    (artifact_dir / "config.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    environment = capture_environment(
        artifact_dir / "environment.json", seed=int(config.get("random_seed", 42))
    )

    output_rows: list[dict[str, Any]] = []
    logs: list[str] = []
    models: dict[str, Any] = {}
    for model_id in sorted(expected_models):
        model_path = REPO_ROOT / config["model_artifact_paths"][model_id]
        if not model_path.exists():
            raise FileNotFoundError(f"Missing frozen model artifact: {model_path}")
        model = joblib.load(model_path)
        if not hasattr(model, "predict_proba"):
            raise TypeError(f"{model_id} does not expose predict_proba")
        models[model_id] = model
        logs.append(f"[{model_id}] loaded {model_path.relative_to(REPO_ROOT)}")

    for prep in prep_rows:
        model_id = prep["model_id"]
        batch_id, row_index = _parse_sample_id(prep["sample_id"])
        x_batch = batches[batch_id][0]
        if row_index >= len(x_batch):
            raise IndexError(f"{prep['sample_id']} exceeds batch {batch_id} row count")
        top_k = int(prep["top_k"])
        candidate = _parse_features(prep["candidate_features"], "candidate_features")
        reference = _parse_features(prep["reference_features"], "reference_features")
        metrics = evaluate_fidelity(
            models[model_id],
            x_batch[row_index],
            baseline,
            candidate,
            reference,
            top_k,
        )
        identity = {
            "experiment_id": experiment_id,
            "source_experiment_id": source_experiment_id,
            "sample_id": prep["sample_id"],
            "batch": batch_id,
            "row_index_in_batch": row_index,
            "model_id": model_id,
            "reference_method": prep["reference_method"],
            "candidate_method": prep["candidate_method"],
        }
        output_rows.append({**identity, **metrics})

    output_rows.sort(key=lambda row: (row["model_id"], row["sample_id"], row["top_k"]))
    summary_rows = summarize_rows(output_rows)
    expected_summary_rows = config.get("expected_summary_rows")
    if expected_summary_rows is not None and len(summary_rows) != int(expected_summary_rows):
        raise ValueError(f"Expected {expected_summary_rows} summary rows, found {len(summary_rows)}")
    _write_csv(per_sample_path, output_rows, PER_SAMPLE_COLUMNS)
    _write_csv(summary_path, summary_rows, SUMMARY_COLUMNS)
    (artifact_dir / "run.log").write_text(
        "\n".join(logs + [f"[stage10] evaluated_rows={len(output_rows)}"]) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "experiment_id": experiment_id,
        "stage": "10",
        "status": "EXECUTED",
        "created_at": environment["timestamp_utc"],
        "git_commit": environment["git_commit"],
        "protocol_version": config["protocol_version"],
        "config_hash": stable_hash(config),
        "dataset_hash": config["dataset_hash"],
        "split_protocol": config["split_protocol"],
        "source_experiment_id": source_experiment_id,
        "n_per_sample_rows": len(output_rows),
        "n_summary_rows": len(summary_rows),
        "models": sorted(expected_models),
        "top_k_values": sorted(expected_top_k),
        "interpretation": "Descriptive metrics only; no preregistered pass/fail threshold.",
        "input_artifacts": {
            str(prep_path.relative_to(REPO_ROOT)): sha256_file(prep_path),
            **{
                str((REPO_ROOT / config["model_artifact_paths"][model_id]).relative_to(REPO_ROOT)): sha256_file(
                    REPO_ROOT / config["model_artifact_paths"][model_id]
                )
                for model_id in sorted(expected_models)
            },
        },
        "output_artifacts": {
            str(per_sample_path.relative_to(REPO_ROOT)): sha256_file(per_sample_path),
            str(summary_path.relative_to(REPO_ROOT)): sha256_file(summary_path),
        },
    }
    write_json(artifact_dir / "manifest.json", manifest)
    print(f"[stage10] status=EXECUTED rows={len(output_rows)} summaries={len(summary_rows)}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/xai/stage10_fidelity_v1.yaml"),
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Validate the frozen protocol without loading data or running models.",
    )
    args = parser.parse_args()
    config_path = args.config if args.config.is_absolute() else REPO_ROOT / args.config
    if args.check_config:
        config = _load_config(config_path)
        print(f"[stage10] config valid: {config['protocol_version']}")
        return
    run_stage10(config_path)


if __name__ == "__main__":
    main()
