"""Execute preregistered Stage 11 explanation stability analyses."""
from __future__ import annotations
import csv, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import joblib, numpy as np, pandas as pd, yaml
from scipy.optimize import linear_sum_assignment
from scipy.stats import kendalltau, spearmanr

ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
from src.data.loader import batch_number, discover_batches, load_batch  # noqa:E402

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p:Path,data:list[dict[str,Any]],fields:list[str]|None=None):
 p.parent.mkdir(parents=True,exist_ok=True); fields=fields or (list(data[0]) if data else ["experiment_id"])
 with p.open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(data)
def norm(v):
 a=np.abs(np.asarray(v,float)); s=a.sum(); return a/s if s else np.zeros_like(a)
def rank_metrics(a,b,ks=(5,10,20)):
 ra=pd.Series(-np.asarray(a)).rank(method="average").to_numpy(); rb=pd.Series(-np.asarray(b)).rank(method="average").to_numpy()
 out={"spearman":float(spearmanr(ra,rb).statistic),"kendall_tau_b":float(kendalltau(ra,rb).statistic)}
 for k in ks:
  aa=set(np.argsort(-np.asarray(a))[:k]);bb=set(np.argsort(-np.asarray(b))[:k]);out[f"jaccard_at_{k}"]=len(aa&bb)/len(aa|bb)
 return out
def mag_metrics(a,b):
 x=norm(a);y=norm(b);den=np.linalg.norm(x)*np.linalg.norm(y);return {"cosine_similarity":float(x@y/den) if den else np.nan,"normalized_l1_distance":float(np.abs(x-y).sum()/2)}
def sign_metrics(a,b,k=20,tol=1e-12):
 a=np.asarray(a);b=np.asarray(b);valid=(np.abs(a)>tol)|(np.abs(b)>tol);top=np.union1d(np.argsort(-np.abs(a))[:k],np.argsort(-np.abs(b))[:k]);agree=np.sign(a)==np.sign(b)
 return {"sign_agreement":float(agree[valid].mean()) if valid.any() else np.nan,"top_k_sign_agreement":float(agree[top].mean()),"sign_flip_frequency":float((np.sign(a[valid])!=np.sign(b[valid])).mean()) if valid.any() else np.nan}
def boot(vals,rng,reps=1000):
 vals=np.asarray(vals,float);vals=vals[np.isfinite(vals)]
 if len(vals)<3:return (float(np.mean(vals)) if len(vals) else np.nan,np.nan,np.nan)
 z=np.array([np.mean(rng.choice(vals,len(vals),replace=True)) for _ in range(reps)]);return float(vals.mean()),float(np.quantile(z,.025)),float(np.quantile(z,.975))
def corr_ci(x,y,rng,reps=1000):
 x=np.asarray(x,float);y=np.asarray(y,float);ok=np.isfinite(x)&np.isfinite(y);x=x[ok];y=y[ok]
 if len(x)<3:return np.nan,np.nan,np.nan
 est=float(spearmanr(x,y).statistic);z=[]
 for _ in range(reps):
  idx=rng.integers(0,len(x),len(x));v=spearmanr(x[idx],y[idx]).statistic
  if np.isfinite(v):z.append(v)
 return est,float(np.quantile(z,.025)),float(np.quantile(z,.975))

def summarize_pairs(rows: list[dict[str, Any]], top_k_values: list[int]) -> list[dict[str, Any]]:
 """Compatibility summary for the original Stage 11 pairwise-test contract."""
 frame=pd.DataFrame(rows); summaries=[]
 for model_id,group in frame.groupby("model_id",sort=True):
  reference=group[(group["comparison"]=="REFERENCE")&(group["batch_a"]!=group["batch_b"])]
  adjacent=group[group["comparison"]=="ADJACENT"]
  row={"experiment_id":group["experiment_id"].iloc[0],"source_experiment_id":group["source_experiment_id"].iloc[0],"model_id":model_id,"method":group["method"].iloc[0],"n_reference_comparisons":int(len(reference)),"n_adjacent_comparisons":int(len(adjacent)),"mean_reference_spearman":float(reference["spearman_rank_correlation"].mean()),"std_reference_spearman":float(reference["spearman_rank_correlation"].std(ddof=1)),"minimum_reference_spearman":float(reference["spearman_rank_correlation"].min()),"mean_reference_kendall":float(reference["kendall_rank_correlation"].mean()),"mean_reference_cosine":float(reference["importance_cosine_similarity"].mean()),"mean_adjacent_spearman":float(adjacent["spearman_rank_correlation"].mean()),"std_adjacent_spearman":float(adjacent["spearman_rank_correlation"].std(ddof=1)),"minimum_adjacent_spearman":float(adjacent["spearman_rank_correlation"].min()),"mean_adjacent_kendall":float(adjacent["kendall_rank_correlation"].mean()),"mean_adjacent_cosine":float(adjacent["importance_cosine_similarity"].mean())}
  for top_k in top_k_values:
   column=f"top_{top_k}_jaccard"; row[f"mean_reference_top_{top_k}_jaccard"]=float(reference[column].mean()); row[f"mean_adjacent_top_{top_k}_jaccard"]=float(adjacent[column].mean())
  summaries.append(row)
 return summaries

