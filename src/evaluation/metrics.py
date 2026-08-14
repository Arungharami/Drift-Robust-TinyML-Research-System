"""Metrics computed exclusively from raw prediction records."""
from __future__ import annotations
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, precision_recall_fscore_support

def metrics_from_predictions(frame: pd.DataFrame, class_order: list[int]) -> tuple[dict[str, float], pd.DataFrame]:
    y_true=frame.true_label; y_pred=frame.predicted_label
    precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=class_order, zero_division=0)
    macro = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    summary={"accuracy":accuracy_score(y_true,y_pred),"macro_f1":macro[2],"balanced_accuracy":balanced_accuracy_score(y_true,y_pred),"macro_precision":macro[0],"macro_recall":macro[1]}
    classes=pd.DataFrame({"gas_class":class_order,"precision":precision,"recall":recall,"f1":f1,"support":support})
    return summary, classes
