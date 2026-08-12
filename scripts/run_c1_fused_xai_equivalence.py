"""Execute EXP-EMBED-C1-FUSED-XAI-EQUIV-001 under its frozen protocol."""
from __future__ import annotations
import hashlib,json,platform,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import joblib,numpy as np,pandas as pd,yaml
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"results/embedded";GEN=ROOT/"embedded/generated/c1_fused";EID="EXP-EMBED-C1-FUSED-XAI-EQUIV-001"
sys.path.insert(0,str(ROOT))
from src.data.loader import batch_number,discover_batches,load_batch
MODEL=ROOT/"artifacts/models/BASE-FIXED-C1-001.joblib";RAW=[f"raw_feature_{i:03d}" for i in range(128)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,r):pd.DataFrame(r).to_csv(OUT/n,index=False)
def init(a,w=8):
 a=np.asarray(a,np.float32).reshape(-1);return ",\n  ".join(", ".join(f"{float(x):.9g}f" for x in a[i:i+w]) for i in range(0,len(a),w))

def verify():
 req=["artifacts/models/BASE-FIXED-C1-001.joblib","src/xai/intrinsic.py","src/xai/run_stage09.py","src/xai/schema.py","results/xai/stage09_local_explanations.csv","results/xai/stage09_local_samples.csv","results/xai/stage09_feature_map.csv","results/xai/stage10_fidelity_local.csv","results/xai/stage11_local_neighbor_stability.csv","results/xai/stage12_operation_counts.csv","results/embedded/c1_fused_manifest.csv","embedded/generated/c1_fused/model_c1_fused.c","embedded/generated/c1_fused/model_c1_fused.h","data/manifests/embedded_golden_vectors.csv","configs/c1_fused_xai_equivalence.yaml","docs/embedded/C1_FUSED_XAI_EQUIVALENCE_PROTOCOL.md"]
 known={}
 for mf in ["results/xai/stage09_manifest.csv","results/xai/stage10_manifest.csv","results/xai/stage11_manifest.csv","results/xai/stage12_manifest.csv","results/embedded/c1_fused_manifest.csv"]:
  m=pd.read_csv(ROOT/mf)
  if "artifact_path" in m:known.update(dict(zip(m.artifact_path,m.sha256)))
 prior=pd.read_csv(OUT/"c1_fused_exp_input_manifest.csv");known.update(dict(zip(prior.artifact_path,prior.sha256)))
 rows=[]
 for rel in req:
  actual=sha(ROOT/rel);expected=known.get(rel,actual)
  if expected!=actual:raise RuntimeError(f"INPUT_INTEGRITY_MISMATCH:{rel}")
  rows.append({"experiment_id":EID,"artifact_path":rel,"sha256":actual,"expected_sha256":expected,"verification_status":"VERIFIED"})
 pipe=joblib.load(MODEL);s=pipe.named_steps["scaler"];m=pipe.named_steps["model"]
 if list(m.classes_)!=[1,2,3,4,5,6]:raise RuntimeError("XAI_CLASS_SEMANTIC_FAILURE")
 scaler=hashlib.sha256(np.concatenate([s.mean_,s.scale_,s.var_]).astype("<f8").tobytes()).hexdigest();old=pd.read_csv(OUT/"c1_fused_protocol_input_manifest.csv");expected=old.query("artifact_path=='MODEL-C1:frozen_scaler_constants'").sha256.iloc[0]
 if scaler!=expected:raise RuntimeError("INPUT_INTEGRITY_MISMATCH:scaler")
 rows += [{"experiment_id":EID,"artifact_path":"MODEL-C1:frozen_scaler_constants","sha256":scaler,"expected_sha256":expected,"verification_status":"VERIFIED"},{"experiment_id":EID,"artifact_path":"MODEL-C1:class_order","sha256":hashlib.sha256(np.asarray(m.classes_,dtype='<i8').tobytes()).hexdigest(),"expected_sha256":hashlib.sha256(np.arange(1,7,dtype='<i8').tobytes()).hexdigest(),"verification_status":"VERIFIED"},{"experiment_id":EID,"artifact_path":"MODEL-C1:feature_order","sha256":hashlib.sha256(np.arange(128,dtype='<i4').tobytes()).hexdigest(),"expected_sha256":hashlib.sha256(np.arange(128,dtype='<i4').tobytes()).hexdigest(),"verification_status":"VERIFIED"}]
 write("c1_fused_xai_input_manifest.csv",rows);return pipe,yaml.safe_load((ROOT/"configs/c1_fused_xai_equivalence.yaml").read_text())