def main(config_path:Path=ROOT/"configs/xai_stability_protocol.yaml"):
 cfg=yaml.safe_load(config_path.read_text(encoding="utf-8"));eid=cfg["experiment_id"];xdir=ROOT/"results/xai";adir=ROOT/f"artifacts/explanations/{eid}"
 stage10_manifest_path=xdir/"stage10_manifest.csv";stage10=pd.read_csv(stage10_manifest_path);inputs=[stage10_manifest_path]
 for r in stage10.itertuples():
  p=ROOT/r.artifact_path
  if not p.is_file() or sha(p)!=r.sha256:raise RuntimeError(f"Stage 11 BLOCKED: Stage 10 hash mismatch {r.artifact_path}")
  inputs.append(p)
 inputs += [xdir/n for n in ("stage09_global_importance.csv","stage09_local_samples.csv","stage09_local_explanations.csv","stage09_feature_map.csv","stage09_manifest.csv")]
 inputs += [ROOT/"results/drift/global_drift_by_batch.csv",ROOT/"results/baselines/fixed_origin_metrics.csv"]
 models={mid:joblib.load(ROOT/f"artifacts/models/BASE-FIXED-{mid.replace('MODEL-','')}-001.joblib") for mid in cfg["models"]}
 inputs += [ROOT/f"artifacts/models/BASE-FIXED-{mid.replace('MODEL-','')}-001.joblib" for mid in cfg["models"]]
 if any(not p.is_file() for p in inputs):raise FileNotFoundError("Stage 11 BLOCKED: missing source artifact")
 write(xdir/"stage11_input_manifest.csv",[{"experiment_id":eid,"artifact_path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"bytes":p.stat().st_size,"integrity_status":"VERIFIED"} for p in inputs])
 paths={batch_number(p):p for p in discover_batches(ROOT/"data/raw")};data={b:load_batch(paths[b]) for b in cfg["eligible_global_batches"]}
 gi=pd.read_csv(xdir/"stage09_global_importance.csv");ls=pd.read_csv(xdir/"stage09_local_samples.csv");le=pd.read_csv(xdir/"stage09_local_explanations.csv");fmap=pd.read_csv(xdir/"stage09_feature_map.csv")
 drift=pd.read_csv(ROOT/"results/drift/global_drift_by_batch.csv");drift=drift[drift.metric=="normalized_wasserstein"].set_index("comparison_batch").median_feature_drift.to_dict()
 perf=pd.read_csv(ROOT/"results/baselines/fixed_origin_metrics.csv");perf={(r.model,int(r.test_batch)):float(r.macro_f1) for r in perf.itertuples()}
 families={int(r.feature_index)-1:("steady_state_resistance_change" if r.feature_type=="dR" else "normalized_resistance_response" if r.feature_type=="dR_norm" else "rising_transient_ema" if str(r.feature_type).startswith("EMAi") else "decaying_transient_ema") for r in fmap.itertuples()}
 probmeans={(mid,b):models[mid].predict_proba(data[b][0]).mean(axis=0) for mid in models for b in data}
 comparisons=[("ADJACENT",*p) for p in cfg["comparison_families"]["adjacent"]]+[("ANCHOR_TO_FUTURE",*p) for p in cfg["comparison_families"]["anchor_to_future"]]
 gr=[];gm=[];ss=[];ff=[];rel=[];direction=[]
 for mid in cfg["models"]:
  method="PERMUTATION_IMPORTANCE_MACRO_F1";vectors={}
  for b in cfg["eligible_global_batches"]:
   q=gi[(gi.model_id==mid)&(gi.method==method)&(gi.batch.astype(str)==str(b))].sort_values("feature_index");vectors[b]=q.importance.to_numpy(float)
  for typ,a,b in comparisons:
   va,vb=vectors[a],vectors[b];rm=rank_metrics(va,vb,cfg["top_k_features"]);mm=mag_metrics(va,vb);input_change=abs(float(drift[b])-float(drift[a]));f1change=abs(perf[(mid,b)]-perf[(mid,a)]);outchange=float(np.abs(probmeans[(mid,b)]-probmeans[(mid,a)]).sum()/2)
   base={"experiment_id":eid,"model_id":mid,"method":method,"comparison_type":typ,"anchor_batch":2,"batch_a":a,"batch_b":b,"n_features":128}
   gr.append(base|rm|{"unit":"correlation_or_proportion","status":"EXECUTED"});gm.append(base|mm|{"unit":"similarity_or_normalized_distance","status":"EXECUTED"})
   sa=np.array([np.abs(va[(s-1)*8:s*8]).sum() for s in range(1,17)]);sb=np.array([np.abs(vb[(s-1)*8:s*8]).sum() for s in range(1,17)]);sr=rank_metrics(sa,sb,cfg["top_k_sensors"]);sm=mag_metrics(sa,sb)
   ss.append(base|{"sensor_spearman":sr["spearman"],"sensor_kendall_tau_b":sr["kendall_tau_b"],"jaccard_at_1":sr["jaccard_at_1"],"jaccard_at_3":sr["jaccard_at_3"],"jaccard_at_5":sr["jaccard_at_5"],"sensor_importance_l1_distance":sm["normalized_l1_distance"],"input_change":input_change,"unit":"correlation_or_normalized_distance","status":"EXECUTED"})
   fams=sorted(set(families.values()));fa=np.array([sum(abs(va[i]) for i in families if families[i]==f) for f in fams]);fb=np.array([sum(abs(vb[i]) for i in families if families[i]==f) for f in fams]);fr=rank_metrics(fa,fb,(1,));fm=mag_metrics(fa,fb)
   ff.append(base|{"families":json.dumps(fams),"family_rank_spearman":fr["spearman"],"family_kendall_tau_b":fr["kendall_tau_b"],"dominant_family_a":fams[int(np.argmax(fa))],"dominant_family_b":fams[int(np.argmax(fb))],"dominant_family_changed":bool(np.argmax(fa)!=np.argmax(fb)),"family_importance_l1_distance":fm["normalized_l1_distance"],"unit":"correlation_or_normalized_distance","status":"EXECUTED"})
   for eps in cfg["relative_stability"]["sensitivity_epsilons"]:rel.append(base|{"scope":"GLOBAL","explanation_distance":mm["normalized_l1_distance"],"input_change":input_change,"model_macro_f1_change":f1change,"model_output_distribution_change":outchange,"epsilon":eps,"explanation_per_input_change":mm["normalized_l1_distance"]/(input_change+eps),"explanation_per_output_change":mm["normalized_l1_distance"]/(outchange+eps),"unit":"ratio_with_components","status":"EXECUTED"})
  direction.append({"experiment_id":eid,"scope":"GLOBAL","model_id":mid,"method":method,"status":"NOT_APPLICABLE","reason":"Permutation macro-F1 importance sign is not a directional feature attribution","sign_agreement":"NOT_APPLICABLE","top_k_sign_agreement":"NOT_APPLICABLE","sign_flip_frequency":"NOT_APPLICABLE","unit":"NOT_APPLICABLE"})
 # local vectors and actual standardized samples
 vec={(m,s,method):g.sort_values("feature_index").contribution.to_numpy(float) for (m,s,method),g in le.groupby(["model_id","sample_id","method"])}
 sample_rows={(r.model_id,r.sample_id):r for r in ls.itertuples()};xs={}
 for r in ls.itertuples():xs[(r.model_id,r.sample_id)]=models[r.model_id].named_steps["scaler"].transform(data[int(r.batch)][0][int(r.row_index_in_batch):int(r.row_index_in_batch)+1])[0]
 neigh=[]
 for (mid,sid,method),v in vec.items():
  r=sample_rows[(mid,sid)];cand=[q for q in ls.itertuples() if q.model_id==mid and q.sample_id!=sid and int(q.batch)==int(r.batch) and int(q.true_label)==int(r.true_label) and int(q.predicted_label)==int(r.predicted_label) and (mid,q.sample_id,method) in vec]
  cand=sorted(cand,key=lambda q:np.linalg.norm(xs[(mid,sid)]-xs[(mid,q.sample_id)]))[:cfg["local_neighbors"]["count"]]
  for q in cand:
   w=vec[(mid,q.sample_id,method)];rm=rank_metrics(np.abs(v),np.abs(w),cfg["top_k_features"]);mm=mag_metrics(v,w);sm=sign_metrics(v,w);ind=float(np.linalg.norm(xs[(mid,sid)]-xs[(mid,q.sample_id)])/np.sqrt(128));pa=models[mid].predict_proba(data[int(r.batch)][0][int(r.row_index_in_batch):int(r.row_index_in_batch)+1])[0];pb=models[mid].predict_proba(data[int(q.batch)][0][int(q.row_index_in_batch):int(q.row_index_in_batch)+1])[0];od=float(np.abs(pa-pb).sum()/2)
   row={"experiment_id":eid,"model_id":mid,"method":method,"center_sample_id":sid,"neighbor_sample_id":q.sample_id,"batch":int(r.batch),"true_class":int(r.true_label),"predicted_class":int(r.predicted_label),"category":r.category,"input_distance":ind,"model_output_distance":od,"explanation_distance":mm["normalized_l1_distance"],"spearman":rm["spearman"],"kendall_tau_b":rm["kendall_tau_b"],"jaccard_at_5":rm["jaccard_at_5"],"jaccard_at_10":rm["jaccard_at_10"],"jaccard_at_20":rm["jaccard_at_20"],"cosine_similarity":mm["cosine_similarity"],**sm,"neighbor_count_requested":cfg["local_neighbors"]["count"],"unit":"standardized_distance_similarity_or_proportion","status":"EXECUTED"};neigh.append(row);direction.append({"experiment_id":eid,"scope":"LOCAL_NEIGHBOR","model_id":mid,"method":method,"status":"EXECUTED","reason":"signed local contributions","sign_agreement":sm["sign_agreement"],"top_k_sign_agreement":sm["top_k_sign_agreement"],"sign_flip_frequency":sm["sign_flip_frequency"],"unit":"proportion"})
 # one-to-one matched cross-sectional pairs
 matches=[];cross=[]
 for mid in cfg["models"]:
  methods=[m for m,spec in cfg["local_methods"].items() if mid in spec["models"]]
  for method in methods:
   for ba,bb in cfg["cross_batch_matching"]["pairs"]:
    for cls in sorted(ls[ls.model_id==mid].true_label.unique()):
     aa=[r for r in ls.itertuples() if r.model_id==mid and int(r.batch)==ba and int(r.true_label)==int(cls) and (mid,r.sample_id,method) in vec];bbrows=[r for r in ls.itertuples() if r.model_id==mid and int(r.batch)==bb and int(r.true_label)==int(cls) and (mid,r.sample_id,method) in vec]
     if not aa or not bbrows:continue
     cost=np.array([[np.linalg.norm(xs[(mid,a.sample_id)]-xs[(mid,b.sample_id)])/np.sqrt(128) for b in bbrows] for a in aa]);ii,jj=linear_sum_assignment(cost)
     for i,j in zip(ii,jj):
      a,b=aa[i],bbrows[j];va=vec[(mid,a.sample_id,method)];vb=vec[(mid,b.sample_id,method)];rm=rank_metrics(np.abs(va),np.abs(vb),cfg["top_k_features"]);mm=mag_metrics(va,vb);sm=sign_metrics(va,vb);pa=models[mid].predict_proba(data[ba][0][int(a.row_index_in_batch):int(a.row_index_in_batch)+1])[0];pb=models[mid].predict_proba(data[bb][0][int(b.row_index_in_batch):int(b.row_index_in_batch)+1])[0];od=float(np.abs(pa-pb).sum()/2)
      matches.append({"experiment_id":eid,"model_id":mid,"method":method,"source_sample_id":a.sample_id,"target_sample_id":b.sample_id,"source_batch":ba,"target_batch":bb,"true_class":int(cls),"source_predicted_class":int(a.predicted_label),"target_predicted_class":int(b.predicted_label),"prediction_consistent":bool(a.predicted_label==b.predicted_label),"matching_cost":float(cost[i,j]),"matching_algorithm":"ONE_TO_ONE_HUNGARIAN_WITHIN_TRUE_CLASS","unit":"standardized_euclidean_per_sqrt_feature_count","status":"EXECUTED"})
      cross.append({"experiment_id":eid,"analysis":"CROSS_SECTIONAL_MATCHED_ANALYSIS_NOT_LONGITUDINAL","model_id":mid,"method":method,"source_sample_id":a.sample_id,"target_sample_id":b.sample_id,"source_batch":ba,"target_batch":bb,"true_class":int(cls),"source_category":a.category,"target_category":b.category,"input_distance":float(cost[i,j]),"model_output_distance":od,"explanation_distance":mm["normalized_l1_distance"],"spearman":rm["spearman"],"kendall_tau_b":rm["kendall_tau_b"],"jaccard_at_5":rm["jaccard_at_5"],"jaccard_at_10":rm["jaccard_at_10"],"jaccard_at_20":rm["jaccard_at_20"],"cosine_similarity":mm["cosine_similarity"],**sm,"unit":"distance_similarity_or_proportion","status":"EXECUTED"})
 write(xdir/"stage11_global_rank_stability.csv",gr);write(xdir/"stage11_global_magnitude_stability.csv",gm);write(xdir/"stage11_direction_stability.csv",direction);write(xdir/"stage11_sensor_stability.csv",ss);write(xdir/"stage11_feature_family_stability.csv",ff);write(xdir/"stage11_local_neighbor_stability.csv",neigh);write(xdir/"stage11_cross_batch_matches.csv",matches);write(xdir/"stage11_cross_batch_stability.csv",cross);write(xdir/"stage11_relative_stability.csv",rel)
 # fidelity linkage at matched global model/method/batch units and local sample units
 fg=pd.read_csv(xdir/"stage10_fidelity_global.csv").groupby(["model_id","method","batch"],as_index=False).selected_minus_random.mean();mg=pd.DataFrame(gm);stab=mg.groupby(["model_id","method","batch_b"],as_index=False).normalized_l1_distance.mean().rename(columns={"batch_b":"batch"});link=fg.merge(stab,on=["model_id","method","batch"]);links=[]
 for keys,g in link.groupby(["model_id","method"]):
  est,lo,hi=corr_ci(g.selected_minus_random,g.normalized_l1_distance,np.random.default_rng(cfg["bootstrap"]["seed"]),cfg["bootstrap"]["repetitions"]);links.append({"experiment_id":eid,"scope":"GLOBAL_MATCHED_BATCH","model_id":keys[0],"method":keys[1],"n":len(g),"fidelity_metric":"mean_selected_minus_random_macro_f1_damage","stability_metric":"mean_explanation_l1_distance_ending_at_batch","spearman":est,"ci_low":lo,"ci_high":hi,"unit":"correlation","status":"EXECUTED"})
 fl=pd.read_csv(xdir/"stage10_fidelity_local.csv").groupby(["model_id","method","sample_id"],as_index=False).selected_minus_random.mean();nl=pd.DataFrame(neigh).groupby(["model_id","method","center_sample_id"],as_index=False).explanation_distance.mean().rename(columns={"center_sample_id":"sample_id"});ll=fl.merge(nl,on=["model_id","method","sample_id"])
 for keys,g in ll.groupby(["model_id","method"]):
  est,lo,hi=corr_ci(g.selected_minus_random,g.explanation_distance,np.random.default_rng(cfg["bootstrap"]["seed"]+1),cfg["bootstrap"]["repetitions"]);links.append({"experiment_id":eid,"scope":"LOCAL_MATCHED_SAMPLE","model_id":keys[0],"method":keys[1],"n":len(g),"fidelity_metric":"mean_selected_minus_random_target_score_drop","stability_metric":"mean_neighbor_explanation_l1_distance","spearman":est,"ci_low":lo,"ci_high":hi,"unit":"correlation","status":"EXECUTED"})
 write(xdir/"stage11_fidelity_stability_link.csv",links)
 # bootstrap summaries and continuous correlations
 rng=np.random.default_rng(cfg["bootstrap"]["seed"]);ci=[]
 for keys,g in pd.DataFrame(gr).groupby(["model_id","method","comparison_type"]):
  for metric in ("spearman","kendall_tau_b","jaccard_at_5","jaccard_at_10","jaccard_at_20"):
   est,lo,hi=boot(g[metric],rng,cfg["bootstrap"]["repetitions"]);ci.append({"experiment_id":eid,"scope":"GLOBAL_RANK","model_id":keys[0],"method":keys[1],"comparison":keys[2],"category":"ALL","metric_name":metric,"estimate":est,"ci_low":lo,"ci_high":hi,"n":len(g),"resampling_unit":"chronological_batch_pair","unit":"correlation_or_proportion","status":"DERIVED"})
 for keys,g in pd.DataFrame(neigh).groupby(["model_id","method","category"]):
  for metric in ("explanation_distance","jaccard_at_10","sign_agreement"):
   est,lo,hi=boot(g[metric],rng,cfg["bootstrap"]["repetitions"]);ci.append({"experiment_id":eid,"scope":"LOCAL_NEIGHBOR","model_id":keys[0],"method":keys[1],"comparison":"WITHIN_CONTEXT","category":keys[2],"metric_name":metric,"estimate":est,"ci_low":lo,"ci_high":hi,"n":len(g),"resampling_unit":"center_neighbor_pair","unit":"normalized_distance_or_proportion","status":"DERIVED"})
 # global explanation distance correlations with input and behavior change
 rdf=pd.DataFrame(rel);base=rdf[rdf.epsilon==cfg["relative_stability"]["epsilon"]]
 for keys,g in base.groupby(["model_id","method"]):
  for metric in ("input_change","model_macro_f1_change","model_output_distribution_change"):
   est,lo,hi=corr_ci(g.explanation_distance,g[metric],rng,cfg["bootstrap"]["repetitions"]);ci.append({"experiment_id":eid,"scope":"RELATIVE_CORRELATION","model_id":keys[0],"method":keys[1],"comparison":"ALL_CHRONOLOGICAL_PAIRS","category":"ALL","metric_name":f"explanation_distance_vs_{metric}_spearman","estimate":est,"ci_low":lo,"ci_high":hi,"n":len(g),"resampling_unit":"chronological_batch_pair","unit":"correlation","status":"DERIVED"})
 write(xdir/"stage11_bootstrap_ci.csv",ci)
 summary=[]
 for scope,frame,metric in [("GLOBAL_RANK",pd.DataFrame(gr),"spearman"),("GLOBAL_MAGNITUDE",pd.DataFrame(gm),"normalized_l1_distance"),("SENSOR",pd.DataFrame(ss),"sensor_importance_l1_distance"),("LOCAL_NEIGHBOR",pd.DataFrame(neigh),"explanation_distance"),("CROSS_BATCH",pd.DataFrame(cross),"explanation_distance")]:
  for keys,g in frame.groupby(["model_id","method"]):summary.append({"experiment_id":eid,"scope":scope,"model_id":keys[0],"method":keys[1],"metric_name":metric,"mean":float(g[metric].mean()),"median":float(g[metric].median()),"n":len(g),"unit":"correlation" if metric=="spearman" else "normalized_distance","evidence_state":"DERIVED"})
 write(xdir/"stage11_stability_summary.csv",summary)
 adir.mkdir(parents=True,exist_ok=True);(adir/"config.yaml").write_bytes(config_path.read_bytes())
 names=cfg["expected_outputs"][:-2]+["stage11_bootstrap_ci.csv","stage11_stability_summary.csv","stage11_input_manifest.csv"];outs=[xdir/n for n in names];man=[{"experiment_id":eid,"artifact_path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"rows":sum(1 for _ in p.open(encoding="utf-8"))-1,"status":"EXECUTED"} for p in outs];write(xdir/"stage11_manifest.csv",man)
 (adir/"manifest.json").write_text(json.dumps({"experiment_id":eid,"scientific_execution_status":"EXECUTED","public_deployment_status":"BLOCKED_CREDENTIALS","created_at":datetime.now(timezone.utc).isoformat(),"outputs":man},indent=2),encoding="utf-8")
 print(json.dumps({"status":"EXECUTED","global_pairs":len(gr),"local_neighbor_pairs":len(neigh),"cross_batch_matches":len(matches),"bootstrap_rows":len(ci)},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
