"""Build secondary baseline figures strictly from completed CSV evidence."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/"results/baselines"; FIG=ROOT/"results/figures"; SRC=FIG/"sources"
NAMES={"MODEL-C1":"Logistic Regression","MODEL-C2":"Random Forest","MODEL-C3":"RBF-SVM","MODEL-C4":"MLP Classifier"}
def save(fig,name):
    for ext in ("png","pdf","svg"): fig.savefig(FIG/f"{name}.{ext}",dpi=300,bbox_inches="tight")
    plt.close(fig)
def main():
    raw=pd.read_csv(BASE/"predictions/fixed_origin_b1_predictions.csv"); records=[]
    fig,axes=plt.subplots(4,3,figsize=(10,12))
    for row,(model,batch) in enumerate((m,b) for m in NAMES for b in (2,6,10)):
        group=raw[(raw.model==model)&(raw.test_batch==batch)]; matrix=confusion_matrix(group.true_label,group.predicted_label,labels=range(1,7)); ax=axes.flat[row]; image=ax.imshow(matrix,cmap="Blues"); ax.set(title=f"{NAMES[model]} — B{batch}",xticks=range(6),xticklabels=range(1,7),yticks=range(6),yticklabels=range(1,7))
        for true in range(6):
            for predicted in range(6): records.append({"model":model,"test_batch":batch,"true_class":true+1,"predicted_class":predicted+1,"count":matrix[true,predicted]})
    fig.supxlabel("Predicted class"); fig.supylabel("True class"); save(fig,"confusion_matrix_evolution")
    pd.DataFrame(records).to_csv(SRC/"confusion_matrix_evolution.csv",index=False)
    summary=pd.read_csv(BASE/"fixed_origin_summary.csv"); complexity=pd.read_csv(BASE/"model_complexity.csv"); complexity["complexity_value"]=np.select([complexity.model.eq("MODEL-C1"),complexity.model.eq("MODEL-C2"),complexity.model.eq("MODEL-C3"),complexity.model.eq("MODEL-C4")],[complexity.coefficient_count,complexity.total_nodes,complexity.support_vector_values,complexity.parameter_count],default=np.nan); complexity["complexity_definition"]=np.select([complexity.model.eq("MODEL-C1"),complexity.model.eq("MODEL-C2"),complexity.model.eq("MODEL-C3"),complexity.model.eq("MODEL-C4")],["coefficient count","total tree nodes","support-vector scalar values","parameter count"],default="unknown"); source=summary.merge(complexity[["model","complexity_value","complexity_definition","serialized_host_bytes"]],on="model"); source.to_csv(SRC/"figure_15_accuracy_robustness_complexity.csv",index=False)
    fig,ax=plt.subplots(figsize=(8,5)); ax.scatter(source.complexity_value,source.mean_future_macro_f1,s=60)
    for _,r in source.iterrows(): ax.annotate(NAMES[r.model],(r.complexity_value,r.mean_future_macro_f1),fontsize=8)
    ax.set_xscale("log"); ax.set(xlabel="Model-specific structural complexity (log scale; see source definition)",ylabel="Mean future Macro-F1",title="Performance–Robustness–Complexity Comparison"); save(fig,"figure_15_complexity_comparison")
    sensor=pd.read_csv(BASE/"sensor_drift_vs_importance.csv"); sensor.to_csv(SRC/"sensor_drift_vs_importance.csv",index=False); fig,ax=plt.subplots(figsize=(7,5)); ax.scatter(sensor.drift_score,sensor.importance_score)
    for _,r in sensor.iterrows(): ax.annotate(int(r.sensor),(r.drift_score,r.importance_score),fontsize=8)
    ax.set(xlabel="Mean feature drift",ylabel="Mean permutation importance",title="Sensor-level Drift vs Importance"); save(fig,"sensor_drift_vs_importance")
if __name__=="__main__": main()
