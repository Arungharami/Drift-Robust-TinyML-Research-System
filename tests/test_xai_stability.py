"""Synthetic tests for Stage 11 stability; no research artifacts required."""
from __future__ import annotations

import numpy as np
import pytest

from src.xai.run_stage11 import summarize_pairs
from src.xai.stability import (
    compare_explanations,
    cosine_similarity,
    top_k_jaccard,
    validate_feature_vectors,
)


def test_identical_explanations_are_perfectly_stable():
    ranks = [1, 2, 3, 4]
    importance = [0.8, 0.6, 0.3, 0.1]
    result = compare_explanations(
        ranks,
        importance,
        ranks,
        importance,
        top_k_values=[1, 2],
        expected_features=4,
    )
    assert result["spearman_rank_correlation"] == pytest.approx(1.0)
    assert result["kendall_rank_correlation"] == pytest.approx(1.0)
    assert result["importance_cosine_similarity"] == pytest.approx(1.0)
    assert result["top_1_jaccard"] == 1.0
    assert result["top_2_jaccard"] == 1.0


def test_reversed_rankings_have_negative_rank_correlation():
    result = compare_explanations(
        [1, 2, 3, 4],
        [4.0, 3.0, 2.0, 1.0],
        [4, 3, 2, 1],
        [1.0, 2.0, 3.0, 4.0],
        top_k_values=[1, 2],
        expected_features=4,
    )
    assert result["spearman_rank_correlation"] == pytest.approx(-1.0)
    assert result["kendall_rank_correlation"] == pytest.approx(-1.0)
    assert result["top_1_jaccard"] == 0.0
    assert result["top_2_jaccard"] == 0.0


def test_top_k_jaccard_uses_feature_positions():
    assert top_k_jaccard([1, 2, 3, 4], [2, 1, 4, 3], 2) == 1.0
    assert top_k_jaccard([1, 2, 3, 4], [3, 4, 1, 2], 2) == 0.0


def test_validation_rejects_incomplete_rank_permutation():
    with pytest.raises(ValueError, match="complete"):
        validate_feature_vectors([1, 1, 3], [0.2, 0.3, 0.4], expected_features=3)


def test_cosine_rejects_zero_vector():
    with pytest.raises(ValueError, match="zero vector"):
        cosine_similarity([0.0, 0.0], [1.0, 2.0])


def test_summary_excludes_reference_self_comparison():
    common = {
        "experiment_id": "EXP-STAB-TEST",
        "source_experiment_id": "EXP-XAI-TEST",
        "model_id": "MODEL-C1",
        "method": "METHOD",
        "kendall_rank_correlation": 0.5,
        "importance_cosine_similarity": 0.6,
        "top_1_jaccard": 0.0,
        "top_3_jaccard": 0.2,
    }
    rows = [
        {
            **common,
            "comparison": "REFERENCE",
            "batch_a": 2,
            "batch_b": 2,
            "spearman_rank_correlation": 1.0,
        },
        {
            **common,
            "comparison": "REFERENCE",
            "batch_a": 2,
            "batch_b": 3,
            "spearman_rank_correlation": 0.4,
        },
        {
            **common,
            "comparison": "ADJACENT",
            "batch_a": 2,
            "batch_b": 3,
            "spearman_rank_correlation": 0.7,
        },
    ]
    summary = summarize_pairs(rows, [1, 3])
    assert len(summary) == 1
    assert summary[0]["n_reference_comparisons"] == 1
    assert summary[0]["mean_reference_spearman"] == pytest.approx(0.4)
    assert summary[0]["mean_adjacent_spearman"] == pytest.approx(0.7)
