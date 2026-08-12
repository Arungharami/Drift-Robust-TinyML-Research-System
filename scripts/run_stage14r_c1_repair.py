"""Execute the preregistered all-FP32 explicit C1 preprocessing repair candidates."""
from __future__ import annotations
import csv,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
import joblib,numpy as np,pandas as pd,yaml
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"results/embedded";EXP=ROOT/"embedded/experimental/c1_preprocessing_repair";EID="EXP-EMBED-C1-PREPROC-REPAIR-001"
CANDS=["C1-PREPROC-P0-BASELINE","C1-PREPROC-P1-RECIPROCAL","C1-PREPROC-P2-AFFINE","C1-PREPROC-P3-SPLIT_MEAN","C1-PREPROC-P4-COMPENSATED"]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,rows):pd.DataFrame(rows).to_csv(OUT/name,index=False)
def init(a,w=8):
 f=np.asarray(a,np.float32).reshape(-1);return ",\n  ".join(", ".join(f"{float(x):.9g}f" for x in f[i:i+w]) for i in range(0,len(f),w))
def rel(a,b):return np.abs(a-b)/np.maximum(np.abs(a),1e-8)

def verify():
 s14=pd.read_csv(OUT/"stage14_manifest.csv");registered=dict(zip(s14.artifact_path,s14.sha256));s13=pd.read_csv(OUT/"stage13_manifest.csv");registered.update(dict(zip(s13.artifact_path,s13.sha256)))
 req=["artifacts/models/BASE-FIXED-C1-001.joblib","configs/embedded_equivalence_protocol.yaml","results/embedded/stage14_manifest.csv","data/manifests/embedded_golden_vectors.csv","data/manifests/embedded_boundary_vectors.csv","embedded/generated/c1/model_c1.c","embedded/generated/c1/model_c1.h","embedded/generated/c1/preprocessing_c1.c","embedded/generated/c1/preprocessing_c1.h","embedded/generated/c1/inference_c1.c","results/embedded/stage14_preprocessing_equivalence.csv","results/embedded/stage14_output_equivalence.csv","results/embedded/stage14_decision_equivalence.csv","results/embedded/stage14_c1_xai_equivalence.csv"]
 rows=[]
 for r in req:
  p=ROOT/r;actual=sha(p);expected=registered.get(r)
  if r.startswith("artifacts/models"):
   q=pd.read_csv(OUT/"stage14_input_manifest.csv");expected=q.loc[q.artifact_path.eq(r),"sha256"].iloc[0]
  if expected and actual!=expected:raise RuntimeError(f"BLOCKED_INPUT_INTEGRITY {r}")
  rows.append({"experiment_id":EID,"artifact_path":r,"sha256":actual,"expected_sha256":expected or actual,"verification_status":"VERIFIED"})
 pipe=joblib.load(ROOT/req[0]);s=pipe.named_steps["scaler"];h=hashlib.sha256(np.concatenate([s.mean_,s.scale_,s.var_]).astype("<f8").tobytes()).hexdigest();p13=pd.read_csv(OUT/"stage13_preprocessing_inventory.csv");expected=p13.loc[p13.model_id.eq("MODEL-C1"),"constants_sha256"].iloc[0]
 if h!=expected:raise RuntimeError("BLOCKED_INPUT_INTEGRITY scaler")
 rows.append({"experiment_id":EID,"artifact_path":"MODEL-C1:frozen_scaler_constants","sha256":h,"expected_sha256":expected,"verification_status":"VERIFIED"});write("stage14r_input_manifest.csv",rows)

