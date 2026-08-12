"""Controlled host-side timing for frozen Stage 09 explanation mechanisms."""
from __future__ import annotations
import os
for _name in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","BLIS_NUM_THREADS"):
    os.environ[_name]="1"
import csv,hashlib,json,platform,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from typing import Any,Callable
import joblib,numpy as np,pandas as pd,psutil,scipy,sklearn,threadpoolctl,yaml
from sklearn.inspection import permutation_importance
from sklearn.metrics import f1_score,make_scorer
from sklearn.model_selection import train_test_split
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.data.loader import batch_number,discover_batches,load_batch  # noqa:E402
from src.xai.intrinsic import CoefficientExplainer,ImpurityExplainer  # noqa:E402
from src.xai.local_ablation import SingleFeatureAblationExplainer  # noqa:E402

def sha(p:Path):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p:Path,data,fields=None):
 p.parent.mkdir(parents=True,exist_ok=True);fields=fields or (list(data[0]) if data else ["experiment_id"])
 with p.open("w",encoding="utf-8",newline="") as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(data)
def stats(v):
 a=np.asarray(v,float);q=np.quantile(a,[.25,.75,.95,.99]);return {"median_ns":float(np.median(a)),"mean_ns":float(a.mean()),"p95_ns":float(q[2]),"p99_ns":float(q[3]),"iqr_ns":float(q[1]-q[0]),"min_ns":float(a.min()),"max_ns":float(a.max()),"std_ns":float(a.std(ddof=1)) if len(a)>1 else 0.0,"cv":float(a.std(ddof=1)/a.mean()) if len(a)>1 and a.mean() else 0.0,"n":len(a)}
def boot(v,rng,reps=1000):
 a=np.asarray(v,float);z=np.array([np.median(rng.choice(a,len(a),replace=True)) for _ in range(reps)]);return float(np.median(a)),float(np.quantile(z,.025)),float(np.quantile(z,.975))

