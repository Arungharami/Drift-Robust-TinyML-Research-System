"""Deterministic global-explanation stability metrics for Stage 11."""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.stats import kendalltau, spearmanr


def validate_feature_vectors(
    ranks: Sequence[int],
    importance: Sequence[float],
    *,
    expected_features: int,
) -> tuple[np.ndarray, np.ndarray]:
    rank_array = np.asarray(ranks, dtype=int)
    importance_array = np.asarray(importance, dtype=float)
    if rank_array.ndim != 1 or importance_array.ndim != 1:
        raise ValueError("ranks and importance must be one-dimensional")
    if rank_array.size != expected_features or importance_array.size != expected_features:
        raise ValueError(f"expected {expected_features} features")
    if set(rank_array.tolist()) != set(range(1, expected_features + 1)):
        raise ValueError("ranks must be a complete 1..n_features permutation")
    if not np.all(np.isfinite(importance_array)):
        raise ValueError("importance values must be finite")
    return rank_array, importance_array


def top_k_jaccard(ranks_a: Sequence[int], ranks_b: Sequence[int], top_k: int) -> float:
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    a = np.asarray(ranks_a, dtype=int)
    b = np.asarray(ranks_b, dtype=int)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("rank vectors must be matching one-dimensional arrays")
    if top_k > a.size:
        raise ValueError("top_k exceeds the number of features")
    selected_a = set(np.flatnonzero(a <= top_k).tolist())
    selected_b = set(np.flatnonzero(b <= top_k).tolist())
    union = selected_a | selected_b
    return len(selected_a & selected_b) / float(len(union))


def cosine_similarity(values_a: Sequence[float], values_b: Sequence[float]) -> float:
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)
    if a.shape != b.shape or a.ndim != 1:
        raise ValueError("importance vectors must be matching one-dimensional arrays")
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0.0:
        raise ValueError("cosine similarity is undefined for a zero vector")
    return float(np.dot(a, b) / denominator)


def compare_explanations(
    ranks_a: Sequence[int],
    importance_a: Sequence[float],
    ranks_b: Sequence[int],
    importance_b: Sequence[float],
    *,
    top_k_values: Sequence[int],
    expected_features: int,
) -> dict[str, float]:
    """Compare two feature-level global explanations with complementary metrics."""
    rank_a, value_a = validate_feature_vectors(
        ranks_a, importance_a, expected_features=expected_features
    )
    rank_b, value_b = validate_feature_vectors(
        ranks_b, importance_b, expected_features=expected_features
    )
    spearman = float(spearmanr(rank_a, rank_b).statistic)
    kendall = float(kendalltau(rank_a, rank_b).statistic)
    result = {
        "spearman_rank_correlation": spearman,
        "kendall_rank_correlation": kendall,
        "importance_cosine_similarity": cosine_similarity(value_a, value_b),
    }
    for top_k in top_k_values:
        result[f"top_{int(top_k)}_jaccard"] = top_k_jaccard(rank_a, rank_b, int(top_k))
    return result