def generate():
 pipe=joblib.load(ROOT/"artifacts/models/BASE-FIXED-C1-001.joblib");s=pipe.named_steps["scaler"];mean=s.mean_.astype(np.float64);scale=s.scale_.astype(np.float64);mean_hi=mean.astype(np.float32);mean_lo=(mean-mean_hi.astype(np.float64)).astype(np.float32);inv=1.0/scale;inv_hi=inv.astype(np.float32);inv_lo=(inv-inv_hi.astype(np.float64)).astype(np.float32);a=inv_hi;b=(-mean/scale).astype(np.float32)
 arrays={"mean":mean_hi,"scale":scale.astype(np.float32),"inverse_scale":inv_hi,"affine_a":a,"affine_b":b,"mean_hi":mean_hi,"mean_lo":mean_lo,"inverse_scale_hi":inv_hi,"inverse_scale_lo":inv_lo}
 header='#ifndef REPAIR_CANDIDATES_H\n#define REPAIR_CANDIDATES_H\nextern const char *repair_candidate_ids[5];\nint repair_preprocess(int candidate,const float raw[128],float z[128]);\n#endif\n'
 source='#include "repair_candidates.h"\n#include <math.h>\nconst char *repair_candidate_ids[5]={'+','.join('"'+x+'"' for x in CANDS)+'};\n'+''.join(f'static const float {k}[128]={{\n  {init(v)}\n}};\n' for k,v in arrays.items())+'int repair_preprocess(int c,const float x[128],float z[128]){for(int i=0;i<128;i++){if(!isfinite(x[i]))return 0;switch(c){case 0:z[i]=(x[i]-mean[i])/scale[i];break;case 1:z[i]=(x[i]-mean[i])*inverse_scale[i];break;case 2:z[i]=x[i]*affine_a[i]+affine_b[i];break;case 3:{float d=(x[i]-mean_hi[i])-mean_lo[i];z[i]=d/scale[i];break;}case 4:{float d=(x[i]-mean_hi[i])-mean_lo[i];z[i]=d*inverse_scale_hi[i]+d*inverse_scale_lo[i];break;}default:return 0;}}return 1;}\n'
 (EXP/"repair_candidates.h").write_text(header,encoding="utf-8",newline="\n");(EXP/"repair_candidates.c").write_text(source,encoding="utf-8",newline="\n")
 rows=[]
 refs={"mean":mean,"scale":scale,"inverse_scale":inv,"affine_a":inv,"affine_b":-mean/scale,"mean_hi":mean,"mean_lo":mean-mean_hi.astype(np.float64),"inverse_scale_hi":inv,"inverse_scale_lo":inv-inv_hi.astype(np.float64)}
 mapping={CANDS[0]:["mean","scale"],CANDS[1]:["mean","inverse_scale"],CANDS[2]:["affine_a","affine_b"],CANDS[3]:["mean_hi","mean_lo","scale"],CANDS[4]:["mean_hi","mean_lo","inverse_scale_hi","inverse_scale_lo"]}
 for cand,names in mapping.items():
  for name in names:
   src=np.asarray(refs[name],np.float64);dst=np.asarray(arrays[name],np.float32);rows.append({"experiment_id":EID,"candidate_id":cand,"constant_name":name,"elements":128,"source_dtype":"float64_offline_reference","stored_dtype":"float32","max_absolute_conversion_error":np.abs(src-dst.astype(float)).max(),"max_relative_conversion_error":rel(src,dst.astype(float)).max(),"source_sha256":hashlib.sha256(src.astype("<f8").tobytes()).hexdigest(),"stored_sha256":hashlib.sha256(dst.astype("<f4").tobytes()).hexdigest()})
 write("stage14r_candidate_constants.csv",rows)
 # Deterministic generation check.
 h=(sha(EXP/"repair_candidates.h"),sha(EXP/"repair_candidates.c"));return pipe,h

def compile_run(pipe,genhash):
 gold=pd.read_csv(ROOT/"data/manifests/embedded_golden_vectors.csv");gold=gold[gold.model_id.eq("MODEL-C1")];raw=[f"raw_feature_{i:03d}" for i in range(128)];vec=EXP/"c1_repair_vectors.csv";gold[["sample_id",*raw]].to_csv(vec,index=False,header=False)
 exe=EXP/"c1_repair_host.exe";out=EXP/"c1_repair_outputs.csv";out2=EXP/"c1_repair_outputs_repeat.csv";cmd=[sys.executable,"-m","ziglang","cc","-O2","-std=c11","-fno-fast-math","-ffp-contract=off",f"-I{EXP}",f"-I{ROOT/'embedded/generated/c1'}",str(EXP/"harness.c"),str(EXP/"repair_candidates.c"),str(ROOT/"embedded/generated/c1/model_c1.c"),"-o",str(exe),"-lm"]
 subprocess.run(cmd,check=True,capture_output=True,text=True);subprocess.run([str(exe),str(vec),str(out)],check=True);subprocess.run([str(exe),str(vec),str(out2)],check=True)
 if out.read_bytes()!=out2.read_bytes():raise RuntimeError("NONDETERMINISTIC_OUTPUT")
 # Generator source hashes remain byte-identical after a second generation.
 _,h2=generate()
 if genhash!=h2:raise RuntimeError("NONDETERMINISTIC_GENERATION")
 return gold,pd.read_csv(out),[vec,exe,out,out2]," ".join(cmd)

