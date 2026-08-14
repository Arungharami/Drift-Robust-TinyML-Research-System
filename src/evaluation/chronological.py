"""Leakage-guarded execution primitives."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

@dataclass(frozen=True)
class FitScope:
    train_batches: tuple[int, ...]
    test_batch: int | str
    protocol: str
    def validate(self) -> None:
        if self.protocol != "IID_DIAGNOSTIC_ONLY" and (not self.train_batches or max(self.train_batches) >= int(self.test_batch)): raise ValueError("Temporal leakage: training must precede test")

def fit_predict(model: Pipeline, x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, y_test: np.ndarray, scope: FitScope, experiment_id: str, model_id: str, sample_ids: list[str], provenance: dict[str, str]) -> tuple[pd.DataFrame, float]:
    scope.validate(); assert len(set(sample_ids)) == len(sample_ids)
    started=perf_counter(); model.fit(x_train,y_train); duration=perf_counter()-started
    prediction=model.predict(x_test)
    frame=pd.DataFrame({"experiment_id":experiment_id,"model":model_id,"protocol":scope.protocol,"train_batches":";".join(map(str,scope.train_batches)),"test_batch":scope.test_batch,"sample_index":sample_ids,"true_label":y_test,"predicted_label":prediction,"correct":prediction==y_test,"environment":provenance["environment"],"git_commit":provenance["git_commit"]})
    if hasattr(model,"predict_proba"):
        probabilities=model.predict_proba(x_test)
        for index,label in enumerate(model.classes_): frame[f"probability_class_{label}"]=probabilities[:,index]
    return frame,duration
