"""Execute checkpoint-2 classical protocols and save prediction-first evidence."""
from __future__ import annotations
import json, platform, subprocess
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
import joblib, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd, sklearn, yaml
from scipy.stats import spearmanr
from sklearn.inspection import permutation_importance
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from src.data.loader import batch_number, discover_batches, load_batch
from src.evaluation.chronological import FitScope, fit_predict
from src.evaluation.metrics import metrics_from_predictions
from src.evaluation.statistics import spearman_summary
from src.models.classical import build_model, complexity_metadata, serialize_model
from src.utils.hashing import sha256_file, stable_hash
from src.utils.registry import FIELDS, append_experiment

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"results/baselines"; PRED=OUT/"predictions"; FIG=ROOT/"results/figures"; SRC=FIG/"sources"; TABLE=ROOT/"results/tables"; MODEL_DIR=ROOT/"artifacts/models"
MODEL_NAMES={"MODEL-C1":"Logistic Regression","MODEL-C2":"Random Forest","MODEL-C3":"RBF-SVM","MODEL-C4":"MLP Classifier"}

def git_commit()->str: return subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
def save_fig(fig:plt.Figure,name:str)->None:
    for ext in ("png","pdf","svg"): fig.savefig(FIG/f"{name}.{ext}",dpi=300,bbox_inches="tight")
    plt.close(fig)
