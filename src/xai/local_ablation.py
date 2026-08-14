"""Single-feature-ablation local explanation — model-agnostic, off-device.

Deliberately NOT SHAP and NOT LIME: no Shapley-value coalition sampling, no local surrogate
regression. For a given instance and its predicted class, each feature is independently reset
to a fixed training-set baseline value (the Batch-1 / training-split per-feature mean — the
only data a FIXED_ORIGIN-trained model ever legitimately saw) and the drop in predicted-class
probability is recorded as that feature's local contribution. This is the simplest defensible
model-agnostic local attribution method; see SHAP POLICY / LIME POLICY in
docs/experiments/STAGE09_RESOURCE_AWARE_XAI.md for why a heavier method was not introduced here.
"""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.pipeline import Pipeline

from .base import RESOURCE_CLASS_ABLATION, ExplainerAdapter


class SingleFeatureAblationExplainer(ExplainerAdapter):
    method_name = "SINGLE_FEATURE_ABLATION_LOCAL"
    resource_class = RESOURCE_CLASS_ABLATION

    def __init__(self, pipeline: Pipeline, model_id: str, baseline: np.ndarray):
        # Checked before super().__init__() so an incompatible object raises a clear ValueError
        # here rather than an opaque AttributeError from the base class's named_steps access.
        if not hasattr(pipeline, "predict_proba"):
            raise ValueError(f"{model_id} pipeline lacks predict_proba; ablation explainer requires it")
        super().__init__(pipeline, model_id)
        self.baseline = baseline  # per-feature baseline value, shape (n_features,)

    @property
    def supports_local(self) -> bool:
        return hasattr(self.pipeline, "predict_proba")

    @property
    def supports_global(self) -> bool:
        return False  # this method is defined per-instance; use PermutationImportanceExplainer for global

    def _explain_global(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError  # unreachable: supports_global is always False

    def _explain_local(self, x_row: np.ndarray, **kwargs: Any) -> dict[str, Any]:
        n_features = x_row.shape[0]
        base_proba = self.pipeline.predict_proba(x_row.reshape(1, -1))[0]
        predicted_class_index = int(np.argmax(base_proba))
        predicted_class = int(self.pipeline.classes_[predicted_class_index])
        base_prob = float(base_proba[predicted_class_index])

        # Vectorized: build one perturbed copy per feature in a single (n_features, n_features)
        # batch, ablating one feature per row, then one predict_proba call for the whole batch.
        perturbed = np.tile(x_row, (n_features, 1))
        np.fill_diagonal(perturbed, self.baseline)
        ablated_proba = self.pipeline.predict_proba(perturbed)[:, predicted_class_index]
        contributions = base_prob - ablated_proba  # positive => feature supports predicted class

        return {
            "method": self.method_name,
            "predicted_class": predicted_class,
            "base_probability": base_prob,
            "feature_contributions": contributions.tolist(),
        }
