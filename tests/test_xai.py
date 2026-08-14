"""Tests for src/xai — schema, deterministic sampling, feature ranking, top-k extraction,
capability detection, provenance fields, invalid/missing model handling, and fixed-seed
permutation reproducibility. No test depends on the real UCI dataset or the real model
artifacts — small synthetic fixtures only, so this suite runs anywhere.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.xai import feature_map as feature_map_mod
from src.xai import schema
from src.xai.base import NotApplicableError
from src.xai.intrinsic import CoefficientExplainer, ImpurityExplainer, build_intrinsic_explainers
from src.xai.local_ablation import SingleFeatureAblationExplainer
from src.xai.permutation import PermutationImportanceExplainer
from src.xai.sampling import CATEGORY_CORRECT, CATEGORY_MISCLASSIFIED, CATEGORY_NEAR_BOUNDARY, select_local_samples

SEED = 42


def _synthetic_dataset(n_samples: int = 120, n_features: int = 10, n_classes: int = 3):
    rng = np.random.RandomState(SEED)
    x = rng.normal(size=(n_samples, n_features))
    weights = rng.normal(size=(n_features, n_classes))
    logits = x @ weights
    y = np.argmax(logits, axis=1) + 1  # labels 1..n_classes, matching the project's 1-indexed classes
    return x, y


def _fitted_pipeline(estimator) -> Pipeline:
    x, y = _synthetic_dataset()
    pipeline = Pipeline([("scaler", StandardScaler()), ("model", estimator)])
    pipeline.fit(x, y)
    return pipeline


# --- schema -----------------------------------------------------------------------------------


def test_rank_from_importance_descending():
    ranks = schema.rank_from_importance([0.1, 0.9, 0.5])
    assert ranks == [3, 1, 2]


def test_rank_from_importance_ties_broken_by_index():
    ranks = schema.rank_from_importance([0.5, 0.5, 0.9])
    assert ranks[2] == 1
    assert sorted(ranks[:2]) == [2, 3]


def test_top_k_feature_indices():
    importance = [0.1, 0.9, 0.5, 0.3]
    assert schema.top_k_feature_indices(importance, 2) == [1, 2]
    assert schema.top_k_feature_indices(importance, 4) == [1, 2, 3, 0]


def test_build_global_importance_rows_shape_and_status():
    rows = schema.build_global_importance_rows(
        experiment_id="EXP-XAI-TEST", model_id="MODEL-C1", method="TEST_METHOD", batch="ALL",
        importance=[0.2, 0.8], importance_std=[0.01, 0.02], feature_names=["f1", "f2"],
    )
    assert len(rows) == 2
    assert set(rows[0]) == set(schema.GLOBAL_IMPORTANCE_COLUMNS)
    assert {r["feature_index"] for r in rows} == {0, 1}
    ranks = {r["feature_index"]: r["rank"] for r in rows}
    assert ranks[1] == 1 and ranks[0] == 2


def test_build_reduced_rows_respects_top_k_values():
    rows = schema.build_reduced_rows(
        experiment_id="EXP-XAI-TEST", model_id="MODEL-C1", method="TEST_METHOD", batch="ALL",
        importance=[0.1, 0.9, 0.5, 0.3, 0.05], feature_names=["a", "b", "c", "d", "e"], top_k_values=(1, 3),
    )
    top1 = [r for r in rows if r["top_k"] == 1]
    top3 = [r for r in rows if r["top_k"] == 3]
    assert len(top1) == 1 and top1[0]["feature_name"] == "b"
    assert len(top3) == 3
    assert {r["feature_name"] for r in top3} == {"b", "c", "d"}


def test_build_reduced_rows_skips_k_larger_than_feature_count():
    rows = schema.build_reduced_rows(
        experiment_id="E", model_id="M", method="X", batch="ALL",
        importance=[0.1, 0.2], feature_names=["a", "b"], top_k_values=(1, 10),
    )
    assert {r["top_k"] for r in rows} == {1}


# --- feature map --------------------------------------------------------------------------------


def test_feature_map_covers_all_128_features_exactly_once():
    rows = feature_map_mod.build_feature_map()
    assert len(rows) == 128
    assert sorted(r["feature_index"] for r in rows) == list(range(1, 129))


def test_feature_map_sensor_grouping_is_contiguous_blocks_of_eight():
    rows = feature_map_mod.build_feature_map()
    by_index = {r["feature_index"]: r for r in rows}
    assert by_index[1]["sensor_id"] == 1
    assert by_index[8]["sensor_id"] == 1
    assert by_index[9]["sensor_id"] == 2
    assert by_index[128]["sensor_id"] == 16


def test_feature_map_rejects_wrong_feature_count():
    with pytest.raises(ValueError):
        feature_map_mod.build_feature_map(n_features=100)


def test_feature_map_does_not_invent_meaning_beyond_documented_types():
    rows = feature_map_mod.build_feature_map()
    documented = set(feature_map_mod.FEATURE_TYPES_PER_SENSOR)
    assert {r["feature_type"] for r in rows} == documented
    # original_name must be the raw column index, never a semantic guess
    assert all(r["original_name"] == str(r["feature_index"]) for r in rows)


def test_write_feature_map_creates_valid_csv(tmp_path: Path):
    out = tmp_path / "feature_map.csv"
    rows = feature_map_mod.write_feature_map(out)
    assert out.exists()
    loaded = pd.read_csv(out)
    assert len(loaded) == len(rows) == 128
    assert list(loaded.columns) == list(feature_map_mod.FEATURE_MAP_COLUMNS)


# --- capability detection -----------------------------------------------------------------------


def test_logistic_regression_supports_intrinsic_coefficient_local_and_global():
    pipeline = _fitted_pipeline(LogisticRegression(max_iter=500, random_state=SEED))
    explainer = CoefficientExplainer(pipeline, "MODEL-C1")
    assert explainer.supports_local is True
    assert explainer.supports_global is True


def test_random_forest_does_not_support_intrinsic_coefficient():
    pipeline = _fitted_pipeline(RandomForestClassifier(n_estimators=10, random_state=SEED))
    explainer = CoefficientExplainer(pipeline, "MODEL-C2")
    assert explainer.supports_local is False
    assert explainer.supports_global is False


def test_random_forest_supports_impurity_global_only():
    pipeline = _fitted_pipeline(RandomForestClassifier(n_estimators=10, random_state=SEED))
    explainer = ImpurityExplainer(pipeline, "MODEL-C2")
    assert explainer.supports_global is True
    assert explainer.supports_local is False


def test_svc_has_no_applicable_intrinsic_explainer():
    pipeline = _fitted_pipeline(SVC(probability=True, random_state=SEED))
    explainers = build_intrinsic_explainers(pipeline, "MODEL-C3")
    assert explainers == []


def test_calling_unsupported_explanation_raises_not_applicable():
    pipeline = _fitted_pipeline(RandomForestClassifier(n_estimators=10, random_state=SEED))
    explainer = CoefficientExplainer(pipeline, "MODEL-C2")
    with pytest.raises(NotApplicableError):
        explainer.explain_global()


def test_impurity_local_raises_not_applicable():
    pipeline = _fitted_pipeline(RandomForestClassifier(n_estimators=10, random_state=SEED))
    explainer = ImpurityExplainer(pipeline, "MODEL-C2")
    with pytest.raises(NotApplicableError):
        explainer.explain_local(np.zeros(10))


# --- permutation importance (fixed-seed reproducibility) --------------------------------------


def test_permutation_importance_is_reproducible_given_fixed_seed():
    pipeline = _fitted_pipeline(LogisticRegression(max_iter=500, random_state=SEED))
    x, y = _synthetic_dataset()
    explainer_a = PermutationImportanceExplainer(pipeline, "MODEL-C1", n_repeats=3, seed=SEED)
    explainer_b = PermutationImportanceExplainer(pipeline, "MODEL-C1", n_repeats=3, seed=SEED)
    result_a = explainer_a.explain_global(x=x, y=y)
    result_b = explainer_b.explain_global(x=x, y=y)
    assert result_a["importance"] == result_b["importance"]
    assert result_a["scoring_metric"] == "macro_f1"


def test_permutation_importance_global_only():
    pipeline = _fitted_pipeline(LogisticRegression(max_iter=500, random_state=SEED))
    explainer = PermutationImportanceExplainer(pipeline, "MODEL-C1", n_repeats=3, seed=SEED)
    assert explainer.supports_local is False
    assert explainer.supports_global is True


# --- local ablation ------------------------------------------------------------------------------


def test_ablation_explanation_shape_matches_feature_count():
    pipeline = _fitted_pipeline(LogisticRegression(max_iter=500, random_state=SEED))
    x, _ = _synthetic_dataset()
    baseline = x.mean(axis=0)
    explainer = SingleFeatureAblationExplainer(pipeline, "MODEL-C1", baseline=baseline)
    result = explainer.explain_local(x[0])
    assert len(result["feature_contributions"]) == x.shape[1]
    assert result["method"] == "SINGLE_FEATURE_ABLATION_LOCAL"


def test_ablation_is_model_agnostic_across_estimator_types():
    x, _ = _synthetic_dataset()
    baseline = x.mean(axis=0)
    for estimator in (LogisticRegression(max_iter=500, random_state=SEED), RandomForestClassifier(n_estimators=10, random_state=SEED)):
        pipeline = _fitted_pipeline(estimator)
        explainer = SingleFeatureAblationExplainer(pipeline, "MODEL-X", baseline=baseline)
        result = explainer.explain_local(x[0])
        assert len(result["feature_contributions"]) == x.shape[1]


# --- deterministic sampling -----------------------------------------------------------------------


def _predictions_frame() -> pd.DataFrame:
    rng = np.random.RandomState(SEED)
    rows = []
    for batch in (2, 6):
        for i in range(20):
            true_label = int(rng.randint(1, 4))
            predicted_label = true_label if rng.random() > 0.3 else int(rng.randint(1, 4))
            probs = rng.dirichlet(np.ones(3))
            rows.append({
                "batch": batch, "row_index": i, "true_label": true_label, "predicted_label": predicted_label,
                "correct": predicted_label == true_label,
                "probability_class_1": probs[0], "probability_class_2": probs[1], "probability_class_3": probs[2],
            })
    return pd.DataFrame(rows)


def test_select_local_samples_is_deterministic():
    frame = _predictions_frame()
    a = select_local_samples(frame, seed=SEED)
    b = select_local_samples(frame, seed=SEED)
    pd.testing.assert_frame_equal(a, b)


def test_select_local_samples_produces_expected_categories():
    frame = _predictions_frame()
    selected = select_local_samples(frame, seed=SEED, per_class_correct=1, max_misclassified=2, max_near_boundary=2)
    all_categories = set(",".join(selected["category"]).split(","))
    assert all_categories <= {CATEGORY_CORRECT, CATEGORY_MISCLASSIFIED, CATEGORY_NEAR_BOUNDARY}
    assert len(selected) > 0
    # sample_id itself is assembled downstream in run_stage09.py from (batch, row_index); here
    # we confirm that pair is already unique, which is what makes a later sample_id unique.
    pairs = list(zip(selected["batch"], selected["row_index"]))
    assert len(pairs) == len(set(pairs))


def test_select_local_samples_handles_empty_input():
    empty = pd.DataFrame(columns=["batch", "row_index", "true_label", "predicted_label", "correct"])
    result = select_local_samples(empty, seed=SEED)
    assert len(result) == 0


def test_select_local_samples_no_duplicate_rows_across_categories():
    frame = _predictions_frame()
    selected = select_local_samples(frame, seed=SEED)
    pairs = list(zip(selected["batch"], selected["row_index"]))
    assert len(pairs) == len(set(pairs))


# --- invalid / missing model handling (schema-level; full I/O path covered by the runner itself) -


def test_explainer_rejects_missing_predict_proba():
    class _NoProba:
        pass

    with pytest.raises(ValueError):
        SingleFeatureAblationExplainer(_NoProba(), "MODEL-X", baseline=np.zeros(3))
