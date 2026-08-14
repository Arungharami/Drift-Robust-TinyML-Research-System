"""Pure schema/ranking utilities — no I/O, fully unit-testable.

Column schemas match the mission's result-table spec exactly so downstream Stage 10/11 code
(and the eventual portal evidence exporter) can rely on a fixed, documented shape.
"""
from __future__ import annotations

from typing import Any

TOP_K_VALUES = (1, 3, 5, 10)

GLOBAL_IMPORTANCE_COLUMNS = (
    "experiment_id", "model_id", "method", "batch", "feature_index", "feature_name",
    "importance", "importance_std", "rank", "status",
)
LOCAL_SAMPLE_COLUMNS = (
    "experiment_id", "sample_id", "model_id", "batch", "row_index_in_batch", "true_label",
    "predicted_label", "correct", "prediction_margin", "category",
)
LOCAL_EXPLANATION_COLUMNS = (
    "experiment_id", "sample_id", "model_id", "method", "feature_index", "feature_name",
    "contribution", "rank",
)
REDUCED_EXPLANATION_COLUMNS = (
    "experiment_id", "model_id", "method", "batch", "top_k", "feature_index", "feature_name",
    "importance", "rank", "status",
)
FIDELITY_PREP_COLUMNS = (
    "experiment_id", "sample_id", "model_id", "reference_method", "candidate_method", "top_k",
    "reference_features", "candidate_features",
)
MANIFEST_ROW_COLUMNS = (
    "experiment_id", "model_id", "method", "scope", "status", "reason",
)


def rank_from_importance(importance: list[float]) -> list[int]:
    """1-indexed dense rank, descending importance. Ties broken by feature index (stable)."""
    order = sorted(range(len(importance)), key=lambda i: (-importance[i], i))
    ranks = [0] * len(importance)
    for position, feature_index in enumerate(order, start=1):
        ranks[feature_index] = position
    return ranks


def top_k_feature_indices(importance: list[float], k: int) -> list[int]:
    """Feature indices of the k largest importance values, ties broken by feature index."""
    order = sorted(range(len(importance)), key=lambda i: (-importance[i], i))
    return order[:k]


def build_global_importance_rows(
    *, experiment_id: str, model_id: str, method: str, batch: str, importance: list[float],
    importance_std: list[float] | None, feature_names: list[str], status: str = "EXECUTED",
) -> list[dict[str, Any]]:
    ranks = rank_from_importance(importance)
    stds = importance_std or [None] * len(importance)
    return [
        {
            "experiment_id": experiment_id, "model_id": model_id, "method": method, "batch": batch,
            "feature_index": i, "feature_name": feature_names[i], "importance": importance[i],
            "importance_std": stds[i], "rank": ranks[i], "status": status,
        }
        for i in range(len(importance))
    ]


def build_reduced_rows(
    *, experiment_id: str, model_id: str, method: str, batch: str, importance: list[float],
    feature_names: list[str], top_k_values: tuple[int, ...] = TOP_K_VALUES, status: str = "EXECUTED",
) -> list[dict[str, Any]]:
    ranks = rank_from_importance(importance)
    rows: list[dict[str, Any]] = []
    for k in top_k_values:
        if k > len(importance):
            continue
        for feature_index in top_k_feature_indices(importance, k):
            rows.append(
                {
                    "experiment_id": experiment_id, "model_id": model_id, "method": method, "batch": batch,
                    "top_k": k, "feature_index": feature_index, "feature_name": feature_names[feature_index],
                    "importance": importance[feature_index], "rank": ranks[feature_index], "status": status,
                }
            )
    return rows
