"""Stage 11 runner: chronological stability of Stage 09 global explanations.

Usage:
    python -m src.xai.run_stage11 --config configs/xai/stage11_stability_v1.yaml
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.utils.hashing import sha256_file, stable_hash  # noqa: E402
from src.utils.reproducibility import capture_environment  # noqa: E402
from src.xai.manifest import write_json  # noqa: E402
from src.xai.stability import compare_explanations, validate_feature_vectors  # noqa: E402


def _load_config(path: Path) -> dict[str, Any]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    required = {
        "protocol_version",
        "experiment_id",
        "source_experiment_id",
        "dataset_hash",
        "split_protocol",
        "split_hash",
        "method",
        "eligible_model_ids",
        "batches",
        "reference_batch",
        "top_k_values",
        "n_features",
        "input_path",
        "output_paths",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"Stage 11 config is missing keys: {missing}")
    batches = [int(value) for value in config["batches"]]
    if batches != sorted(set(batches)):
        raise ValueError("batches must be sorted and unique")
    if int(config["reference_batch"]) not in batches:
        raise ValueError("reference_batch must be one of batches")
    return config


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def _build_vectors(
    rows: list[dict[str, str]], config: dict[str, Any]
) -> dict[tuple[str, int], tuple[np.ndarray, np.ndarray]]:
    method = str(config["method"])
    models = set(config["eligible_model_ids"])
    batches = {int(value) for value in config["batches"]}
    n_features = int(config["n_features"])
    selected = [
        row
        for row in rows
        if row["method"] == method
        and row["model_id"] in models
        and row["batch"] != "ALL"
        and int(row["batch"]) in batches
        and row["status"] == "EXECUTED"
    ]
    vectors: dict[tuple[str, int], tuple[np.ndarray, np.ndarray]] = {}
    for model_id in sorted(models):
        for batch_id in sorted(batches):
            group = [
                row
                for row in selected
                if row["model_id"] == model_id and int(row["batch"]) == batch_id
            ]
            if len(group) != n_features:
                raise ValueError(
                    f"{model_id} batch {batch_id}: expected {n_features} rows, found {len(group)}"
                )
            indices = [int(row["feature_index"]) for row in group]
            expected_indices = set(range(n_features))
            if set(indices) != expected_indices:
                raise ValueError(f"{model_id} batch {batch_id}: incomplete feature indices")
            ordered = sorted(group, key=lambda row: int(row["feature_index"]))
            ranks = np.asarray([int(row["rank"]) for row in ordered], dtype=int)
            importance = np.asarray([float(row["importance"]) for row in ordered], dtype=float)
            vectors[(model_id, batch_id)] = validate_feature_vectors(
                ranks, importance, expected_features=n_features
            )
    return vectors


def summarize_pairs(rows: list[dict[str, Any]], top_k_values: list[int]) -> list[dict[str, Any]]:
    frame = pd.DataFrame(rows)
    summaries: list[dict[str, Any]] = []
    for model_id, group in frame.groupby("model_id", sort=True):
        reference = group[
            (group["comparison"] == "REFERENCE")
            & (group["batch_a"] != group["batch_b"])
        ]
        adjacent = group[group["comparison"] == "ADJACENT"]
        row: dict[str, Any] = {
            "experiment_id": group["experiment_id"].iloc[0],
            "source_experiment_id": group["source_experiment_id"].iloc[0],
            "model_id": model_id,
            "method": group["method"].iloc[0],
            "n_reference_comparisons": int(len(reference)),
            "n_adjacent_comparisons": int(len(adjacent)),
            "mean_reference_spearman": float(reference["spearman_rank_correlation"].mean()),
            "std_reference_spearman": float(reference["spearman_rank_correlation"].std(ddof=1)),
            "minimum_reference_spearman": float(reference["spearman_rank_correlation"].min()),
            "mean_reference_kendall": float(reference["kendall_rank_correlation"].mean()),
            "mean_reference_cosine": float(reference["importance_cosine_similarity"].mean()),
            "mean_adjacent_spearman": float(adjacent["spearman_rank_correlation"].mean()),
            "std_adjacent_spearman": float(adjacent["spearman_rank_correlation"].std(ddof=1)),
            "minimum_adjacent_spearman": float(adjacent["spearman_rank_correlation"].min()),
            "mean_adjacent_kendall": float(adjacent["kendall_rank_correlation"].mean()),
            "mean_adjacent_cosine": float(adjacent["importance_cosine_similarity"].mean()),
        }
        for top_k in top_k_values:
            column = f"top_{top_k}_jaccard"
            row[f"mean_reference_top_{top_k}_jaccard"] = float(reference[column].mean())
            row[f"mean_adjacent_top_{top_k}_jaccard"] = float(adjacent[column].mean())
        summaries.append(row)
    return summaries


def run_stage11(config_path: Path) -> dict[str, Any]:
    config = _load_config(config_path)
    input_path = REPO_ROOT / config["input_path"]
    pairwise_path = REPO_ROOT / config["output_paths"]["pairwise"]
    summary_path = REPO_ROOT / config["output_paths"]["summary"]
    artifact_dir = REPO_ROOT / config["output_paths"]["artifact_dir"]
    top_k_values = [int(value) for value in config["top_k_values"]]
    batches = [int(value) for value in config["batches"]]
    reference_batch = int(config["reference_batch"])
    models = sorted(config["eligible_model_ids"])
    n_features = int(config["n_features"])

    vectors = _build_vectors(_read_csv(input_path), config)
    comparisons: list[tuple[str, int, int]] = [
        ("REFERENCE", reference_batch, batch_id) for batch_id in batches
    ]
    comparisons += [
        ("ADJACENT", batches[index], batches[index + 1])
        for index in range(len(batches) - 1)
    ]

    pairwise_rows: list[dict[str, Any]] = []
    for model_id in models:
        for comparison, batch_a, batch_b in comparisons:
            ranks_a, importance_a = vectors[(model_id, batch_a)]
            ranks_b, importance_b = vectors[(model_id, batch_b)]
            metrics = compare_explanations(
                ranks_a,
                importance_a,
                ranks_b,
                importance_b,
                top_k_values=top_k_values,
                expected_features=n_features,
            )
            pairwise_rows.append(
                {
                    "experiment_id": config["experiment_id"],
                    "source_experiment_id": config["source_experiment_id"],
                    "model_id": model_id,
                    "method": config["method"],
                    "comparison": comparison,
                    "batch_a": batch_a,
                    "batch_b": batch_b,
                    "batch_gap": batch_b - batch_a,
                    "n_features": n_features,
                    **metrics,
                }
            )

    summary_rows = summarize_pairs(pairwise_rows, top_k_values)
    expected_pairwise = config.get("expected_pairwise_rows")
    expected_summary = config.get("expected_summary_rows")
    if expected_pairwise is not None and len(pairwise_rows) != int(expected_pairwise):
        raise ValueError(f"Expected {expected_pairwise} pairwise rows, found {len(pairwise_rows)}")
    if expected_summary is not None and len(summary_rows) != int(expected_summary):
        raise ValueError(f"Expected {expected_summary} summary rows, found {len(summary_rows)}")

    _write_csv(pairwise_path, pairwise_rows)
    _write_csv(summary_path, summary_rows)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifact_dir / "config.json", config)
    (artifact_dir / "config.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False), encoding="utf-8"
    )
    environment = capture_environment(
        artifact_dir / "environment.json", seed=int(config.get("random_seed", 42))
    )
    (artifact_dir / "run.log").write_text(
        f"[stage11] models={len(models)} pairwise_rows={len(pairwise_rows)} "
        f"summary_rows={len(summary_rows)}\n",
        encoding="utf-8",
    )
    manifest = {
        "experiment_id": config["experiment_id"],
        "stage": "11",
        "status": "EXECUTED",
        "created_at": environment["timestamp_utc"],
        "git_commit": environment["git_commit"],
        "protocol_version": config["protocol_version"],
        "config_hash": stable_hash(config),
        "source_experiment_id": config["source_experiment_id"],
        "dataset_hash": config["dataset_hash"],
        "split_protocol": config["split_protocol"],
        "split_hash": config["split_hash"],
        "method": config["method"],
        "models": models,
        "batches": batches,
        "reference_batch": reference_batch,
        "top_k_values": top_k_values,
        "n_pairwise_rows": len(pairwise_rows),
        "n_summary_rows": len(summary_rows),
        "interpretation": "Descriptive stability metrics only; no preregistered pass/fail threshold.",
        "input_artifacts": {str(input_path.relative_to(REPO_ROOT)): sha256_file(input_path)},
        "output_artifacts": {
            str(pairwise_path.relative_to(REPO_ROOT)): sha256_file(pairwise_path),
            str(summary_path.relative_to(REPO_ROOT)): sha256_file(summary_path),
        },
    }
    write_json(artifact_dir / "manifest.json", manifest)
    print(
        f"[stage11] status=EXECUTED pairs={len(pairwise_rows)} "
        f"summaries={len(summary_rows)}"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/xai/stage11_stability_v1.yaml"),
    )
    parser.add_argument("--check-config", action="store_true")
    args = parser.parse_args()
    config_path = args.config if args.config.is_absolute() else REPO_ROOT / args.config
    if args.check_config:
        config = _load_config(config_path)
        print(f"[stage11] config valid: {config['protocol_version']}")
        return
    run_stage11(config_path)


if __name__ == "__main__":
    main()
