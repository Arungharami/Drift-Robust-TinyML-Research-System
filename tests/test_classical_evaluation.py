from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from src.evaluation.chronological import FitScope, fit_predict
from src.evaluation.metrics import metrics_from_predictions
from src.models.classical import complexity_metadata, serialize_model

def tiny_pipeline(): return Pipeline([("scaler",StandardScaler()),("model",LogisticRegression())])
def test_preprocessor_fits_training_scope_only():
    x_train=np.array([[0.],[2.],[0.],[2.]]); y=np.array([1,2,1,2]); x_test=np.array([[100.],[200.]])
    model=tiny_pipeline(); frame,_=fit_predict(model,x_train,y,x_test,np.array([1,2]),FitScope((1,),2,"FIXED_ORIGIN_B1"),"E","M",["B2:0","B2:1"],{"environment":"e","git_commit":"g"})
    assert model.named_steps["scaler"].mean_[0]==1 and len(frame)==2
def test_prediction_metrics_recompute():
    frame=pd.DataFrame({"true_label":[1,1,2,2],"predicted_label":[1,2,2,2]}); summary,classes=metrics_from_predictions(frame,[1,2]); assert summary["accuracy"]==.75 and classes.support.sum()==4
def test_iid_label_is_explicit():
    FitScope(tuple(),"IID","IID_DIAGNOSTIC_ONLY").validate()
def test_complexity_metadata(tmp_path:Path):
    model=tiny_pipeline().fit([[0],[1],[2],[3]],[1,1,2,2]); artifact=tmp_path/"m.joblib"; serialize_model(model,artifact); metadata=complexity_metadata(model,artifact); assert metadata["parameter_count"]>0 and metadata["serialized_host_bytes"]>0
