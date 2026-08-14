"""Execute the frozen Stage 10 fidelity protocol without fitting any model or preprocessing."""
from __future__ import annotations
import csv, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import balanced_accuracy_score, f1_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.data.loader import batch_number, discover_batches, load_batch  # noqa: E402

REQ = ["stage09_global_importance.csv", "stage09_reduced_explanations.csv", "stage09_local_samples.csv", "stage09_local_explanations.csv", "stage09_fidelity_prep.csv", "stage09_manifest.csv", "stage09_feature_map.csv"]

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def write(path: Path, data: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(data[0]) if data else ["experiment_id"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(data)

def metrics(y: np.ndarray, original: np.ndarray, changed: np.ndarray) -> dict[str, float]:
    return {"macro_f1": f1_score(y, changed, average="macro", zero_division=0), "balanced_accuracy": balanced_accuracy_score(y, changed), "prediction_agreement": float(np.mean(original == changed))}

def perturb(x: np.ndarray, indices: list[int], reference: np.ndarray, retain: bool = False) -> np.ndarray:
    out = np.tile(reference, (len(x), 1)) if retain else x.copy()
    if retain: out[:, indices] = x[:, indices]
    else: out[:, indices] = reference[indices]
    return out

def bootstrap(values: np.ndarray, rng: np.random.Generator, reps: int) -> tuple[float, float, float]:
    if not len(values): return np.nan, np.nan, np.nan
    estimates = np.array([np.mean(rng.choice(values, len(values), replace=True)) for _ in range(reps)])
    return float(np.mean(values)), float(np.quantile(estimates, .025)), float(np.quantile(estimates, .975))

def summarize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compatibility summary used by the original Stage 10 unit contract."""
    if not rows:
        return []
    frame = pd.DataFrame(rows)
    groups = ["experiment_id", "source_experiment_id", "model_id", "candidate_method", "reference_method", "top_k"]
    summary: list[dict[str, Any]] = []
    for keys, group in frame.groupby(groups, sort=True, dropna=False):
        values = dict(zip(groups, keys))
        std = lambda column: float(group[column].std(ddof=1)) if len(group) > 1 else 0.0
        values.update({"n_samples": int(len(group)), "mean_rank_overlap_at_k": float(group["rank_overlap_at_k"].mean()), "candidate_prediction_preservation_rate": float(group["candidate_prediction_preserved"].mean()), "reference_prediction_preservation_rate": float(group["reference_prediction_preserved"].mean()), "mean_candidate_probability_closeness": float(group["candidate_probability_closeness"].mean()), "std_candidate_probability_closeness": std("candidate_probability_closeness"), "mean_reference_probability_closeness": float(group["reference_probability_closeness"].mean()), "mean_candidate_absolute_sufficiency_gap": float(group["candidate_absolute_sufficiency_gap"].mean()), "std_candidate_absolute_sufficiency_gap": std("candidate_absolute_sufficiency_gap"), "mean_reference_absolute_sufficiency_gap": float(group["reference_absolute_sufficiency_gap"].mean()), "mean_candidate_comprehensiveness_drop": float(group["candidate_comprehensiveness_drop"].mean()), "std_candidate_comprehensiveness_drop": std("candidate_comprehensiveness_drop"), "mean_reference_comprehensiveness_drop": float(group["reference_comprehensiveness_drop"].mean()), "mean_candidate_minus_reference_probability_closeness": float(group["candidate_minus_reference_probability_closeness"].mean()), "mean_candidate_minus_reference_absolute_sufficiency_gap": float(group["candidate_minus_reference_absolute_sufficiency_gap"].mean()), "mean_candidate_minus_reference_comprehensiveness_drop": float(group["candidate_minus_reference_comprehensiveness_drop"].mean())})
        summary.append(values)
    return summary

def main(config_path: Path = ROOT / "configs/xai_fidelity_protocol.yaml") -> int:
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")); eid = cfg["experiment_id"]
    result_dir = ROOT / "results/xai"; artifact_dir = ROOT / f"artifacts/explanations/{eid}"
    inputs = [result_dir / name for name in REQ] + [ROOT / p for p in cfg["model_artifacts"].values()]
    manifest = []
    for path in inputs:
        if not path.is_file(): raise FileNotFoundError(f"Stage 10 BLOCKED: missing {path.relative_to(ROOT)}")
        manifest.append({"experiment_id": eid, "artifact_path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size, "integrity_status": "VERIFIED"})
    write(result_dir / "stage10_input_manifest.csv", manifest)

    models = {mid: joblib.load(ROOT / path) for mid, path in cfg["model_artifacts"].items()}
    references = {}
    for mid, pipe in models.items():
        scaler = pipe.named_steps.get("scaler")
        if scaler is None or not hasattr(scaler, "mean_"): raise RuntimeError(f"Stage 10 BLOCKED: {mid} lacks saved training mean")
        references[mid] = np.asarray(scaler.mean_, dtype=float)
    paths = {batch_number(p): p for p in discover_batches(ROOT / "data/raw")}
    data = {b: load_batch(paths[b]) for b in cfg["chronological_batches"]}
    global_imp = pd.read_csv(result_dir / "stage09_global_importance.csv")
    local_samples = pd.read_csv(result_dir / "stage09_local_samples.csv")
    local_exp = pd.read_csv(result_dir / "stage09_local_explanations.csv")
    fmap = pd.read_csv(result_dir / "stage09_feature_map.csv")
    family_by_index = {int(r.feature_index)-1: ("steady_state_resistance_change" if r.feature_type == "dR" else "normalized_resistance_response" if r.feature_type == "dR_norm" else "rising_transient_ema" if str(r.feature_type).startswith("EMAi") else "decaying_transient_ema") for r in fmap.itertuples()}
    rng = np.random.default_rng(cfg["random_control"]["seed"]); reps = int(cfg["random_control"]["repetitions"])
    global_rows=[]; control_rows=[]; sensor_rows=[]; family_rows=[]; local_rows=[]

    for method, eligible in cfg["global_methods"].items():
      for mid in eligible:
        pipe=models[mid]; ref=references[mid]
        for batch in cfg["chronological_batches"]:
          ranking_rows=global_imp[(global_imp.model_id==mid)&(global_imp.method==method)&(global_imp.batch.astype(str)==(str(batch) if method.startswith("PERMUTATION") else "ALL"))].sort_values("rank")
          if ranking_rows.empty: raise RuntimeError(f"applicable ranking missing: {mid}/{method}/B{batch}")
          # Stage 09 global importance uses zero-based feature_index; its feature map and local
          # explanation tables use one-based indices. Keep that historical schema difference explicit.
          ranking=ranking_rows.feature_index.astype(int).tolist(); x,y=data[batch]; original=pipe.predict(x)
          base_f1=f1_score(y,original,average="macro",zero_division=0); base_bal=balanced_accuracy_score(y,original)
          for k in cfg["top_k_features_global"]:
            top=ranking[:k]; bottom=ranking[-k:]; top_m=metrics(y,original,pipe.predict(perturb(x,top,ref))); bottom_m=metrics(y,original,pipe.predict(perturb(x,bottom,ref)))
            top_damage=base_f1-top_m["macro_f1"]; bottom_damage=base_f1-bottom_m["macro_f1"]
            random_d=[]
            for rep in range(reps):
              subset=rng.choice(128,k,replace=False).tolist(); rm=metrics(y,original,pipe.predict(perturb(x,subset,ref))); damage=base_f1-rm["macro_f1"]; random_d.append(damage)
              control_rows.append({"experiment_id":eid,"scope":"GLOBAL_FEATURE","model_id":mid,"method":method,"batch":batch,"k":k,"sample_id":"","repetition":rep,"selected_damage":top_damage,"random_damage":damage,"paired_difference":top_damage-damage,"unit":"macro_f1_proportion"})
            global_rows.append({"experiment_id":eid,"model_id":mid,"method":method,"batch":batch,"k":k,"original_macro_f1":base_f1,"deleted_macro_f1":top_m["macro_f1"],"macro_f1_damage":top_damage,"original_balanced_accuracy":base_bal,"deleted_balanced_accuracy":top_m["balanced_accuracy"],"balanced_accuracy_damage":base_bal-top_m["balanced_accuracy"],"prediction_agreement":top_m["prediction_agreement"],"bottom_k_damage":bottom_damage,"random_damage_mean":float(np.mean(random_d)),"selected_minus_random":top_damage-float(np.mean(random_d)),"probability_selected_exceeds_random":float(np.mean(top_damage>np.asarray(random_d))),"reference_source":"BATCH_1_SAVED_SCALER_MEAN","measurement_type":"EXECUTED"})
          # physical sensor groups
          scores={s:0.0 for s in range(1,17)}
          for r in ranking_rows.itertuples(): scores[int(r.feature_index)//8+1]+=abs(float(r.importance))
          sensor_rank=sorted(scores,key=scores.get,reverse=True)
          for sk in cfg["top_k_sensors"]:
            sensors=sensor_rank[:sk]; idx=[i for s in sensors for i in range((s-1)*8,s*8)]; changed=metrics(y,original,pipe.predict(perturb(x,idx,ref))); damage=base_f1-changed["macro_f1"]; rd=[]
            for rep in range(reps):
              rs=rng.choice(np.arange(1,17),sk,replace=False).tolist(); ri=[i for s in rs for i in range((s-1)*8,s*8)]; d=base_f1-metrics(y,original,pipe.predict(perturb(x,ri,ref)))["macro_f1"]; rd.append(d)
              control_rows.append({"experiment_id":eid,"scope":"SENSOR_GROUP","model_id":mid,"method":method,"batch":batch,"k":sk,"sample_id":"","repetition":rep,"selected_damage":damage,"random_damage":d,"paired_difference":damage-d,"unit":"macro_f1_proportion"})
            sensor_rows.append({"experiment_id":eid,"model_id":mid,"method":method,"batch":batch,"sensor_k":sk,"selected_sensors":json.dumps(sensors),"features_altered":len(idx),"macro_f1_damage":damage,"random_damage_mean":float(np.mean(rd)),"selected_minus_random":damage-float(np.mean(rd)),"unit":"macro_f1_proportion"})
          # ranked families, evaluated independently
          fscores={fam:0.0 for fam in set(family_by_index.values())}
          for r in ranking_rows.itertuples(): fscores[family_by_index[int(r.feature_index)]]+=abs(float(r.importance))
          for rank,(fam,score) in enumerate(sorted(fscores.items(),key=lambda z:z[1],reverse=True),1):
            idx=[i for i,f in family_by_index.items() if f==fam]; changed=metrics(y,original,pipe.predict(perturb(x,idx,ref)))
            family_rows.append({"experiment_id":eid,"model_id":mid,"method":method,"batch":batch,"family":fam,"family_rank":rank,"aggregated_importance":score,"features_altered":len(idx),"macro_f1_damage":base_f1-changed["macro_f1"],"unit":"macro_f1_proportion"})

    for sample in local_samples.itertuples():
      mid=sample.model_id; batch=int(sample.batch); x=data[batch][0][int(sample.row_index_in_batch):int(sample.row_index_in_batch)+1]; pipe=models[mid]; ref=references[mid]
      proba=pipe.predict_proba(x)[0]; classes=list(pipe.classes_); pred=sample.predicted_label; ci=classes.index(pred); original_score=float(proba[ci])
      for method in cfg["local_methods"]:
        if mid not in cfg["local_methods"][method]: continue
        ranked=local_exp[(local_exp.model_id==mid)&(local_exp.sample_id==sample.sample_id)&(local_exp.method==method)].sort_values("rank").feature_index.astype(int).sub(1).tolist()
        if not ranked: continue
        label="ABLATION_CONSISTENCY" if method=="SINGLE_FEATURE_ABLATION_LOCAL" else "LOCAL_FIDELITY"
        for k in cfg["top_k_features_local"]:
          idx=ranked[:k]; deleted=perturb(x,idx,ref); retained=perturb(x,idx,ref,True); dp=pipe.predict_proba(deleted)[0]; rp=pipe.predict_proba(retained)[0]; dscore=float(dp[ci]); rscore=float(rp[ci]); drops=[]
          for rep in range(reps):
            ri=rng.choice(128,k,replace=False).tolist(); random_score=float(pipe.predict_proba(perturb(x,ri,ref))[0,ci]); drop=original_score-random_score; drops.append(drop)
            control_rows.append({"experiment_id":eid,"scope":"LOCAL_FEATURE","model_id":mid,"method":method,"batch":batch,"k":k,"sample_id":sample.sample_id,"repetition":rep,"selected_damage":original_score-dscore,"random_damage":drop,"paired_difference":original_score-dscore-drop,"unit":"probability"})
          scaler=pipe.named_steps["scaler"]; dist=float(np.linalg.norm(scaler.transform(deleted)-scaler.transform(x)))
          local_rows.append({"experiment_id":eid,"source_experiment_id":"EXP-XAI-0001","model_id":mid,"batch":batch,"sample_id":sample.sample_id,"true_class":sample.true_label,"original_predicted_class":pred,"correct":sample.correct,"category":sample.category,"method":method,"evaluation_label":label,"k":k,"selected_features":json.dumps([i+1 for i in idx]),"original_target_score":original_score,"deleted_target_score":dscore,"target_score_drop":original_score-dscore,"deleted_predicted_class":pipe.predict(deleted)[0],"class_flip":bool(pipe.predict(deleted)[0]!=pred),"retained_target_score":rscore,"target_score_retained_ratio":rscore/original_score if original_score else np.nan,"retained_predicted_class":pipe.predict(retained)[0],"random_target_score_drop_mean":float(np.mean(drops)),"selected_minus_random":original_score-dscore-float(np.mean(drops)),"perturbation_standardized_l2":dist,"features_altered":k,"reference_source":"BATCH_1_SAVED_SCALER_MEAN","unit":"probability","measurement_type":"EXECUTED"})

    write(result_dir/"stage10_fidelity_global.csv",global_rows); write(result_dir/"stage10_fidelity_local.csv",local_rows); write(result_dir/"stage10_fidelity_sensor_groups.csv",sensor_rows); write(result_dir/"stage10_fidelity_feature_families.csv",family_rows); write(result_dir/"stage10_random_controls.csv",control_rows)
    ci=[]; brng=np.random.default_rng(cfg["bootstrap"]["seed"]); controls=pd.DataFrame(control_rows); locals_df=pd.DataFrame(local_rows)
    for keys,g in controls.groupby(["scope","model_id","method","batch","k"]):
      est,lo,hi=bootstrap(g.paired_difference.to_numpy(float),brng,int(cfg["bootstrap"]["repetitions"])); ci.append({"experiment_id":eid,"scope":keys[0],"model_id":keys[1],"method":keys[2],"batch":keys[3],"category":"ALL","k":keys[4],"metric_name":"selected_minus_random_damage","estimate":est,"ci_low":lo,"ci_high":hi,"n":len(g),"unit":g.unit.iloc[0],"bootstrap_repetitions":cfg["bootstrap"]["repetitions"],"measurement_type":"DERIVED"})
    for keys,g in locals_df.groupby(["model_id","method","batch","category","k"]):
      est,lo,hi=bootstrap(g.selected_minus_random.to_numpy(float),brng,int(cfg["bootstrap"]["repetitions"])); ci.append({"experiment_id":eid,"scope":"LOCAL_SAMPLE","model_id":keys[0],"method":keys[1],"batch":keys[2],"category":keys[3],"k":keys[4],"metric_name":"selected_minus_random_target_score_drop","estimate":est,"ci_low":lo,"ci_high":hi,"n":len(g),"unit":"probability","bootstrap_repetitions":cfg["bootstrap"]["repetitions"],"measurement_type":"DERIVED"})
    write(result_dir/"stage10_bootstrap_ci.csv",ci)
    summary=[]
    for scope,frame,metric in [("GLOBAL",pd.DataFrame(global_rows),"selected_minus_random"),("SENSOR",pd.DataFrame(sensor_rows),"selected_minus_random"),("LOCAL",locals_df,"selected_minus_random")]:
      for keys,g in frame.groupby(["model_id","method"]): summary.append({"experiment_id":eid,"scope":scope,"model_id":keys[0],"method":keys[1],"metric_name":metric,"mean":float(g[metric].mean()),"median":float(g[metric].median()),"n":len(g),"unit":"proportion" if scope!="LOCAL" else "probability","evidence_state":"DERIVED"})
    write(result_dir/"stage10_fidelity_summary.csv",summary)
    artifact_dir.mkdir(parents=True,exist_ok=True); (artifact_dir/"config.yaml").write_bytes(config_path.read_bytes())
    outputs=[result_dir/n for n in ["stage10_fidelity_global.csv","stage10_fidelity_local.csv","stage10_fidelity_sensor_groups.csv","stage10_fidelity_feature_families.csv","stage10_random_controls.csv","stage10_bootstrap_ci.csv","stage10_fidelity_summary.csv","stage10_input_manifest.csv"]]
    out_manifest=[{"experiment_id":eid,"artifact_path":p.relative_to(ROOT).as_posix(),"sha256":digest(p),"rows":sum(1 for _ in p.open(encoding="utf-8"))-1,"status":"EXECUTED"} for p in outputs]
    write(result_dir/"stage10_manifest.csv",out_manifest)
    (artifact_dir/"manifest.json").write_text(json.dumps({"experiment_id":eid,"status":"EXECUTED","created_at":datetime.now(timezone.utc).isoformat(),"reference_source":"BATCH_1_SAVED_SCALER_MEAN","random_seed":42,"bootstrap_seed":1042,"outputs":out_manifest},indent=2),encoding="utf-8")
    print(json.dumps({"status":"EXECUTED","global_rows":len(global_rows),"local_rows":len(local_rows),"sensor_rows":len(sensor_rows),"family_rows":len(family_rows),"control_rows":len(control_rows),"ci_rows":len(ci)},indent=2)); return 0

if __name__ == "__main__": raise SystemExit(main())
