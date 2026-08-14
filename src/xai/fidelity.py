"""Behavioral fidelity metrics for reduced local explanations.

The functions in this module are model-agnostic and operate on fitted estimators that expose
predict_proba and classes_. Feature indices are 1-based at the artifact boundary to match the
UCI dataset and Stage 09 outputs, then converted to zero-based NumPy positions internally.
"""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np


def validate_feature_ranking(
    features: Sequence[int], *, n_features: int, minimum_length: int, name: str
) -> list[int]:
    """Validate a 1-based feature ranking and return it as plain integers."""
    values = [int(value) for value in features]
    if len(values) < minimum_length:
        raise ValueError(f"{name} has {len(values)} features; expected at least {minimum_length}")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} contains duplicate feature indices")
    invalid = [value for value in values if not 1 <= value <= n_features]
    if invalid:
        raise ValueError(f"{name} contains out-of-range feature indices: {invalid}")
    return values


def rank_overlap_at_k(candidate: Sequence[int], reference: Sequence[int], top_k: int) -> float:
    """Set overlap of two ranked top-k explanations, normalized by k."""
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    if len(candidate) < top_k or len(reference) < top_k:
        raise ValueError("candidate and reference rankings must each contain at least top_k entries")
    return len(set(candidate[:top_k]) & set(reference[:top_k])) / float(top_k)


def build_keep_delete_inputs(
    sample: np.ndarray, baseline: np.ndarray, features: Sequence[int]
) -> tuple[np.ndarray, np.ndarray]:
    """Build keep-only and delete-selected counterfactual inputs."""
    sample_array = np.asarray(sample, dtype=float)
    baseline_array = np.asarray(baseline, dtype=float)
    if sample_array.ndim != 1 or baseline_array.ndim != 1:
        raise ValueError("sample and baseline must be one-dimensional")
    if sample_array.shape != baseline_array.shape:
        raise ValueError("sample and baseline must have identical shapes")
    selected = validate_feature_ranking(
        features,
        n_features=sample_array.size,
        minimum_length=1,
        name="features",
    )
    positions = np.asarray(selected, dtype=int) - 1
    keep_only = baseline_array.copy()
    keep_only[positions] = sample_array[positions]
    delete_selected = sample_array.copy()
    delete_selected[positions] = baseline_array[positions]
    return keep_only, delete_selected


def evaluate_fidelity(
    model: Any,
    sample: np.ndarray,
    baseline: np.ndarray,
    candidate_features: Sequence[int],
    reference_features: Sequence[int],
    top_k: int,
) -> dict[str, Any]:
    """Evaluate candidate and reference top-k behavior for one sample.

    Probabilities are always measured for the class predicted on the unperturbed input. This
    keeps sufficiency and comprehensiveness comparable even when a perturbed input changes class.
    """
    if not hasattr(model, "predict_proba"):
        raise TypeError("fidelity evaluation requires a fitted model with predict_proba")
    sample_array = np.asarray(sample, dtype=float)
    baseline_array = np.asarray(baseline, dtype=float)
    if sample_array.ndim != 1 or baseline_array.shape != sample_array.shape:
        raise ValueError("sample and baseline must be matching one-dimensional vectors")

    candidate = validate_feature_ranking(
        candidate_features,
        n_features=sample_array.size,
        minimum_length=top_k,
        name="candidate_features",
    )[:top_k]
    reference = validate_feature_ranking(
        reference_features,
        n_features=sample_array.size,
        minimum_length=top_k,
        name="reference_features",
    )[:top_k]

    candidate_keep, candidate_delete = build_keep_delete_inputs(sample_array, baseline_array, candidate)
    reference_keep, reference_delete = build_keep_delete_inputs(sample_array, baseline_array, reference)
    variants = np.vstack(
        [sample_array, candidate_keep, candidate_delete, reference_keep, reference_delete]
    )
    probabilities = np.asarray(model.predict_proba(variants), dtype=float)
    if probabilities.ndim != 2 or probabilities.shape[0] != 5:
        raise ValueError("predict_proba returned an unexpected shape")
    classes = np.asarray(getattr(model, "classes_", np.arange(probabilities.shape[1])))
    if classes.size != probabilities.shape[1]:
        raise ValueError("model classes_ does not match predict_proba columns")

    predicted_positions = np.argmax(probabilities, axis=1)
    predicted_classes = classes[predicted_positions]
    target_position = int(predicted_positions[0])
    target_probabilities = probabilities[:, target_position]
    full_probability = float(target_probabilities[0])

    def metrics(keep_position: int, delete_position: int) -> dict[str, Any]:
        keep_probability = float(target_probabilities[keep_position])
        delete_probability = float(target_probabilities[delete_position])
        sufficiency_gap = full_probability - keep_probability
        return {
            "prediction_preserved": int(predicted_classes[keep_position] == predicted_classes[0]),
            "keep_predicted_class": predicted_classes[keep_position].item()
            if hasattr(predicted_classes[keep_position], "item")
            else predicted_classes[keep_position],
            "delete_predicted_class": predicted_classes[delete_position].item()
            if hasattr(predicted_classes[delete_position], "item")
            else predicted_classes[delete_position],
            "keep_target_probability": keep_probability,
            "delete_target_probability": delete_probability,
            "probability_closeness": max(0.0, 1.0 - abs(full_probability - keep_probability)),
            "sufficiency_gap": sufficiency_gap,
            "absolute_sufficiency_gap": abs(sufficiency_gap),
            "comprehensiveness_drop": full_probability - delete_probability,
        }

    candidate_metrics = metrics(1, 2)
    reference_metrics = metrics(3, 4)
    full_class = predicted_classes[0].item() if hasattr(predicted_classes[0], "item") else predicted_classes[0]
    row: dict[str, Any] = {
        "top_k": int(top_k),
        "rank_overlap_at_k": rank_overlap_at_k(candidate, reference, top_k),
        "full_predicted_class": full_class,
        "full_target_probability": full_probability,
    }
    row.update({f"candidate_{key}": value for key, value in candidate_metrics.items()})
    row.update({f"reference_{key}": value for key, value in reference_metrics.items()})
    row["candidate_minus_reference_probability_closeness"] = (
        row["candidate_probability_closeness"] - row["reference_probability_closeness"]
    )
    row["candidate_minus_reference_absolute_sufficiency_gap"] = (
        row["candidate_absolute_sufficiency_gap"] - row["reference_absolute_sufficiency_gap"]
    )
    row["candidate_minus_reference_comprehensiveness_drop"] = (
        row["candidate_comprehensiveness_drop"] - row["reference_comprehensiveness_drop"]
    )
    return row
