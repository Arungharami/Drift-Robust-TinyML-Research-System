"""Deterministic scientific reference chain for future embedded equivalence tests.

This module only loads existing frozen pipelines. It never fits, converts, or exports a model.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def model_path(model_id: str) -> Path:
    return ROOT / f"artifacts/models/BASE-FIXED-{model_id.replace('MODEL-', '')}-001.joblib"


def load_frozen_pipeline(model_id: str):
    pipeline = joblib.load(model_path(model_id))
    if not hasattr(pipeline, "named_steps") or not {"scaler", "model"}.issubset(pipeline.named_steps):
        raise ValueError(f"{model_id} is not the expected frozen scaler→estimator pipeline")
    return pipeline


def reference_inference(model_id: str, raw_features: np.ndarray) -> dict[str, Any]:
    pipeline = load_frozen_pipeline(model_id)
    raw = np.asarray(raw_features, dtype=np.float64).reshape(1, -1)
    if raw.shape[1] != 128:
        raise ValueError(f"Expected 128 raw features, received {raw.shape[1]}")
    scaler = pipeline.named_steps["scaler"]
    estimator = pipeline.named_steps["model"]
    transformed = scaler.transform(raw)
    prediction = estimator.predict(transformed)
    decision = estimator.decision_function(transformed) if hasattr(estimator, "decision_function") else None
    probability = estimator.predict_proba(transformed) if hasattr(estimator, "predict_proba") else None
    # Tree ensembles expose vote-normalized class probabilities rather than decision_function;
    # retain that vector as their defined class-score representation as well as probability.
    if decision is None and probability is not None:
        decision = probability.copy()
    if probability is not None:
        confidence = float(np.max(probability[0]))
        order = np.argsort(probability[0])
        margin = float(probability[0, order[-1]] - probability[0, order[-2]])
        competing = estimator.classes_[order[-2]]
    else:
        scores = np.asarray(decision).reshape(-1)
        order = np.argsort(scores)
        confidence = float(scores[order[-1]])
        margin = float(scores[order[-1]] - scores[order[-2]])
        competing = estimator.classes_[order[-2]]
    return {
        "model_id": model_id,
        "raw_features": raw[0],
        "transformed_features": transformed[0],
        "decision_scores": None if decision is None else np.asarray(decision).reshape(-1),
        "probabilities": None if probability is None else np.asarray(probability).reshape(-1),
        "predicted_label": int(prediction[0]),
        "confidence": confidence,
        "margin": margin,
        "nearest_competing_class": int(competing),
        "model_sha256": hashlib.sha256(model_path(model_id).read_bytes()).hexdigest(),
    }
