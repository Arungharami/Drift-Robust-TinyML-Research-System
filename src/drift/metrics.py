"""Interpretable univariate drift metrics."""
from __future__ import annotations
import numpy as np
from scipy.stats import wasserstein_distance

def _validated_samples(reference, comparison, epsilon):
    reference = np.asarray(reference, dtype=float)
    comparison = np.asarray(comparison, dtype=float)
    for sample in (reference, comparison):
        if sample.ndim != 1 or len(sample) < 2 or not np.isfinite(sample).all():
            raise ValueError("Drift metrics require finite 1-D samples with at least two values")
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be finite and positive")
    return reference, comparison

def standardized_mean_shift(reference: np.ndarray, comparison: np.ndarray, epsilon: float = 1e-12) -> float:
    reference, comparison = _validated_samples(reference, comparison, epsilon)
    pooled = np.sqrt((reference.var(ddof=1) + comparison.var(ddof=1)) / 2)
    return float(abs(reference.mean() - comparison.mean()) / max(pooled, epsilon))

def normalized_wasserstein(reference: np.ndarray, comparison: np.ndarray, epsilon: float = 1e-12) -> float:
    reference, comparison = _validated_samples(reference, comparison, epsilon)
    scale = max(float(np.std(reference, ddof=1)), epsilon)
    return float(wasserstein_distance(reference, comparison) / scale)
