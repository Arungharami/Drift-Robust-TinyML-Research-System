"""Model-agnostic permutation importance, off-device, on legitimate held-out chronological
evaluation data. Uses the project's already-frozen primary metric (macro-F1 — see
configs/classical_baselines.yaml: feature_importance.method) rather than silently substituting
a different scoring function. Applicable to every fitted classifier regardless of architecture.

NEVER modifies the model or preprocessing: the fitted pipeline is used strictly in inference
mode. NEVER uses permutation results to retrain or reselect the model — that would violate the
frozen chronological protocol.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.inspection import permutation_importance
from sklearn.metrics import f1_score, make_scorer
from sklearn.pipeline import Pipeline

from .base import RESOURCE_CLASS_PERMUTATION, ExplainerAdapter

MACRO_F1_SCORER = make_scorer(f1_score, average="macro", zero_division=0)


class PermutationImportanceExplainer(ExplainerAdapter):
    """Global-only by construction — permutation importance is a dataset-level statistic."""

    method_name = "PERMUTATION_IMPORTANCE_MACRO_F1"
    resource_class = RESOURCE_CLASS_PERMUTATION

    def __init__(self, pipeline: Pipeline, model_id: str, n_repeats: int, seed: int):
        super().__init__(pipeline, model_id)
        self.n_repeats = n_repeats
        self.seed = seed

    @property
    def supports_local(self) -> bool:
        return False

    @property
    def supports_global(self) -> bool:
        return True  # model-agnostic: applies to every fitted sklearn-compatible classifier

    def _explain_local(self, x_row: np.ndarray, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError  # unreachable: supports_local is always False

    def _explain_global(self, x: np.ndarray | None = None, y: np.ndarray | None = None, **kwargs: Any) -> dict[str, Any]:
        if x is None or y is None:
            raise ValueError("PermutationImportanceExplainer.explain_global requires x, y (held-out data)")
        result = permutation_importance(
            self.pipeline, x, y, scoring=MACRO_F1_SCORER, n_repeats=self.n_repeats, random_state=self.seed, n_jobs=1
        )
        return {
            "method": self.method_name,
            "importance": result.importances_mean.tolist(),
            "importance_std": result.importances_std.tolist(),
            "n_repeats": self.n_repeats,
            "scoring_metric": "macro_f1",
        }