def analyze(pipe,gold,exported):
 cfg=yaml.safe_load((ROOT/"configs/c1_fp32_preprocessing_repair.yaml").read_text());tol=cfg["tolerances"];gold=gold.set_index("sample_id");boundary=set(pd.read_csv(ROOT/"data/manifests/embedded_boundary_vectors.csv").query("model_id=='MODEL-C1'").sample_id);model=pipe.named_steps["model"];s=pipe.named_steps["scaler"]
 pre=[];outputs=[];bounds=[];xai=[];decomp=[];summary=[]
 for cand,frame in exported.groupby("candidate_id",sort=False):
  maxsa=maxpa=maxnorm=0.;decisions=[];bdec=[]
  for e in frame.set_index("sample_id").itertuples():
   r=gold.loc[e.Index];raw64=np.array([r[f"raw_feature_{i:03d}"] for i in range(128)]);raw32=raw64.astype(np.float32);zref=np.array([r[f"transformed_feature_{i:03d}"] for i in range(128)]);zexp=np.array([getattr(e,f"z_{i:03d}") for i in range(128)]);ae=np.abs(zref-zexp);re=rel(zref,zexp)
   for i in range(128):
    passed=ae[i]<=tol["preprocessing"]["max_absolute_error"] and re[i]<=tol["preprocessing"]["max_relative_error"];mag=abs(zref[i]);bins=cfg["diagnostics"]["reference_magnitude_bins"];label=next(f"[{bins[k]},{bins[k+1]})" for k in range(len(bins)-1) if mag>=float(bins[k]) and mag<float(bins[k+1]))
    pre.append({"experiment_id":EID,"candidate_id":cand,"sample_id":e.Index,"feature_id":f"F{i:03d}","reference_value":zref[i],"candidate_value":zexp[i],"absolute_error":ae[i],"relative_error":re[i],"relative_error_denominator":max(abs(zref[i]),1e-8),"abs_reference_z":mag,"reference_magnitude_bin":label,"pass":passed})
    if cand==CANDS[0] and not passed:
     m64=s.mean_[i];sc64=s.scale_[i];m32=np.float32(m64);sc32=np.float32(sc64);d64=raw64[i]-m64;d32=np.float32(raw32[i]-m32);spacing=abs(float(np.spacing(np.float32(zexp[i])))) or np.finfo(np.float32).tiny
     decomp.append({"experiment_id":EID,"sample_id":e.Index,"feature_id":f"F{i:03d}","raw_reference_float64":raw64[i],"raw_fp32":raw32[i],"raw_cast_error":abs(raw64[i]-float(raw32[i])),"mean_float64":m64,"mean_fp32":m32,"mean_cast_error":abs(m64-float(m32)),"scale_float64":sc64,"scale_fp32":sc32,"scale_cast_error":abs(sc64-float(sc32)),"reference_x_minus_mean":d64,"fp32_x_minus_mean":d32,"subtraction_error":abs(d64-float(d32)),"reference_standardized_value":zref[i],"fp32_standardized_value":zexp[i],"absolute_error":ae[i],"relative_error":re[i],"ULP_error":ae[i]/spacing,"cancellation_indicator":abs(d64)/max(abs(raw64[i]),abs(m64),np.finfo(float).tiny),"raw_rounding_contribution":abs((float(raw32[i])-m64)/sc64-zref[i]),"mean_rounding_contribution":abs((raw64[i]-float(m32))/sc64-zref[i]),"scale_rounding_contribution":abs(d64/float(sc32)-zref[i]),"arithmetic_interaction_residual":max(0.,ae[i]-abs((float(raw32[i])-float(m32))/float(sc32)-zref[i]))})
   rs=np.asarray(json.loads(r.decision_scores));rp=np.asarray(json.loads(r.probabilities));es=np.array([getattr(e,f"score_{c}") for c in range(6)]);ep=np.array([getattr(e,f"prob_{c}") for c in range(6)]);se=np.abs(rs-es);pe=np.abs(rp-ep);norm=abs(ep.sum()-1);maxsa=max(maxsa,se.max());maxpa=max(maxpa,pe.max());maxnorm=max(maxnorm,norm);agree=int(e.prediction)==int(r.predicted_label);decisions.append(agree)
   for c in range(6):outputs.append({"experiment_id":EID,"candidate_id":cand,"sample_id":e.Index,"class_label":c+1,"reference_score":rs[c],"candidate_score":es[c],"score_absolute_error":se[c],"score_pass":se[c]<=tol["score_max_absolute_error"],"reference_probability":rp[c],"candidate_probability":ep[c],"probability_absolute_error":pe[c],"probability_pass":pe[c]<=tol["probability_max_absolute_error"],"probability_sum":ep.sum(),"normalization_error":norm,"normalization_pass":norm<=tol["probability_normalization_absolute_error"]})
   order=np.argsort(ep);margin=ep[order[-1]]-ep[order[-2]]
   if e.Index in boundary:bdec.append(agree);bounds.append({"experiment_id":EID,"candidate_id":cand,"sample_id":e.Index,"reference_scores":json.dumps(rs.tolist()),"candidate_scores":json.dumps(es.tolist()),"reference_probabilities":json.dumps(rp.tolist()),"candidate_probabilities":json.dumps(ep.tolist()),"reference_margin":r.margin,"candidate_margin":margin,"reference_prediction":r.predicted_label,"candidate_prediction":e.prediction,"runner_up_class":order[-2]+1,"agreement":agree})
   ci=int(r.predicted_label)-1;ar=model.coef_[ci]*zref;ax=np.array([getattr(e,f"attribution_{i:03d}") for i in range(128)]);aae=np.abs(ar-ax);are=rel(ar,ax);zero=tol["xai"]["sign_reference_zero_threshold"];tops={k:len(set(np.argsort(-np.abs(ar))[:k])&set(np.argsort(-np.abs(ax))[:k]))/k for k in tol["xai"]["top_k"]}
   for i in range(128):xai.append({"experiment_id":EID,"candidate_id":cand,"sample_id":e.Index,"feature_id":f"F{i:03d}","reference_attribution":ar[i],"candidate_attribution":ax[i],"absolute_error":aae[i],"relative_error":are[i],"sign_agreement":abs(ar[i])<=zero or np.sign(ar[i])==np.sign(ax[i]),**{f"top_{k}_overlap":v for k,v in tops.items()},"pass":aae[i]<=tol["xai"]["attribution_max_absolute_error"] and are[i]<=tol["xai"]["attribution_max_relative_error"] and (abs(ar[i])<=zero or np.sign(ar[i])==np.sign(ax[i])) and all(v==1 for v in tops.values())})
  cf=pd.DataFrame([x for x in pre if x["candidate_id"]==cand]);xf=pd.DataFrame([x for x in xai if x["candidate_id"]==cand]);summary.append({"candidate_id":cand,"preprocessing_max_absolute_error":cf.absolute_error.max(),"preprocessing_median_absolute_error":cf.absolute_error.median(),"preprocessing_p95_absolute_error":cf.absolute_error.quantile(.95),"preprocessing_max_relative_error":cf.relative_error.max(),"preprocessing_median_relative_error":cf.relative_error.median(),"preprocessing_p95_relative_error":cf.relative_error.quantile(.95),"failed_feature_rows":int((~cf["pass"]).sum()),"affected_samples":cf.loc[~cf["pass"],"sample_id"].nunique(),"affected_features":cf.loc[~cf["pass"],"feature_id"].nunique(),"score_max_absolute_error":maxsa,"probability_max_absolute_error":maxpa,"normalization_max_error":maxnorm,"golden_agreement":sum(decisions)/len(decisions),"boundary_agreement":sum(bdec)/len(bdec),"xai_failed_rows":int((~xf["pass"]).sum()),"mandatory_pass":bool(cf["pass"].all() and maxsa<=tol["score_max_absolute_error"] and maxpa<=tol["probability_max_absolute_error"] and maxnorm<=tol["probability_normalization_absolute_error"] and all(decisions) and all(bdec) and xf["pass"].all())})
 write("stage14r_preprocessing_equivalence.csv",pre);write("stage14r_output_equivalence.csv",outputs);write("stage14r_boundary_equivalence.csv",bounds);write("stage14r_xai_equivalence.csv",xai);write("stage14r_error_decomposition.csv",decomp);return pd.DataFrame(summary)