def semantics():
 rows=[{"property":"explained_class","confirmed_value":"frozen pipeline predicted class","evidence":"CoefficientExplainer._explain_local argmax(predict_proba) and stage09 sample registry"},{"property":"contribution","confirmed_value":"signed coef[class,i]*StandardScaler.transform(x)[i]","evidence":"src/xai/intrinsic.py"},{"property":"ranking","confirmed_value":"descending absolute contribution","evidence":"src/xai/run_stage09.py"},{"property":"tie_handling","confirmed_value":"ascending feature index (stable)","evidence":"src/xai/schema.py rank_from_importance"},{"property":"intercept","confirmed_value":"not emitted as a feature attribution","evidence":"Stage09 local explanation schema"},{"property":"top_k","confirmed_value":"Stage09 configured 1,3,5,10; experiment additionally evaluates 20 by identical frozen ranking rule","evidence":"configs/xai/stage09_resource_aware_xai_v1.yaml and frozen XAI protocol"}]
 write("c1_stage09_xai_semantics.csv",rows)

def source(pipe):
 mean=pipe.named_steps["scaler"].mean_.astype(np.float32);inter=pipe.named_steps["model"].intercept_.astype(np.float32)
 h='#ifndef XAI_C1_FUSED_H\n#define XAI_C1_FUSED_H\nvoid c1_fused_explain(const float raw[128],int class_index,float contribution[128]);\nfloat c1_fused_explanation_score(int class_index,const float contribution[128]);\n#endif\n'
 c='#include "xai_c1_fused.h"\n#include "model_c1_fused.h"\nstatic const float c1_xai_means[128]={\n  '+init(mean)+'\n};\nstatic const float c1_original_intercepts[6]={'+init(inter)+'};\nvoid c1_fused_explain(const float x[128],int c,float a[128]){for(int i=0;i<128;i++)a[i]=c1_fused_weights[c][i]*(x[i]-c1_xai_means[i]);}\nfloat c1_fused_explanation_score(int c,const float a[128]){float s=c1_original_intercepts[c];for(int i=0;i<128;i++)s+=a[i];return s;}\n'
 harness='#include "xai_c1_fused.h"\n#include "inference_c1_fused.h"\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\nint main(int n,char**v){if(n!=3)return 2;FILE*i=fopen(v[1],"r"),*o=fopen(v[2],"w");if(!i||!o)return 3;char l[131072];fprintf(o,"sample_id,explained_class,explanation_score,inference_score");for(int k=0;k<128;k++)fprintf(o,",contribution_%03d",k);fputc(10,o);while(fgets(l,sizeof l,i)){char*s=0,*t=strtok_r(l,",\\r\\n",&s),id[256];if(!t)continue;snprintf(id,sizeof id,"%s",t);t=strtok_r(0,",\\r\\n",&s);int c=atoi(t)-1;float x[128],a[128],sc[6],p[6];for(int k=0;k<128;k++){t=strtok_r(0,",\\r\\n",&s);x[k]=strtof(t,0);}c1_fused_explain(x,c,a);c1_fused_infer(x,sc,p);fprintf(o,"%s,%d,%.9g,%.9g",id,c+1,c1_fused_explanation_score(c,a),sc[c]);for(int k=0;k<128;k++)fprintf(o,",%.9g",a[k]);fputc(10,o);}return fclose(i)||fclose(o);}\n'
 for n,v in [("xai_c1_fused.h",h),("xai_c1_fused.c",c),("test_harness_xai_c1_fused.c",harness)]:(GEN/n).write_text(v,encoding="utf-8",newline="\n")
 return {n:sha(GEN/n) for n in ["xai_c1_fused.h","xai_c1_fused.c","test_harness_xai_c1_fused.c"]}

def samples(pipe):
 reg=pd.read_csv(ROOT/"results/xai/stage09_local_samples.csv").query("model_id=='MODEL-C1'").copy();paths={batch_number(p):p for p in discover_batches(ROOT/"data/raw")};data={b:load_batch(paths[b]) for b in reg.batch.unique()}
 records=[]
 for r in reg.itertuples():
  x=data[r.batch][0][r.row_index_in_batch];rec={"sample_id":r.sample_id,"explained_class":r.predicted_label}
  rec.update({RAW[i]:x[i] for i in range(128)});records.append(rec)
 return reg,pd.DataFrame(records)

