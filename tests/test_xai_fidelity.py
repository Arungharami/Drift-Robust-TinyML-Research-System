"""Synthetic tests for Stage 10 fidelity metrics; no research data or artifacts required."""
from __future__ import annotations

import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.xai.fidelity import (
    build_keep_delete_inputs,
    evaluate_fidelity,
    rank_overlap_at_k,
    validate_feature_ranking,
)
from src.xai.run_stage10 import summarize_rows


def _model_and_sample():
    rng = np.random.RandomState(42)
    x = rng.normal(size=(160, 6))
    y = (2.0 * x[:, 0] - x[:, 1] + 0.5 * x[:, 2] > 0).astype(int)
    model = Pipeline(
        [("scaler", StandardScaler()), ("model", LogisticRegression(random_state=42))]
    )
    model.fit(x, y)
    return model, x[0], x.mean(axis=0)


def test_rank_overlap_at_k():
    assert rank_overlap_at_k([1, 2, 3], [1, 3, 4], 3) == pytest.approx(2 / 3)
    assert rank_overlap_at_k([1, 2], [3, 4], 2) == 0.0


def test_rank_overlap_rejects_short_rankings():
    with pytest.raises(ValueError):
        rank_overlap_at_k([1], [1, 2], 2)


def test_feature_ranking_validation_rejects_duplicates_and_bounds():
    with pytest.raises(ValueError, match="duplicate"):
        validate_feature_ranking([1, 1], n_features=3, minimum_length=2, name="candidate")
    with pytest.raises(ValueError, match="out-of-range"):
        validate_feature_ranking([1, 4], n_features=3, minimum_length=2, name="candidate")


def test_keep_delete_inputs_are_complementary():
    sample = np.array([10.0, 20.0, 30.0, 40.0])
    baseline = np.array([1.0, 2.0, 3.0, 4.0])
    keep, delete = build_keep_delete_inputs(sample, baseline, [1, 3])
    np.testing.assert_array_equal(keep, [10.0, 2.0, 30.0, 4.0])
    np.testing.assert_array_equal(delete, [1.0, 20.0, 3.0, 40.0])


def test_identical_candidate_and_reference_have_identical_behavior():
    model, sample, baseline = _model_and_sample()
    result = evaluate_fidelity(model, sample, baseline, [1, 2], [1, 2, 3, 4], 2)
    assert result["rank_overlap_at_k"] == 1.0
    assert result["candidate_probability_closeness"] == pytest.approx(
        result["reference_probability_closeness"]
    )
    assert result["candidate_absolute_sufficiency_gap"] == pytest.approx(
        result["reference_absolute_sufficiency_gap"]
    )
    assert result["candidate_comprehensiveness_drop"] == pytest.approx(
        result["reference_comprehensiveness_drop"]
    )


def test_metrics_are_finite_and_probabilistic_values_bounded():
    model, sample, baseline = _model_and_sample()
    result = evaluate_fidelity(model, sample, baseline, [1, 2], [3, 4, 5, 6], 2)
    assert 0.0 <= result["full_target_probability"] <= 1.0
    assert 0.0 <= result["candidate_probability_closeness"] <= 1.0
    assert result["candidate_prediction_preserved"] in {0, 1}
    assert all(
        np.isfinite(value)
        for key, value in result.items()
        if isinstance(value, float) and key != "top_k"
    )


def test_summarize_rows_groups_models_and_top_k():
    base = {
        "experiment_id": "EXP-FID-TEST",
        "source_experiment_id": "EXP-XAI-TEST",
        "model_id": "MODEL-C1",
        "candidate_method": "CANDIDATE",
        "reference_method": "REFERENCE",
        "top_k": 1,
        "rank_overlap_at_k": 0.5,
        "candidate_prediction_preserved": 1,
        "reference_prediction_preserved": 1,
        "candidate_probability_closeness": 0.8,
        "reference_probability_closeness": 0.9,
        "candidate_absolute_sufficiency_gap": 0.2,
        "reference_absolute_sufficiency_gap": 0.1,
        "candidate_comprehensiveness_drop": 0.3,
        "reference_comprehensiveness_drop": 0.4,
        "candidate_minus_reference_probability_closeness": -0.1,
        "candidate_minus_reference_absolute_sufficiency_gap": 0.1,
        "candidate_minus_reference_comprehensiveness_drop": -0.1,
    }
    rows = [base, {**base, "rank_overlap_at_k": 1.0, "candidate_prediction_preserved": 0}]
    summary = summarize_rows(rows)
    assert len(summary) == 1
    assert summary[0]["n_samples"] == 2
    assert summary[0]["mean_rank_overlap_at_k"] == pytest.approx(0.75)
    assert summary[0]["candidate_prediction_preservation_rate"] == pytest.approx(0.5)