def finish(summary,artifacts,cmd):
 cfg=yaml.safe_load((ROOT/"configs/c1_fp32_preprocessing_repair.yaml").read_text());ops={CANDS[0]:(256,1024,0,0,1,1,1),CANDS[1]:(256,1024,0,1,0,1,1),CANDS[2]:(256,1024,0,1,0,1,1),CANDS[3]:(384,1536,1,0,1,2,2),CANDS[4]:(512,2048,2,2,0,3,2)};complexity=[]
 for cand,(const,bytes_,rank,mul,div,add,temp) in ops.items():complexity.append({"experiment_id":EID,"candidate_id":cand,"fp32_constants":const,"constant_bytes":bytes_,"complexity_rank":cfg["complexity_rank"][cand],"multiplications":mul,"divisions":div,"additions_subtractions":add,"temporary_fp32_values":temp,"total_runtime_operations_per_128_features":128*(mul+div+add),"derived_working_buffer_bytes":128*4,"source_code_complexity_proxy":rank+mul+div+add,"measurement_type":"DERIVED_COMPUTATIONAL_STRUCTURE"})
 write("stage14r_complexity.csv",complexity);eligible=summary[summary.mandatory_pass].merge(pd.DataFrame(complexity),on="candidate_id")
 if len(eligible):selected=eligible.sort_values(["complexity_rank","constant_bytes","total_runtime_operations_per_128_features"]).iloc[0].candidate_id;state="REPAIR_DEMONSTRATED"
 else:selected="NONE";state="STRICT_FP32_EXPLICIT_STANDARDIZATION_REPAIR_NOT_DEMONSTRATED"
 selection=[]
 for r in summary.itertuples():selection.append({"experiment_id":EID,"candidate_id":r.candidate_id,"mandatory_pass":r.mandatory_pass,"eligible_for_selection":r.mandatory_pass,"selection_rank":"SELECTED" if r.candidate_id==selected else "NOT_SELECTED","selection_rule":"PASS_ALL_THEN_COMPLEXITY_STORAGE_OPERATIONS_ORDER","repair_state":state,"reason":"selected by frozen lexicographic rule" if r.candidate_id==selected else "failed mandatory criteria" if not r.mandatory_pass else "more complex than selected passing candidate"})
 write("stage14r_candidate_selection.csv",selection);outcome="PASSED" if selected!="NONE" else "FAILED";claims=[{"claim_id":"C-EMBED-C1-REPAIR-01","experiment_id":EID,"status":"SUPPORTED" if outcome=="PASSED" else "UNSUPPORTED","evidence":state},{"claim_id":"C-EMBED-C1-REPAIR-XAI-01","experiment_id":EID,"status":"SUPPORTED" if outcome=="PASSED" else "UNSUPPORTED","evidence":f"selected_candidate={selected}"}];write("stage14r_claim_evaluation.csv",claims)
 proposal=ROOT/"docs/embedded/C1_FUSED_PREPROCESSING_INFERENCE_PROPOSAL.md"
 if outcome=="FAILED":proposal.write_text("# C1 fused preprocessing/inference proposal — not executed\n\nA future separately frozen experiment may derive `w_raw[c,i]=w[c,i]/scale[i]` and `b_raw[c]=intercept[c]-sum_i(w[c,i]*mean[i]/scale[i])`, then infer directly from raw inputs. This cannot retroactively satisfy explicit preprocessing equivalence and was not generated, compiled, or tested in Stage 14R.\n",encoding="utf-8")
 summary.to_csv(OUT/"stage14r_candidate_summary.csv",index=False);env={"experiment_id":EID,"compiler":"ziglang 0.16.0","flags":"-O2 -std=c11 -fno-fast-math -ffp-contract=off","build_command":cmd,"scope":"HOST_FP32_REPAIR","mcu_execution":"NOT_EXECUTED","timestamp":datetime.now(timezone.utc).isoformat()};(OUT/"stage14r_build_environment.json").write_text(json.dumps(env,indent=2)+"\n")
 paths=artifacts+[ROOT/"configs/c1_fp32_preprocessing_repair.yaml",ROOT/"docs/embedded/STAGE14R_C1_PREPROCESSING_REPAIR_PROTOCOL.md",ROOT/"docs/embedded/STAGE14R_C1_PREPROCESSING_REPAIR.md"]+[OUT/x for x in ["stage14r_input_manifest.csv","stage14r_error_decomposition.csv","stage14r_candidate_constants.csv","stage14r_preprocessing_equivalence.csv","stage14r_output_equivalence.csv","stage14r_boundary_equivalence.csv","stage14r_xai_equivalence.csv","stage14r_complexity.csv","stage14r_candidate_selection.csv","stage14r_candidate_summary.csv","stage14r_claim_evaluation.csv","stage14r_build_environment.json"]]+([proposal] if proposal.exists() else [])
 rows=[]
 for p in paths:rows.append({"experiment_id":EID,"artifact_path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"generator":"scripts/run_stage14r_c1_repair.py","source_model_sha256":sha(ROOT/"artifacts/models/BASE-FIXED-C1-001.joblib"),"evidence_state":"EXECUTED_HOST_REPAIR"})
 write("stage14r_manifest.csv",rows);print(json.dumps({"status":outcome,"selected":selected,"repair_state":state,"candidates":summary.to_dict("records")},indent=2))

def main():
 verify();pipe,h=generate();gold,exp,arts,cmd=compile_run(pipe,h);summary=analyze(pipe,gold,exp);finish(summary,[EXP/"repair_candidates.h",EXP/"repair_candidates.c",EXP/"harness.c",*arts],cmd)
if __name__=="__main__":main()