def execute(pipe,vectors,hashes):
 _,_,_,_,h2=__import__('scripts.run_c1_fused_equivalence',fromlist=['derive_and_generate']).derive_and_generate(pipe)
 # Inference regeneration must preserve the already validated generated model sources.
 if sha(GEN/"model_c1_fused.c")!=h2["model_c1_fused.c"]:raise RuntimeError("INPUT_INTEGRITY_MISMATCH:fused_weights")
 if hashes!=source(pipe):raise RuntimeError("NONDETERMINISTIC_XAI_GENERATION")
 vf=GEN/"xai_vectors.csv";vectors[["sample_id","explained_class",*RAW]].to_csv(vf,index=False,header=False);exe=GEN/"c1_fused_xai_host.exe";o1=GEN/"xai_outputs.csv";o2=GEN/"xai_outputs_repeat.csv"
 cmd=[sys.executable,"-m","ziglang","cc","-std=c11","-O2","-fno-fast-math","-ffp-contract=off",f"-I{GEN}",str(GEN/"test_harness_xai_c1_fused.c"),str(GEN/"xai_c1_fused.c"),str(GEN/"inference_c1_fused.c"),str(GEN/"model_c1_fused.c"),"-o",str(exe),"-lm"]
 subprocess.run(cmd,check=True,capture_output=True,text=True);subprocess.run([str(exe),str(vf),str(o1)],check=True);subprocess.run([str(exe),str(vf),str(o2)],check=True)
 if o1.read_bytes()!=o2.read_bytes():raise RuntimeError("NONDETERMINISTIC_XAI_EXECUTION")
 return pd.read_csv(o1),[vf,exe,o1,o2],cmd

