"""Model-intrinsic explanations — only for models that genuinely expose meaningful native
feature contributions. Capability is detected by isinstance checks against the fitted
estimator, never assumed from the model_id string alone.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from .base import RESOURCE_CLASS_INTRINSIC, ExplainerAdapter


class CoefficientExplainer(ExplainerAdapter):
    """Linear coefficient x standardized-value explanation. Only applicable to linear models
    exposing `coef_` (here: MODEL-C1 / LogisticRegression). The scaler is the pipeline's own
    fitted StandardScaler, so the "standardized value" is exactly what the model actually saw.
    """

    method_name = "INTRINSIC_COEFFICIENT"
    resource_class = RESOURCE_CLASS_INTRINSIC

    @property
    def supports_local(self) -> bool:
        return isinstance(self.estimator, LogisticRegression) and hasattr(self.estimator, "coef_")

    @property
    def supports_global(self) -> bool:
        return self.supports_local

    def _standardize(self, x_row: np.ndarray) -> np.ndarray:
        scaler = self.pipeline.named_steps["scaler"]
        return scaler.transform(x_row.reshape(1, -1))[0]

    def _explain_local(self, x_row: np.ndarray, **kwargs: Any) -> dict[str, Any]:
        predicted_class_index = int(np.argmax(self.pipeline.predict_proba(x_row.reshape(1, -1))[0]))
        predicted_class = int(self.estimator.classes_[predicted_class_index])
        coef_row = self.estimator.coef_[predicted_class_index]
        contributions = coef_row * self._standardize(x_row)
        return {
            "method": self.method_name,
            "predicted_class": predicted_class,
            "feature_contributions": contributions.tolist(),
        }

    def _explain_global(self, **kwargs: Any) -> dict[str, Any]:
        # Mean absolute coefficient magnitude across the one-vs-rest / multinomial class rows —
        # a single, class-agnostic global importance score per feature.
        importance = np.mean(np.abs(self.estimator.coef_), axis=0)
        return {"method": self.method_name, "importance": importance.tolist()}


class ImpurityExplainer(ExplainerAdapter):
    """Native mean-decrease-in-impurity feature_importances_. Global only — a per-instance
    decomposition of a random-forest prediction requires tree-path attribution, which is not
    implemented here; local is correctly reported NOT_APPLICABLE rather than approximated.

    Known limitation (documented, not hidden): impurity-based importance is biased toward
    high-cardinality / high-variance features. See docs/experiments/STAGE09_RESOURCE_AWARE_XAI.md.
    """

    method_name = "INTRINSIC_IMPURITY"
    resource_class = RESOURCE_CLASS_INTRINSIC

    @property
    def supports_local(self) -> bool:
        return False

    @property
    def supports_global(self) -> bool:
        return isinstance(self.estimator, RandomForestClassifier) and hasattr(self.estimator, "feature_importances_")

    def _explain_local(self, x_row: np.ndarray, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError  # unreachable: supports_local is always False

    def _explain_global(self, **kwargs: Any) -> dict[str, Any]:
        return {"method": self.method_name, "importance": self.estimator.feature_importances_.tolist()}


def build_intrinsic_explainers(pipeline: Pipeline, model_id: str) -> list[ExplainerAdapter]:
    """Return every intrinsic explainer whose capability check applies to this fitted model."""
    candidates = [CoefficientExplainer(pipeline, model_id), ImpurityExplainer(pipeline, model_id)]
    return [c for c in candidates if c.supports_local or c.supports_global]