def main(config_path:Path=ROOT/"configs/xai_latency_protocol.yaml"):
 cfg=yaml.safe_load(config_path.read_text(encoding="utf-8"));eid=cfg["experiment_id"];xd=ROOT/"results/xai";ad=ROOT/f"artifacts/explanations/{eid}"
 # Verify registered lineage without modifying prior outputs.
 registered={}
 for source in (xd/"stage10_input_manifest.csv",xd/"stage11_input_manifest.csv"):
  for r in pd.read_csv(source).itertuples():registered[r.artifact_path]=r.sha256
 for source in (xd/"stage10_manifest.csv",xd/"stage11_manifest.csv"):
  for r in pd.read_csv(source).itertuples():registered[r.artifact_path]=r.sha256
 required=[xd/"stage10_manifest.csv",xd/"stage11_manifest.csv",xd/"stage09_global_importance.csv",xd/"stage09_local_samples.csv",xd/"stage09_local_explanations.csv",xd/"stage09_feature_map.csv",ROOT/"research/feature_metadata.csv",ROOT/"data/manifests/dataset_manifest.json"]
 required += [ROOT/f"artifacts/models/BASE-FIXED-C{i}-001.joblib" for i in range(1,5)]
 input_rows=[]
 for p in required:
  if not p.is_file():raise RuntimeError(f"BLOCKED_INPUT_INTEGRITY missing {p}")
  rel=p.relative_to(ROOT).as_posix();actual=sha(p);expected=registered.get(rel)
  if expected and expected!=actual:raise RuntimeError(f"BLOCKED_INPUT_INTEGRITY hash mismatch {rel}")
  producer="EXP-XAI-0001" if "stage09" in rel else "EXP-XAI-FIDELITY-001" if "stage10" in rel else "EXP-XAI-STABILITY-001" if "stage11" in rel else "DATA_OR_ONTOLOGY"
  input_rows.append({"artifact_id":"ART-"+actual[:12].upper(),"path":rel,"sha256":actual,"producer_experiment":producer,"required_for":"HOST_COST_BENCHMARK","verification_status":"VERIFIED"})
 write(xd/"stage12_input_manifest.csv",input_rows)
 # Environment contains no username, hostname, serial, or unrelated identity.
 commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
 host={"environment_id":"HOST-STAGE12-001","os":platform.platform(),"os_build":platform.version(),"cpu":platform.processor() or "UNAVAILABLE","architecture":platform.machine(),"physical_core_count":psutil.cpu_count(logical=False),"logical_core_count":os.cpu_count(),"ram_bytes":psutil.virtual_memory().total,"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,"scikit_learn":sklearn.__version__,"joblib":joblib.__version__,"threadpoolctl":threadpoolctl.__version__,"git_commit":commit,"benchmark_timestamp":datetime.now(timezone.utc).isoformat(),"scientific_scope":"HOST_MEASURED","mcu_latency":"NOT_MEASURED","physical_energy":"NOT_MEASURED"}
 (xd/"stage12_host_environment.json").write_text(json.dumps(host,indent=2),encoding="utf-8")
 models={};model_paths={mid:ROOT/f"artifacts/models/BASE-FIXED-{mid.replace('MODEL-','')}-001.joblib" for mid in cfg["models"]}
 raw=[];run_counter=0
 def record(mid,method,scope,batch,sid,phase,state,wall,cpu,fc,sc,pc,bsize=1):
  nonlocal run_counter;run_counter+=1;raw.append({"experiment_id":eid,"run_id":f"T{run_counter:07d}","model_id":mid,"method":method,"scope":scope,"batch":batch,"sample_id_if_applicable":sid,"phase":phase,"warmup_or_measured":state,"wall_time_ns":wall,"cpu_time_ns":cpu,"feature_count":fc,"sample_count":sc,"prediction_calls":pc,"thread_count":1,"batch_size":bsize,"timestamp":datetime.now(timezone.utc).isoformat(),"timer":"time.perf_counter_ns","environment_id":"HOST-STAGE12-001","unit":"nanoseconds","hardware_scope":"HOST"})
 def timed(fn:Callable[[],Any],mid,method,scope,batch="",sid="",phase="",state="MEASURED",fc=128,sc=1,pc=0,bsize=1):
  t0=time.perf_counter_ns();c0=time.process_time_ns();value=fn();c1=time.process_time_ns();t1=time.perf_counter_ns();record(mid,method,scope,batch,sid,phase,state,t1-t0,c1-c0,fc,sc,pc,bsize);return value
 with threadpoolctl.threadpool_limits(limits=1):
  thread_info=threadpoolctl.threadpool_info();effective=[int(x.get("num_threads",0)) for x in thread_info]
  thread_env={"requested_environment":cfg["thread_control"]["environment"],"effective_threadpools":thread_info,"effective_max_threads":max(effective) if effective else 1,"sklearn_n_jobs":1,"verification_status":"VERIFIED" if all(x<=1 for x in effective) else "LIMITATION_EFFECTIVE_THREADS_GT_1"}
  (xd/"stage12_thread_environment.json").write_text(json.dumps(thread_env,indent=2),encoding="utf-8")
  # model load is a separate cold operation
  for mid,p in model_paths.items():
   for i in range(cfg["measured_repeats"]["model_load"]):models[mid]=timed(lambda p=p:joblib.load(p),mid,"MODEL","MODEL",phase="MODEL_LOAD",state="FIRST_CALL" if i==0 else "MEASURED",fc=0,sc=0,pc=0)
   est=models[mid].named_steps["model"]
   if hasattr(est,"n_jobs"):est.n_jobs=1
  paths={batch_number(p):p for p in discover_batches(ROOT/"data/raw")};data={b:load_batch(paths[b]) for b in cfg["batches"]}
  local_samples=pd.read_csv(xd/"stage09_local_samples.csv");local_samples=local_samples[local_samples.batch.isin(cfg["batches"])]
  # baseline end-to-end inference and preprocessing-only diagnostics
  for mid,pipe in models.items():
   scaler=pipe.named_steps["scaler"]
   for b in cfg["batches"]:
    x=data[b][0];one=x[:1];batch=x[:cfg["batch_inference_size"]]
    for state,n in (("WARMUP",cfg["warmup"]["inference_and_local"]),("MEASURED",cfg["measured_repeats"]["inference_and_local"])):
     for _ in range(n):
      timed(lambda:scaler.transform(one),mid,"BASELINE_MODEL","LOCAL",b,"","PREPROCESSING_ONLY",state,128,1,0)
      timed(lambda:pipe.predict_proba(one),mid,"BASELINE_MODEL","LOCAL",b,"","BASELINE_INFERENCE_END_TO_END",state,128,1,1)
      timed(lambda:pipe.predict_proba(batch),mid,"BASELINE_MODEL","BATCH",b,"","BASELINE_INFERENCE_END_TO_END",state,128,len(batch),1,len(batch))
  # static intrinsic global extraction and top-k reduction
  intrinsic=[("MODEL-C1","INTRINSIC_COEFFICIENT",CoefficientExplainer(models["MODEL-C1"],"MODEL-C1")),("MODEL-C2","INTRINSIC_IMPURITY",ImpurityExplainer(models["MODEL-C2"],"MODEL-C2"))]
  for mid,method,expl in intrinsic:
   result=None
   for state,n in (("WARMUP",cfg["warmup"]["intrinsic_and_reduction"]),("MEASURED",cfg["measured_repeats"]["intrinsic_and_reduction"])):
    for _ in range(n):result=timed(expl.explain_global,mid,method,"GLOBAL",phase="ONE_TIME_GLOBAL_EXTRACTION_COST",state=state,fc=128,sc=0,pc=0)
   v=np.asarray(result["importance"])
   for k in cfg["top_k"]:
    for _ in range(cfg["measured_repeats"]["intrinsic_and_reduction"]):timed(lambda v=v,k=k:np.argsort(-np.abs(v))[:k],mid,method,"GLOBAL",phase=f"TOP_K_REDUCTION_K{k}",fc=128,sc=0,pc=0)
  # full dataset-level permutation importance; total cost retained
  scorer=make_scorer(f1_score,average="macro",zero_division=0);preps=cfg["permutation_repeats_per_run"]
  for mid,pipe in models.items():
   for b in cfg["batches"]:
    x_full,y_full=data[b];n_eval=min(int(cfg["permutation_evaluation"]["sample_count"]),len(y_full));x,_,y,_=train_test_split(x_full,y_full,train_size=n_eval,stratify=y_full,random_state=cfg["permutation_evaluation"]["seed"]);fn=lambda pipe=pipe,x=x,y=y:permutation_importance(pipe,x,y,scoring=scorer,n_repeats=preps,random_state=cfg["seed"],n_jobs=1)
    calls=1+128*preps
    for state,n in (("WARMUP",cfg["warmup"]["permutation"]),("MEASURED",cfg["measured_repeats"]["permutation"])):
     for _ in range(n):timed(fn,mid,"PERMUTATION_IMPORTANCE_MACRO_F1","GLOBAL",b,"","GLOBAL_EXPLANATION_TOTAL",state,128,len(x),calls,1)
  # local coefficient and vectorized ablation on every frozen audit sample
  for r in local_samples.sort_values(["model_id","sample_id"]).itertuples():
   mid=r.model_id;pipe=models[mid];b=int(r.batch);x=data[b][0][int(r.row_index_in_batch)];ref=np.asarray(pipe.named_steps["scaler"].mean_)
   explainers=[]
   if mid=="MODEL-C1":explainers.append(("INTRINSIC_COEFFICIENT",CoefficientExplainer(pipe,mid),1,1))
   explainers.append(("SINGLE_FEATURE_ABLATION_LOCAL_VECTORIZED",SingleFeatureAblationExplainer(pipe,mid,ref),2,129))
   for method,expl,pc,sc in explainers:
    result=None
    for state,n in (("WARMUP",cfg["warmup"]["inference_and_local"]),("MEASURED",cfg["measured_repeats"]["inference_and_local"])):
     for _ in range(n):result=timed(lambda expl=expl,x=x:expl.explain_local(x),mid,method,"LOCAL",b,r.sample_id,"EXPLANATION_COMPUTE",state,128,sc,pc,128 if "VECTORIZED" in method else 1)
    v=np.asarray(result["feature_contributions"])
    for k in cfg["top_k"]:
     for _ in range(cfg["measured_repeats"]["inference_and_local"]):timed(lambda v=v,k=k:np.argsort(-np.abs(v))[:k],mid,method,"LOCAL",b,r.sample_id,f"TOP_K_REDUCTION_K{k}",fc=128,sc=1,pc=0)
    for _ in range(cfg["measured_repeats"]["inference_and_local"]):timed(lambda result=result:json.dumps(result),mid,method,"LOCAL",b,r.sample_id,"SERIALIZATION_JSON",fc=128,sc=1,pc=0)
  # bounded naive reference: predetermined first sample per model and batch
  chosen=local_samples.sort_values("sample_id").groupby(["model_id","batch"],as_index=False).first()
  for r in chosen.itertuples():
   mid=r.model_id;pipe=models[mid];b=int(r.batch);x=data[b][0][int(r.row_index_in_batch)];ref=np.asarray(pipe.named_steps["scaler"].mean_)
   def naive():
    base=pipe.predict_proba(x.reshape(1,-1))[0];ci=int(np.argmax(base));vals=[]
    for j in range(128):q=x.copy();q[j]=ref[j];vals.append(float(base[ci]-pipe.predict_proba(q.reshape(1,-1))[0,ci]))
    return vals
   for state,n in (("WARMUP",1),("MEASURED",cfg["measured_repeats"]["naive_ablation"])):
    for _ in range(n):timed(naive,mid,"SINGLE_FEATURE_ABLATION_LOCAL_NAIVE_REFERENCE","LOCAL",b,r.sample_id,"EXPLANATION_COMPUTE",state,128,129,129,1)
 write(xd/"stage12_raw_timings.csv",raw)
 # Summaries regenerate entirely from raw measured rows.
 df=pd.DataFrame(raw);meas=df[df.warmup_or_measured=="MEASURED"].copy();groups=["model_id","method","scope","batch","phase","feature_count","sample_count","prediction_calls","batch_size","environment_id"]
 summary=[]
 for keys,g in meas.groupby(groups,dropna=False):summary.append(dict(zip(groups,keys))|stats(g.wall_time_ns)|{"experiment_id":eid,"median_us":float(np.median(g.wall_time_ns)/1000),"p95_us":float(np.quantile(g.wall_time_ns,.95)/1000),"unit":"nanoseconds_raw_microseconds_presentation","variance_flag":"HIGH_VARIANCE_HOST_MEASUREMENT" if g.wall_time_ns.std(ddof=1)/g.wall_time_ns.mean()>cfg["variance"]["high_variance_threshold"] else "REPORTED_CONTINUOUSLY","scientific_scope":"HOST_MEASURED"})
 write(xd/"stage12_latency_summary.csv",summary);summ=pd.DataFrame(summary)
 write(xd/"stage12_baseline_inference.csv",summ[summ.method=="BASELINE_MODEL"].to_dict("records"));write(xd/"stage12_global_latency.csv",summ[(summ.scope=="GLOBAL")].to_dict("records"));write(xd/"stage12_local_latency.csv",summ[(summ.scope=="LOCAL")&summ.method.str.contains("COEFFICIENT|ABLATION")].to_dict("records"))
 # hardware-independent accounting
 counts=[]
 specs=[("INTRINSIC_COEFFICIENT","GLOBAL",0,0,1,False,False,True,True,"STATIC_PRECOMPUTABLE|REQUIRES_MODEL_INTERNALS|EMBEDDED_FEASIBILITY_UNTESTED"),("INTRINSIC_IMPURITY","GLOBAL",0,0,1,False,False,True,True,"STATIC_PRECOMPUTABLE|REQUIRES_MODEL_INTERNALS|EMBEDDED_FEASIBILITY_UNTESTED"),("PERMUTATION_IMPORTANCE_MACRO_F1","GLOBAL",641,641,128,True,True,False,False,"REQUIRES_DATASET|REQUIRES_LABELS|REQUIRES_MULTIPLE_INFERENCES|EMBEDDED_FEASIBILITY_UNTESTED"),("INTRINSIC_COEFFICIENT","LOCAL",1,1,128,False,False,True,False,"ONLINE_SINGLE_SAMPLE_CAPABLE|REQUIRES_MODEL_INTERNALS|EMBEDDED_FEASIBILITY_UNTESTED"),("SINGLE_FEATURE_ABLATION_LOCAL_VECTORIZED","LOCAL",2,129,128,False,False,False,False,"ONLINE_SINGLE_SAMPLE_CAPABLE|REQUIRES_MULTIPLE_INFERENCES|EMBEDDED_FEASIBILITY_UNTESTED"),("SINGLE_FEATURE_ABLATION_LOCAL_NAIVE_REFERENCE","LOCAL",129,129,128,False,False,False,False,"ONLINE_SINGLE_SAMPLE_CAPABLE|REQUIRES_MULTIPLE_INFERENCES|EMBEDDED_FEASIBILITY_UNTESTED")]
 for method,scope,pc,pert,vlen,train,labels,internals,precomp,states in specs:
  eligible=["MODEL-C1"] if method=="INTRINSIC_COEFFICIENT" else ["MODEL-C2"] if method=="INTRINSIC_IMPURITY" else cfg["models"]
  for mid in eligible:counts.append({"experiment_id":eid,"method":method,"scope":scope,"model_id":mid,"feature_count":128,"sensor_count":16,"sample_count":"BATCH_DEPENDENT" if scope=="GLOBAL" and "PERMUTATION" in method else 1,"prediction_calls":pc,"additional_prediction_calls":max(0,pc-1),"perturbed_samples":pert,"sort_operations":1,"explanation_vector_length":vlen,"requires_training_data":train,"requires_labels":labels,"requires_future_data":False,"requires_model_gradients":False,"requires_model_internals":internals,"supports_online_single_sample":scope=="LOCAL","supports_precomputation":precomp,"supports_static_storage":scope=="GLOBAL","sensor_group_scenario":"ANALYTICAL_ONLY_16_GROUPS","evidence_states":states,"measurement_type":"DERIVED_OPERATION_COUNT"})
 write(xd/"stage12_operation_counts.csv",counts)
 # Bootstrap medians.
 rng=np.random.default_rng(cfg["bootstrap"]["seed"]);cis=[]
 for keys,g in meas.groupby(["model_id","method","scope","batch","phase"],dropna=False):
  est,lo,hi=boot(g.wall_time_ns,rng,cfg["bootstrap"]["repetitions"]);cis.append({"experiment_id":eid,"model_id":keys[0],"method":keys[1],"scope":keys[2],"batch":keys[3],"phase":keys[4],"metric_name":"median_host_wall_time_ns","estimate":est,"ci_low":lo,"ci_high":hi,"n":len(g),"bootstrap_repetitions":cfg["bootstrap"]["repetitions"],"resampling_unit":"timing_replicate","unit":"nanoseconds","measurement_type":"MEASURED_HOST"})
 write(xd/"stage12_bootstrap_ci.csv",cis)
 # Join continuous Stage 10/11 evidence to host explanation compute cost.
 f10=pd.read_csv(xd/"stage10_fidelity_summary.csv");s11=pd.read_csv(xd/"stage11_stability_summary.csv");cost=summ[summ.phase.isin(["EXPLANATION_COMPUTE","ONE_TIME_GLOBAL_EXTRACTION_COST","GLOBAL_EXPLANATION_TOTAL"])].groupby(["model_id","method","scope"],as_index=False)[["median_us","p95_us"]].mean();cost.method=cost.method.str.replace("_VECTORIZED","",regex=False);f=f10.groupby(["model_id","method","scope"],as_index=False)["mean"].mean().rename(columns={"mean":"stage10_fidelity_evidence"});s=s11.groupby(["model_id","method","scope"],as_index=False)["mean"].mean().rename(columns={"mean":"stage11_stability_evidence"});trade=cost.merge(f,on=["model_id","method","scope"],how="left").merge(s,on=["model_id","method","scope"],how="left");trade["experiment_id"]=eid;trade["interpretation"]="CONTINUOUS_EVIDENCE_NO_COMPOSITE_SCORE";trade["host_cost_state"]="HOST_MEASURED";trade["mcu_cost"]="NOT_MEASURED";write(xd/"stage12_fidelity_stability_cost.csv",trade.to_dict("records"))
 ad.mkdir(parents=True,exist_ok=True);(ad/"config.yaml").write_bytes(config_path.read_bytes())
 outputs=[xd/n for n in cfg["expected_outputs"] if n not in ("stage12_manifest.csv",)];man=[]
 for p in outputs:man.append({"experiment_id":eid,"artifact_path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"rows":sum(1 for _ in p.open(encoding="utf-8"))-1 if p.suffix==".csv" else "","status":"EXECUTED"})
 write(xd/"stage12_manifest.csv",man);(ad/"manifest.json").write_text(json.dumps({"experiment_id":eid,"scientific_execution_status":"EXECUTED","scientific_scope":"HOST_MEASURED","public_deployment_status":"BLOCKED_CREDENTIALS","mcu_latency":"NOT_MEASURED","physical_energy":"NOT_MEASURED","outputs":man},indent=2),encoding="utf-8")
 print(json.dumps({"status":"EXECUTED","raw_timing_rows":len(raw),"measured_rows":len(meas),"summary_rows":len(summary),"effective_max_threads":thread_env["effective_max_threads"]},indent=2));return 0
if __name__=="__main__":raise SystemExit(main())