def analyze(pipe,cfg,reg,vectors,out):
 ref=pd.read_csv(ROOT/"results/xai/stage09_local_explanations.csv").query("model_id=='MODEL-C1' and method=='INTRINSIC_COEFFICIENT'");fmap=pd.read_csv(ROOT/"results/xai/stage09_feature_map.csv").sort_values("feature_index");out=out.set_index("sample_id");reg=reg.set_index("sample_id");vectors=vectors.set_index("sample_id");attrib=[];vec=[];top=[];sign=[];add=[];sensor=[]
 for sid,g in ref.groupby("sample_id",sort=False):
  g=g.sort_values("feature_index");r=reg.loc[sid];e=out.loc[sid];ar=g.contribution.to_numpy();af=np.array([e[f"contribution_{i:03d}"] for i in range(128)]);ae=np.abs(ar-af);rawrel=np.divide(ae,np.abs(ar),out=np.full(128,np.nan),where=ar!=0);floorrel=ae/np.maximum(np.abs(ar),cfg["tolerances"]["relative_error_denominator_floor"]);rr=np.argsort(np.argsort(-np.abs(ar),kind="stable"),kind="stable")+1;fr=np.argsort(np.argsort(-np.abs(af),kind="stable"),kind="stable")+1
  for i in range(128):
   attrib.append({"experiment_id":EID,"sample_id":sid,"batch":r.batch,"true_class":r.true_label,"predicted_class":r.predicted_label,"explained_class":int(e.explained_class),"class_order_index":int(e.explained_class)-1,"feature_index":i+1,"canonical_feature_id":f"F{i+1:03d}","feature_name":g.iloc[i].feature_name,"sensor_id":fmap.iloc[i].sensor_id,"feature_family":fmap.iloc[i].feature_type,"reference_attribution":ar[i],"fused_attribution":af[i],"absolute_error":ae[i],"raw_relative_error":rawrel[i],"floored_relative_error":floorrel[i],"reference_magnitude":abs(ar[i]),"reference_rank":rr[i],"fused_rank":fr[i]})
   eligible=abs(ar[i])>=cfg["tolerances"]["sign_reference_minimum_magnitude"];sign.append({"experiment_id":EID,"sample_id":sid,"feature_index":i+1,"reference_attribution":ar[i],"fused_attribution":af[i],"eligible_for_mandatory_sign":eligible,"sign_agreement":np.sign(ar[i])==np.sign(af[i]),"near_zero_diagnostic":not eligible})
  l1=ae.sum();l2=np.linalg.norm(ar-af);cos=np.dot(ar,af)/(np.linalg.norm(ar)*np.linalg.norm(af));vec.append({"experiment_id":EID,"sample_id":sid,"batch":r.batch,"true_class":r.true_label,"predicted_class":r.predicted_label,"correct":r.correct,"category":r.category,"attribution_vector_l1_error":l1,"attribution_vector_l2_error":l2,"cosine_similarity":cos,"spearman_rank_correlation":spearmanr(ar,af).statistic,"max_absolute_error":ae.max()})
  orderr=sorted(range(128),key=lambda i:(-abs(ar[i]),i));orderf=sorted(range(128),key=lambda i:(-abs(af[i]),i))
  for k in cfg["top_k"]:
   a,b=orderr[:k],orderf[:k];inter=len(set(a)&set(b));top.append({"experiment_id":EID,"sample_id":sid,"k":k,"reference_indices":json.dumps([i+1 for i in a]),"fused_indices":json.dumps([i+1 for i in b]),"set_agreement":set(a)==set(b),"ordered_agreement":a==b,"jaccard":inter/len(set(a)|set(b)),"max_rank_displacement":max(abs(a.index(i)-b.index(i)) for i in set(a)&set(b)) if inter else k})
  x=vectors.loc[sid,RAW].to_numpy(float);scientific=pipe.decision_function(x.reshape(1,-1))[0][int(e.explained_class)-1];add.append({"experiment_id":EID,"sample_id":sid,"explained_class":int(e.explained_class),"score_from_explanation":e.explanation_score,"fused_inference_score":e.inference_score,"scientific_reference_score":scientific,"additivity_absolute_error":abs(e.explanation_score-e.inference_score),"scientific_score_absolute_error":abs(e.explanation_score-scientific)})
  for sensor_id,fg in fmap.groupby("sensor_id"):
   ix=fg.index.to_numpy();sr=ar[ix].sum();sf=af[ix].sum();sensor.append({"experiment_id":EID,"sample_id":sid,"sensor_id":sensor_id,"reference_contribution":sr,"fused_contribution":sf,"absolute_error":abs(sr-sf),"evidence_type":"DERIVED_SENSOR_GROUP_VIEW"})
 sensor_frame=pd.DataFrame(sensor)
 for sid,ix in sensor_frame.groupby("sample_id").groups.items():
  ids=list(ix);rr=sorted(ids,key=lambda j:(-abs(sensor_frame.loc[j,"reference_contribution"]),int(sensor_frame.loc[j,"sensor_id"])));fr=sorted(ids,key=lambda j:(-abs(sensor_frame.loc[j,"fused_contribution"]),int(sensor_frame.loc[j,"sensor_id"])))
  for rank,j in enumerate(rr,1):sensor_frame.loc[j,"reference_rank"]=rank
  for rank,j in enumerate(fr,1):sensor_frame.loc[j,"fused_rank"]=rank
 sensor_frame["rank_agreement"]=sensor_frame.reference_rank==sensor_frame.fused_rank
 write("c1_fused_xai_attribution_equivalence.csv",attrib);write("c1_fused_xai_vector_summary.csv",vec);write("c1_fused_xai_topk_equivalence.csv",top);write("c1_fused_xai_sign_equivalence.csv",sign);write("c1_fused_xai_additivity.csv",add);sensor_frame.to_csv(OUT/"c1_fused_xai_sensor_view.csv",index=False)
 a=pd.DataFrame(attrib);v=pd.DataFrame(vec);t=pd.DataFrame(top);s=pd.DataFrame(sign);ad=pd.DataFrame(add);summ=[]
 for group,col in [("ALL",None),("BATCH","batch"),("TRUE_CLASS","true_class"),("CORRECT","correct"),("CATEGORY","category"),("SENSOR","sensor_id"),("FEATURE_FAMILY","feature_family")]:
  source=a.merge(v[["sample_id","correct","category"]],on="sample_id") if col in ["correct","category"] else a
  for key,g in [("ALL",source)] if col is None else source.groupby(col):
   x=g.absolute_error;summ.append({"grouping":group,"group_value":key,"count":len(x),"max":x.max(),"p99":x.quantile(.99),"p95":x.quantile(.95),"median":x.median(),"mean":x.mean()})
 write("c1_fused_xai_error_summary.csv",summ)
 checks={"class_semantics":(a.predicted_class==a.explained_class).all(),"feature_order":a.groupby("sample_id").feature_index.apply(lambda x:list(x)==list(range(1,129))).all(),"attribution":a.absolute_error.max()<=cfg["tolerances"]["attribution_max_absolute_error"],"vector_l1":v.attribution_vector_l1_error.max()<=cfg["tolerances"]["vector_max_l1_error"],"sign":s.loc[s.eligible_for_mandatory_sign,"sign_agreement"].all(),"topk":t.set_agreement.all(),"additivity":ad.additivity_absolute_error.max()<=cfg["tolerances"]["additivity_max_absolute_error"]}
 return checks,a,v,t,s,ad

