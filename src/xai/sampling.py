"""Deterministic local-sample selection.

Selection is by sorted order (batch, then row index), never by unconstrained randomness, so the
exact same sample_ids are reproduced on every re-run given the same predictions — Stage 10/11
depend on this. `seed` is still recorded (and used for the one place ties could otherwise be
ambiguous) purely for provenance completeness.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

CATEGORY_CORRECT = "CORRECT_REPRESENTATIVE"
CATEGORY_MISCLASSIFIED = "MISCLASSIFIED"
CATEGORY_NEAR_BOUNDARY = "NEAR_DECISION_BOUNDARY"


def _margin(probability_columns: pd.DataFrame) -> pd.Series:
    sorted_probs = np.sort(probability_columns.to_numpy(), axis=1)
    return pd.Series(sorted_probs[:, -1] - sorted_probs[:, -2], index=probability_columns.index)


def select_local_samples(
    predictions: pd.DataFrame,
    *,
    seed: int,
    per_class_correct: int = 2,
    max_misclassified: int = 5,
    max_near_boundary: int = 5,
) -> pd.DataFrame:
    """`predictions` columns required: batch, row_index, true_label, predicted_label, correct,
    plus one `probability_class_<label>` column per class. Returns a deterministic subset with
    an added `category` column (a sample may satisfy more than one category — kept once, all
    matching categories recorded, comma-joined).
    """
    frame = predictions.sort_values(["batch", "row_index"]).reset_index(drop=True)
    prob_cols = [c for c in frame.columns if c.startswith("probability_class_")]
    if prob_cols:
        frame = frame.assign(prediction_margin=_margin(frame[prob_cols]))
    else:
        frame = frame.assign(prediction_margin=np.nan)

    categories: dict[int, set[str]] = {}

    def tag(indices: list[int], category: str) -> None:
        for idx in indices:
            categories.setdefault(idx, set()).add(category)

    for batch, batch_frame in frame.groupby("batch", sort=True):
        correct = batch_frame[batch_frame["correct"]]
        for _true_label, group in correct.groupby("true_label", sort=True):
            tag(group.index[:per_class_correct].tolist(), CATEGORY_CORRECT)

        misclassified = batch_frame[~batch_frame["correct"]]
        tag(misclassified.index[:max_misclassified].tolist(), CATEGORY_MISCLASSIFIED)

        if prob_cols:
            boundary = batch_frame.sort_values("prediction_margin", kind="mergesort")
            tag(boundary.index[:max_near_boundary].tolist(), CATEGORY_NEAR_BOUNDARY)

    if not categories:
        return frame.iloc[0:0].assign(category="")

    selected_index = sorted(categories)
    result = frame.loc[selected_index].copy()
    result["category"] = [",".join(sorted(categories[i])) for i in selected_index]
    result["seed"] = seed
    return result.reset_index(drop=True)
