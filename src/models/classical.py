"""Frozen classical baseline factories and defensible complexity profiles."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

def build_model(model_id: str, config: dict[str, Any], seed: int) -> Pipeline:
    params = config["models"][model_id]
    if model_id == "MODEL-C1":
        estimator = LogisticRegression(C=params["C"], solver=params["solver"], max_iter=params["max_iter"], random_state=seed)
    elif model_id == "MODEL-C2":
        estimator = RandomForestClassifier(n_estimators=params["n_estimators"], max_depth=params["max_depth"], min_samples_leaf=params["min_samples_leaf"], n_jobs=params["n_jobs"], random_state=seed)
    elif model_id == "MODEL-C3":
        estimator = SVC(C=params["C"], gamma=params["gamma"], probability=params["probability"], max_iter=params["max_iter"], random_state=seed)
    elif model_id == "MODEL-C4":
        estimator = MLPClassifier(hidden_layer_sizes=tuple(params["hidden_layer_sizes"]), activation=params["activation"], learning_rate_init=params["learning_rate_init"], alpha=params["alpha"], max_iter=params["max_iter"], early_stopping=params["early_stopping"], validation_fraction=params["validation_fraction"], n_iter_no_change=params["n_iter_no_change"], random_state=seed)
    else: raise KeyError(model_id)
    return Pipeline([("scaler", StandardScaler()), ("model", estimator)])

def complexity_metadata(pipeline: Pipeline, artifact: Path) -> dict[str, Any]:
    model = pipeline.named_steps["model"]
    result: dict[str, Any] = {"serialized_host_bytes": artifact.stat().st_size, "complexity_unit": "model-specific host structure"}
    if isinstance(model, LogisticRegression): result.update(parameter_count=int(model.coef_.size + model.intercept_.size), coefficient_count=int(model.coef_.size))
    elif isinstance(model, RandomForestClassifier): result.update(tree_count=len(model.estimators_), total_nodes=sum(t.tree_.node_count for t in model.estimators_), max_tree_depth=max(t.tree_.max_depth for t in model.estimators_))
    elif isinstance(model, SVC): result.update(support_vector_count=int(model.support_vectors_.shape[0]), support_vector_values=int(model.support_vectors_.size))
    elif isinstance(model, MLPClassifier): result.update(parameter_count=int(sum(x.size for x in model.coefs_) + sum(x.size for x in model.intercepts_)), layer_dimensions=list(model.n_layers_ and [model.coefs_[0].shape[0], *[x.shape[1] for x in model.coefs_]]))
    return result

def serialize_model(pipeline: Pipeline, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); joblib.dump(pipeline, path)