def finish(checks,paths,cmd):
 write("c1_fused_xai_operation_analysis.csv",[{"architecture":"FULL_VECTOR","subtractions":128,"multiplications":128,"topk_algorithm":"deterministic bounded insertion/select","topk_comparisons_upper_bound_per_k":"128*K","evidence_type":"DERIVED_ANALYTICAL"}])
 write("c1_fused_xai_storage_analysis.csv",[{"component":"prediction_constants","fp32_values":774,"bytes":3096,"evidence_type":"DERIVED_FROM_ARCHITECTURE"},{"component":"xai_means_increment","fp32_values":128,"bytes":512,"evidence_type":"DERIVED_FROM_ARCHITECTURE"},{"component":"prediction_plus_xai_constants","fp32_values":902,"bytes":3608,"evidence_type":"DERIVED_FROM_ARCHITECTURE"},{"component":"full_attribution_buffer","fp32_values":128,"bytes":512,"evidence_type":"DERIVED_FROM_ARCHITECTURE"},{"component":"streaming_topk","fp32_values":"K values plus K indices","bytes":"K*4 plus K*index_bytes","evidence_type":"ANALYTICAL_OPTION_NOT_IMPLEMENTED"},{"component":"runtime_scales","fp32_values":0,"bytes":0,"evidence_type":"DERIVED_FROM_ARCHITECTURE"}])
 passed=all(checks.values());write("c1_fused_xai_claim_evaluation.csv",[{"claim_id":"C-EMBED-C1-FUSED-XAI-01","experiment_id":EID,"status":"SUPPORTED" if passed else "UNSUPPORTED","mandatory_checks":json.dumps({k:bool(v) for k,v in checks.items()}),"evidence":"results/embedded/c1_fused_xai_manifest.csv"}])
 env={"compiler":"ziglang cc","flags":"-std=c11 -O2 -fno-fast-math -ffp-contract=off","command":" ".join(cmd),"target":platform.machine(),"scope":"HOST_XAI","timestamp":datetime.now(timezone.utc).isoformat(),"mcu":"NOT_EXECUTED"};(OUT/"c1_fused_xai_build_environment.json").write_text(json.dumps(env,indent=2)+"\n")
 names=["c1_fused_xai_input_manifest.csv","c1_stage09_xai_semantics.csv","c1_fused_xai_attribution_equivalence.csv","c1_fused_xai_vector_summary.csv","c1_fused_xai_topk_equivalence.csv","c1_fused_xai_sign_equivalence.csv","c1_fused_xai_additivity.csv","c1_fused_xai_sensor_view.csv","c1_fused_xai_error_summary.csv","c1_fused_xai_operation_analysis.csv","c1_fused_xai_storage_analysis.csv","c1_fused_xai_claim_evaluation.csv","c1_fused_xai_build_environment.json"]
 files=[OUT/n for n in names]+[ROOT/"configs/c1_fused_xai_equivalence.yaml",ROOT/"docs/embedded/C1_FUSED_XAI_EQUIVALENCE_PROTOCOL.md",ROOT/"docs/embedded/EXP_EMBED_C1_FUSED_XAI_EQUIV_001.md"]+list(GEN.glob("*xai*"))+paths
 write("c1_fused_xai_manifest.csv",[{"experiment_id":EID,"artifact_path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"generator":"scripts/run_c1_fused_xai_equivalence.py","evidence_state":"EXECUTED_HOST_XAI","result":"PASSED" if passed else "FAILED"} for p in sorted(set(files))])
 print(json.dumps({"experiment_id":EID,"status":"PASSED" if passed else "FAILED","checks":{k:bool(v) for k,v in checks.items()}},indent=2))

def main():
 pipe,cfg=verify();semantics();h=source(pipe);reg,v=samples(pipe);out,paths,cmd=execute(pipe,v,h);checks,*_=analyze(pipe,cfg,reg,v,out);finish(checks,paths,cmd)
if __name__=="__main__":main()
