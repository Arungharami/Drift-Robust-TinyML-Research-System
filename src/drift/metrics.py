"""Interpretable univariate drift metrics."""
from __future__ import annotations
import numpy as np
from scipy.stats import wasserstein_distance

def standardized_mean_shift(reference: np.ndarray, comparison: np.ndarray, epsilon: float = 1e-12) -> float:
    reference = np.asarray(reference, float); comparison = np.asarray(comparison, float)
    pooled = np.sqrt((reference.var(ddof=1) + comparison.var(ddof=1)) / 2)
    return float(abs(reference.mean() - comparison.mean()) / max(pooled, epsilon))

def normalized_wasserstein(reference: np.ndarray, comparison: np.ndarray, epsilon: float = 1e-12) -> float:
    scale = max(float(np.std(reference, ddof=1)), epsilon)
    return float(wasserstein_distance(reference, comparison) / scale)
