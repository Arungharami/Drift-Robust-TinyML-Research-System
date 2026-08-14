"""ExplainerAdapter interface and capability detection.

Every explanation method implements this interface so run_stage09.py can treat methods
uniformly while still being honest about which (model, method) pairs are actually applicable —
a model is never forced through an explanation method it does not scientifically support.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from sklearn.pipeline import Pipeline

# Resource classes describe the *cost* of computing the explanation itself, not a claim about
# TinyML deployability. Deployability is only established by Stages 13-19 (quantization,
# embedded export, physical measurement).
RESOURCE_CLASS_INTRINSIC = "INTRINSIC_ZERO_COST"  # reads already-fitted parameters, no extra inference
RESOURCE_CLASS_PERMUTATION = "MODEL_AGNOSTIC_MULTI_INFERENCE"  # O(features x repeats) re-inferences
RESOURCE_CLASS_ABLATION = "MODEL_AGNOSTIC_SINGLE_INSTANCE_MULTI_INFERENCE"  # O(features) re-inferences per instance
RESOURCE_CLASS_REFERENCE = "OFF_DEVICE_REFERENCE"  # explicitly not resource-aware; reference/comparison only


class ExplainerAdapter(ABC):
    """Common interface for every Stage-09 explanation method."""

    method_name: str
    resource_class: str

    def __init__(self, pipeline: Pipeline, model_id: str):
        self.pipeline = pipeline
        self.model_id = model_id
        self.estimator = pipeline.named_steps["model"]

    @property
    @abstractmethod
    def supports_local(self) -> bool:
        """Whether explain_local is scientifically applicable to this fitted model."""

    @property
    @abstractmethod
    def supports_global(self) -> bool:
        """Whether explain_global is scientifically applicable to this fitted model."""

    def explain_local(self, x_row: np.ndarray, **kwargs: Any) -> dict[str, Any]:
        if not self.supports_local:
            raise NotApplicableError(
                f"{self.method_name} does not support local explanations for {self.model_id} "
                "(capability not detected on the fitted estimator)"
            )
        return self._explain_local(x_row, **kwargs)

    def explain_global(self, **kwargs: Any) -> dict[str, Any]:
        if not self.supports_global:
            raise NotApplicableError(
                f"{self.method_name} does not support global explanations for {self.model_id} "
                "(capability not detected on the fitted estimator)"
            )
        return self._explain_global(**kwargs)

    @abstractmethod
    def _explain_local(self, x_row: np.ndarray, **kwargs: Any) -> dict[str, Any]: ...

    @abstractmethod
    def _explain_global(self, **kwargs: Any) -> dict[str, Any]: ...


class NotApplicableError(RuntimeError):
    """Raised when a (model, method) pair is not scientifically applicable.

    Callers must catch this and record NOT_APPLICABLE in the manifest rather than letting the
    whole Stage-09 run fail — see Failure Rule in docs/experiments/STAGE09_RESOURCE_AWARE_XAI.md.
    """