def export_table(frame:pd.DataFrame,stem:str)->None:
    TABLE.mkdir(parents=True,exist_ok=True); frame.to_csv(TABLE/f"{stem}.csv",index=False)
    display=frame.fillna("").astype(str); lines=["| "+" | ".join(display.columns)+" |","|"+"|".join(["---"]*len(display.columns))+"|"]+[
        "| "+" | ".join(row)+" |" for row in display.itertuples(index=False,name=None)]
    (TABLE/f"{stem}.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    escape=lambda value:str(value).replace("_","\\_").replace("%","\\%")
    latex=["\\begin{tabular}{"+"l"*len(display.columns)+"}"," \\hline"," & ".join(map(escape,display.columns))+" \\\\"," \\hline"]+[" & ".join(map(escape,row))+" \\\\" for row in display.itertuples(index=False,name=None)]+[" \\hline","\\end{tabular}"]
    (TABLE/f"{stem}.tex").write_text("\n".join(latex)+"\n",encoding="utf-8")
def batches()->dict[int,tuple[np.ndarray,np.ndarray]]: return {batch_number(p):load_batch(p) for p in discover_batches(ROOT/"data/raw")}
def joined(data:dict[int,tuple[np.ndarray,np.ndarray]], ids:list[int])->tuple[np.ndarray,np.ndarray,list[str]]:
    return np.vstack([data[b][0] for b in ids]),np.concatenate([data[b][1] for b in ids]),[f"B{b}:{i}" for b in ids for i in range(len(data[b][1]))]
def evaluate_saved(path:Path,class_order:list[int])->tuple[pd.DataFrame,pd.DataFrame]:
    raw=pd.read_csv(path); summaries=[]; classes=[]
    for (exp,model,protocol,batch),group in raw.groupby(["experiment_id","model","protocol","test_batch"],sort=False):
        summary,detail=metrics_from_predictions(group,class_order); summaries.append({"experiment_id":exp,"model":model,"protocol":protocol,"test_batch":batch,**summary}); detail.insert(0,"test_batch",batch); detail.insert(0,"protocol",protocol); detail.insert(0,"model",model); detail.insert(0,"experiment_id",exp); classes.append(detail)
    return pd.DataFrame(summaries),pd.concat(classes,ignore_index=True)
def provenance(config:dict)->dict:
    validation=json.loads((ROOT/"results/reproducibility/dataset_validation.json").read_text()); manifest=json.loads((ROOT/"data/manifests/dataset_manifest.json").read_text(encoding="utf-8-sig")); commit=git_commit()
    return {"dataset_hash":validation["dataset_hash"],"archive_sha256":manifest["archive_sha256"],"manifest_hash":sha256_file(ROOT/"data/manifests/dataset_manifest.json"),"config_hash":stable_hash(config),"git_commit":commit,"environment":"results/reproducibility/environment.json","python":platform.python_version(),"scikit_learn":sklearn.__version__,"timestamp_utc":datetime.now(timezone.utc).isoformat()}
def execute_protocol(data,config,prov,protocol:str)->tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    rows=[]; training=[]; complexity=[]; seed=config["seed"]
    for model_id in MODEL_NAMES:
        experiment_id={"FIXED_ORIGIN_B1":"BASE-FIXED","EXPANDING_WINDOW":"BASE-EXPAND","IID_DIAGNOSTIC_ONLY":"BASE-IID"}[protocol]+f"-{model_id[-2:]}-001"
        if protocol=="IID_DIAGNOSTIC_ONLY":
            x,y,sids=joined(data,list(range(1,11))); indices=np.arange(len(y)); train_idx,test_idx=train_test_split(indices,test_size=config["iid_diagnostic"]["test_size"],stratify=y,random_state=seed)
            jobs=[(tuple(),"IID",x[train_idx],y[train_idx],x[test_idx],y[test_idx],[sids[i] for i in test_idx])]
        else:
            jobs=[]
            for test_batch in range(2,11):
                train_batches=(1,) if protocol=="FIXED_ORIGIN_B1" else tuple(range(1,test_batch)); xtr,ytr,_=joined(data,list(train_batches)); xte,yte,ids=joined(data,[test_batch]); jobs.append((train_batches,test_batch,xtr,ytr,xte,yte,ids))
        for train_batches,test_batch,xtr,ytr,xte,yte,ids in jobs:
            model=build_model(model_id,config,seed); scope=FitScope(train_batches,test_batch,protocol); frame,duration=fit_predict(model,xtr,ytr,xte,yte,scope,experiment_id,model_id,ids,prov); rows.append(frame)
            training.append({"experiment_id":experiment_id,"model":model_id,"protocol":protocol,"test_batch":test_batch,"train_batches":";".join(map(str,train_batches)),"training_duration_seconds":duration,"seed":seed})
            if protocol=="FIXED_ORIGIN_B1" and test_batch==2:
                artifact=MODEL_DIR/f"{experiment_id}.joblib"; serialize_model(model,artifact); complexity.append({"experiment_id":experiment_id,"model":model_id,"model_name":MODEL_NAMES[model_id],**complexity_metadata(model,artifact)})
    raw=pd.concat(rows,ignore_index=True); path=PRED/f"{protocol.lower()}_predictions.csv"; raw.to_csv(path,index=False)
    metric,classes=evaluate_saved(path,config["class_order"]); return metric,classes,pd.DataFrame(training) if protocol!="FIXED_ORIGIN_B1" else pd.DataFrame(complexity)
def figures(fixed,expand,iid,classes,summary,assoc,feature):
    plt.style.use("seaborn-v0_8-whitegrid")
    for metric,num,title in (("accuracy",6,"Chronological Accuracy by Model"),("macro_f1",7,"Chronological Macro-F1 by Model"),("balanced_accuracy",8,"Balanced Accuracy Across Drift")):
        source=fixed[["model","test_batch",metric]]; source.to_csv(SRC/f"figure_{num}_{metric}.csv",index=False); fig,ax=plt.subplots(figsize=(8,4.5))
        for model,g in source.groupby("model"): ax.plot(g.test_batch,g[metric],marker="o",label=MODEL_NAMES[model])
        ax.set(xlabel="Future batch",ylabel=metric.replace('_',' ').title(),title=title,ylim=(0,1)); ax.legend(fontsize=8); save_fig(fig,f"figure_{num}_{metric}")
    source=summary[["model","b2_to_b10_accuracy_drop_pp"]]; source.to_csv(SRC/"figure_9_degradation.csv",index=False); fig,ax=plt.subplots(figsize=(7,4)); ax.bar([MODEL_NAMES[x] for x in source.model],source.b2_to_b10_accuracy_drop_pp); ax.set(ylabel="B2 minus B10 accuracy (percentage points)",title="B2 to B10 Performance Degradation"); ax.tick_params(axis="x",rotation=20); save_fig(fig,"figure_9_degradation")
    error=classes.assign(error=1-classes.recall).groupby(["gas_class","test_batch"],as_index=False).error.mean(); matrix=error.pivot(index="gas_class",columns="test_batch",values="error"); matrix.to_csv(SRC/"figure_10_class_error_heatmap.csv"); fig,ax=plt.subplots(figsize=(8,4)); im=ax.imshow(matrix,aspect="auto",vmin=0,vmax=1,cmap="magma"); fig.colorbar(im,ax=ax,label="Mean recall error across models"); ax.set(xticks=range(9),xticklabels=range(2,11),yticks=range(6),yticklabels=range(1,7),xlabel="Batch",ylabel="Gas class",title="Class × Chronological Batch Error"); save_fig(fig,"figure_10_class_error_heatmap")
    compare=fixed.merge(expand,on=["model","test_batch"],suffixes=("_fixed","_expanding")); compare.to_csv(SRC/"figure_11_fixed_vs_expanding.csv",index=False); fig,axes=plt.subplots(2,2,figsize=(10,7),sharex=True,sharey=True)
    for ax,(model,g) in zip(axes.flat,compare.groupby("model")): ax.plot(g.test_batch,g.accuracy_fixed,marker="o",label="Fixed"); ax.plot(g.test_batch,g.accuracy_expanding,marker="s",label="Expanding"); ax.set_title(MODEL_NAMES[model]); ax.legend()
    fig.supxlabel("Batch"); fig.supylabel("Accuracy"); save_fig(fig,"figure_11_fixed_vs_expanding")
    iid_compare=iid.merge(fixed.groupby("model",as_index=False)[["accuracy","macro_f1","balanced_accuracy"]].mean(),on="model",suffixes=("_iid","_fixed_mean")); iid_compare.to_csv(SRC/"figure_12_iid_vs_chronological.csv",index=False); fig,ax=plt.subplots(figsize=(8,4)); x=np.arange(4); ax.bar(x-.18,iid_compare.accuracy_iid,.36,label="IID diagnostic"); ax.bar(x+.18,iid_compare.accuracy_fixed_mean,.36,label="Fixed-origin mean"); ax.set(xticks=x,xticklabels=[MODEL_NAMES[x] for x in iid_compare.model],ylabel="Accuracy",title="IID vs Chronological Evaluation",ylim=(0,1)); ax.tick_params(axis="x",rotation=15); ax.legend(); save_fig(fig,"figure_12_iid_vs_chronological")
    assoc.to_csv(SRC/"figure_13_drift_vs_performance.csv",index=False); fig,axes=plt.subplots(1,3,figsize=(12,3.8));
    for ax,metric in zip(axes,["accuracy","macro_f1","balanced_accuracy"]):
        for model,g in assoc.groupby("model"): ax.scatter(g.drift_score,g[metric],label=MODEL_NAMES[model]); ax.set(xlabel="Median normalized Wasserstein drift",ylabel=metric.replace('_',' '))
    axes[0].legend(fontsize=6); save_fig(fig,"figure_13_drift_vs_performance")
    feature.to_csv(SRC/"figure_14_feature_drift_vs_importance.csv",index=False); fig,ax=plt.subplots(figsize=(7,5)); ax.scatter(feature.drift_score,feature.importance_score,s=14,alpha=.65); ax.axvline(feature.drift_score.median(),ls="--",c="grey"); ax.axhline(feature.importance_score.median(),ls="--",c="grey");
    for _,r in feature.nlargest(10,"importance_score").iterrows(): ax.annotate(int(r.feature),(r.drift_score,r.importance_score),fontsize=7)
    ax.set(xlabel="Mean normalized Wasserstein drift",ylabel="Permutation importance (macro-F1 decrease)",title="Feature Drift vs Predictive Importance"); save_fig(fig,"figure_14_feature_drift_vs_importance")
def main():
    for p in (OUT,PRED,FIG,SRC,TABLE,MODEL_DIR): p.mkdir(parents=True,exist_ok=True)
    config=yaml.safe_load((ROOT/"configs/classical_baselines.yaml").read_text()); prov=provenance(config); data=batches()
    fixed,classes,complexity=execute_protocol(data,config,prov,"FIXED_ORIGIN_B1"); fixed.to_csv(OUT/"fixed_origin_metrics.csv",index=False); classes.to_csv(OUT/"class_performance_by_batch.csv",index=False); complexity.to_csv(OUT/"model_complexity.csv",index=False)
    expand,expand_classes,expand_training=execute_protocol(data,config,prov,"EXPANDING_WINDOW"); expand.to_csv(OUT/"expanding_window_metrics.csv",index=False)
    iid,iid_classes,iid_training=execute_protocol(data,config,prov,"IID_DIAGNOSTIC_ONLY"); iid.to_csv(OUT/"iid_diagnostic_metrics.csv",index=False)
    summary=[]
    for model,g in fixed.groupby("model"):
        b2=g[g.test_batch==2].iloc[0]; b10=g[g.test_batch==10].iloc[0]; summary.append({"model":model,"b2_accuracy":b2.accuracy,"b10_accuracy":b10.accuracy,"b2_to_b10_accuracy_drop_pp":100*(b2.accuracy-b10.accuracy),"mean_future_accuracy":g.accuracy.mean(),"mean_future_macro_f1":g.macro_f1.mean(),"mean_future_balanced_accuracy":g.balanced_accuracy.mean(),"worst_batch":g.loc[g.accuracy.idxmin(),"test_batch"],"best_batch":g.loc[g.accuracy.idxmax(),"test_batch"]})
    summary=pd.DataFrame(summary); summary.to_csv(OUT/"fixed_origin_summary.csv",index=False)
    comparison=expand.merge(fixed,on=["model","test_batch"],suffixes=("_expanding","_fixed"));
    for m in ("accuracy","macro_f1","balanced_accuracy"): comparison[f"{m}_change"]=comparison[f"{m}_expanding"]-comparison[f"{m}_fixed"]
    comparison.to_csv(OUT/"expanding_vs_fixed.csv",index=False)
    iid_gap=iid.merge(fixed.groupby("model",as_index=False)[["accuracy","macro_f1","balanced_accuracy"]].mean(),on="model",suffixes=("_iid","_fixed_mean"));
    for m in ("accuracy","macro_f1","balanced_accuracy"): iid_gap[f"{m}_gap"]=iid_gap[f"{m}_iid"]-iid_gap[f"{m}_fixed_mean"]
    iid_gap.to_csv(OUT/"iid_generalization_gap.csv",index=False)
    drift=pd.read_csv(ROOT/"results/drift/global_drift_by_batch.csv"); drift=drift[drift.metric=="normalized_wasserstein"].rename(columns={"comparison_batch":"test_batch","median_feature_drift":"drift_score"}); assoc=fixed.merge(drift[["test_batch","drift_score"]],on="test_batch"); assoc.to_csv(OUT/"drift_performance_by_batch.csv",index=False); correlations=[]
    for model,g in assoc.groupby("model"):
        for metric in ("accuracy","macro_f1","balanced_accuracy"): correlations.append({"model":model,"performance_metric":metric,**spearman_summary(g.drift_score.to_numpy(),g[metric].to_numpy())})
    correlations=pd.DataFrame(correlations); correlations.to_csv(OUT/"drift_performance_correlations.csv",index=False)
    rf=joblib.load(MODEL_DIR/"BASE-FIXED-C2-001.joblib"); x2,y2,_=joined(data,[2]); pi=permutation_importance(rf,x2,y2,scoring="f1_macro",n_repeats=config["feature_importance"]["repeats"],random_state=config["seed"],n_jobs=-1); fd=pd.read_csv(ROOT/"results/drift/feature_drift_by_batch.csv"); fd=fd[fd.metric=="normalized_wasserstein"].groupby(["feature","sensor"],as_index=False).value.mean().rename(columns={"value":"drift_score"}); importance=pd.DataFrame({"feature":range(1,129),"importance_score":pi.importances_mean}); feature=fd.merge(importance,on="feature"); feature["importance_method"]="permutation_importance_macro_f1_on_batch_2"; feature["rank_drift"]=feature.drift_score.rank(ascending=False,method="min").astype(int); feature["rank_importance"]=feature.importance_score.rank(ascending=False,method="min").astype(int); dh=feature.drift_score>=feature.drift_score.median(); ih=feature.importance_score>=feature.importance_score.median(); feature["quadrant"]=np.select([ih&~dh,ih&dh,~ih&~dh,~ih&dh],["HIGH_IMPORTANCE_LOW_DRIFT","HIGH_IMPORTANCE_HIGH_DRIFT","LOW_IMPORTANCE_LOW_DRIFT","LOW_IMPORTANCE_HIGH_DRIFT"],default="UNCLASSIFIED"); feature.to_csv(OUT/"feature_drift_vs_importance.csv",index=False)
    sensor=feature.groupby("sensor",as_index=False).agg(drift_score=("drift_score","mean"),importance_score=("importance_score","mean")); sensor["mapping"]="16 sensors × 8 contiguous features per UCI feature construction"; sensor.to_csv(OUT/"sensor_drift_vs_importance.csv",index=False)
    figures(fixed,expand,iid,classes,summary,assoc,feature)
    export_table(summary,"table_3_fixed_origin_baselines"); export_table(fixed,"table_4_per_batch_performance"); export_table(classes,"table_5_class_performance"); export_table(comparison,"table_6_expanding_window"); export_table(iid_gap,"table_7_iid_diagnostic"); export_table(complexity,"table_8_model_complexity")
    (OUT/"run_provenance.json").write_text(json.dumps({**prov,"seed":config["seed"],"status":"COMPLETED"},indent=2),encoding="utf-8")
    for protocol,prefix,metrics in (("FIXED_ORIGIN_B1","BASE-FIXED",OUT/"fixed_origin_metrics.csv"),("EXPANDING_WINDOW","BASE-EXPAND",OUT/"expanding_window_metrics.csv"),("IID_DIAGNOSTIC_ONLY","BASE-IID",OUT/"iid_diagnostic_metrics.csv")):
        for model in MODEL_NAMES:
            rec=dict.fromkeys(FIELDS,""); rec.update({"experiment_id":f"{prefix}-{model[-2:]}-001","timestamp":prov["timestamp_utc"],"research_question":"Classical temporal generalization and adaptation","protocol":protocol,"model":model,"representation":"RAW_128D_STANDARDIZED","train_batches":"1" if protocol=="FIXED_ORIGIN_B1" else "HISTORICAL" if protocol=="EXPANDING_WINDOW" else "STRATIFIED_RANDOM","test_batches":"2-10" if protocol!="IID_DIAGNOSTIC_ONLY" else "20_PERCENT_RANDOM","seed":config["seed"],"dataset_hash":prov["dataset_hash"],"split_hash":stable_hash({"protocol":protocol,"seed":config["seed"]}),"config_hash":prov["config_hash"],"git_commit":prov["git_commit"],"environment":prov["environment"],"status":"COMPLETED","metrics_artifact":str(metrics.relative_to(ROOT)),"model_artifact":str((MODEL_DIR/f"BASE-FIXED-{model[-2:]}-001.joblib").relative_to(ROOT)) if protocol=="FIXED_ORIGIN_B1" else "","notes":"Metrics recomputed from saved raw predictions."}); append_experiment(ROOT/"results/registry/experiment_registry.csv",rec)
    print(json.dumps({"status":"COMPLETED","fixed_prediction_rows":sum(1 for _ in open(PRED/"fixed_origin_b1_predictions.csv",encoding="utf-8"))-1,"expanding_prediction_rows":sum(1 for _ in open(PRED/"expanding_window_predictions.csv",encoding="utf-8"))-1,"iid_prediction_rows":sum(1 for _ in open(PRED/"iid_diagnostic_only_predictions.csv",encoding="utf-8"))-1},indent=2))
if __name__=="__main__": main()
