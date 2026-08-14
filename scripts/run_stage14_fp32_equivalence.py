"""Execute frozen Stage-14 standalone FP32 host equivalence for C1 and C4 only."""
from __future__ import annotations

import csv, hashlib, json, platform, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.embedded.export_fp32_common import export_model  # noqa:E402

EID="EXP-EMBED-FP32-EQUIV-001";OUT=ROOT/"results/embedded";TEST=ROOT/"embedded/tests/fp32_equivalence"
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name:str,rows:list[dict[str,Any]]):pd.DataFrame(rows).to_csv(OUT/name,index=False)
def relerr(a,b,floor=1e-8):return np.abs(a-b)/np.maximum(np.abs(a),floor)


def verify_inputs()->None:
    stage13=pd.read_csv(OUT/"stage13_manifest.csv"); registered=dict(zip(stage13.artifact_path,stage13.sha256))
    required=["artifacts/models/BASE-FIXED-C1-001.joblib","artifacts/models/BASE-FIXED-C4-001.joblib","results/embedded/stage13_input_manifest.csv","embedded/preprocessing_spec.yaml","configs/embedded_equivalence_protocol.yaml","data/manifests/embedded_golden_vectors.csv","data/manifests/embedded_boundary_vectors.csv","results/embedded/stage13_candidate_matrix.csv"]
    rows=[]
    for pathstr in required:
        p=ROOT/pathstr;actual=sha(p);expected=registered.get(pathstr)
        if expected and actual!=expected:raise RuntimeError(f"BLOCKED_INPUT_INTEGRITY {pathstr}")
        # Model identity is anchored by the already verified Stage-13 input manifest.
        if pathstr.startswith("artifacts/models"):
            m=pd.read_csv(OUT/"stage13_input_manifest.csv");expected=m.loc[m.path.eq(pathstr),"sha256"].iloc[0]
            if actual!=expected:raise RuntimeError(f"BLOCKED_INPUT_INTEGRITY {pathstr}")
        rows.append({"experiment_id":EID,"artifact_path":pathstr,"sha256":actual,"expected_sha256":expected or actual,"verification_status":"VERIFIED"})
    # Frozen scaler constants are verified independently from serialized-container identity.
    prep=pd.read_csv(OUT/"stage13_preprocessing_inventory.csv")
    for mid in ["MODEL-C1","MODEL-C4"]:
        pipe=joblib.load(ROOT/f"artifacts/models/BASE-FIXED-{mid[-2:]}-001.joblib");s=pipe.named_steps["scaler"];h=hashlib.sha256(np.concatenate([s.mean_,s.scale_,s.var_]).astype("<f8").tobytes()).hexdigest();expected=prep.loc[prep.model_id.eq(mid),"constants_sha256"].iloc[0]
        if h!=expected:raise RuntimeError(f"BLOCKED_INPUT_INTEGRITY scaler {mid}")
        rows.append({"experiment_id":EID,"artifact_path":f"{mid}:frozen_scaler_constants","sha256":h,"expected_sha256":expected,"verification_status":"VERIFIED"})
    write("stage14_input_manifest.csv",rows)


def conversion_and_generation()->list[Path]:
    generated=[];rows=[]
    arrays={}
    for mid in ["MODEL-C1","MODEL-C4"]:
        pipe=joblib.load(ROOT/f"artifacts/models/BASE-FIXED-{mid[-2:]}-001.joblib");s,m=pipe.named_steps["scaler"],pipe.named_steps["model"]
        arrays[mid]={"scaler_mean":s.mean_,"scaler_scale":s.scale_}
        if mid=="MODEL-C1":arrays[mid]|={"coefficients":m.coef_,"intercepts":m.intercept_}
        else:
            for i,x in enumerate(m.coefs_,1):arrays[mid][f"weights_{i}"]=x
            for i,x in enumerate(m.intercepts_,1):arrays[mid][f"biases_{i}"]=x
        for name,a in arrays[mid].items():
            src=np.asarray(a,dtype=np.float64);dst=src.astype(np.float32);ae=np.abs(src-dst.astype(np.float64));re=relerr(src,dst.astype(np.float64))
            rows.append({"experiment_id":EID,"model_id":mid,"parameter_array":name,"shape":json.dumps(list(src.shape)),"source_dtype":"float64","destination_dtype":"float32","elements":src.size,"max_absolute_cast_error":ae.max(),"max_relative_cast_error":re.max(),"source_sha256":hashlib.sha256(src.astype("<f8").tobytes()).hexdigest(),"exported_sha256":hashlib.sha256(dst.astype("<f4").tobytes()).hexdigest()})
        first=export_model(mid);h1={p:sha(p) for p in first};second=export_model(mid);h2={p:sha(p) for p in second}
        if h1!=h2:raise RuntimeError(f"NONDETERMINISTIC_OUTPUT generator {mid}")
        generated+=second
    write("stage14_parameter_conversion.csv",rows);return generated


def build_and_run(generated:list[Path])->tuple[dict[str,Path],list[Path]]:
    golden=pd.read_csv(ROOT/"data/manifests/embedded_golden_vectors.csv");rawcols=[f"raw_feature_{i:03d}" for i in range(128)]
    exes={};artifacts=[];commands=[]
    for short,mid,macro in [("c1","MODEL-C1","MODEL_C1"),("c4","MODEL-C4","MODEL_C4")]:
        subset=golden[golden.model_id.eq(mid)];vec=TEST/f"stage14_{short}_test_vectors.csv";subset[["sample_id",*rawcols]].to_csv(vec,index=False,header=False);artifacts.append(vec)
        src=ROOT/f"embedded/generated/{short}";exe=TEST/f"stage14_{short}_o2.exe";exe0=TEST/f"stage14_{short}_o0.exe"
        sources=[TEST/"harness.c",src/f"model_{short}.c",src/f"preprocessing_{short}.c",src/f"inference_{short}.c"]
        for opt,target in [("-O2",exe),("-O0",exe0)]:
            cmd=[sys.executable,"-m","ziglang","cc",opt,"-std=c11","-fno-fast-math",f"-D{macro}",f"-I{src}",*[str(x) for x in sources],"-o",str(target),"-lm"]
            subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True);commands.append(" ".join(cmd));artifacts.append(target)
        output=TEST/f"stage14_{short}_outputs.csv";output2=TEST/f"stage14_{short}_outputs_repeat.csv";output0=TEST/f"stage14_{short}_outputs_o0.csv"
        subprocess.run([str(exe),str(vec),str(output)],check=True);subprocess.run([str(exe),str(vec),str(output2)],check=True);subprocess.run([str(exe0),str(vec),str(output0)],check=True)
        if output.read_bytes()!=output2.read_bytes():raise RuntimeError(f"NONDETERMINISTIC_OUTPUT {mid}")
        exes[mid]=exe;artifacts += [output,output2,output0]
    version=subprocess.check_output([sys.executable,"-m","ziglang","version"],text=True).strip()
    env={"experiment_id":EID,"compiler":"Zig bundled Clang-compatible C compiler","compiler_version":version,"target_architecture":platform.machine(),"host_platform":platform.platform(),"primary_optimization":"-O2","secondary_optimization":"-O0","floating_point_options":"-fno-fast-math","fma_policy":"compiler default without fast-math","language_standard":"C11","math_library":"Zig bundled libc/libm","build_commands":commands,"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"timestamp":datetime.now(timezone.utc).isoformat(),"scientific_scope":"HOST_COMPILED_EQUIVALENCE","mcu_execution":"NOT_EXECUTED"}
    (OUT/"stage14_build_environment.json").write_text(json.dumps(env,indent=2)+"\n",encoding="utf-8");return exes,artifacts


def compare()->dict[str,dict[str,Any]]:
    cfg=yaml.safe_load((ROOT/"configs/fp32_export_equivalence.yaml").read_text(encoding="utf-8"));gold=pd.read_csv(ROOT/"data/manifests/embedded_golden_vectors.csv");boundary=set(pd.read_csv(ROOT/"data/manifests/embedded_boundary_vectors.csv").sample_id)
    prep_rows=[];out_rows=[];dec_rows=[];bound_rows=[];xai_rows=[];summ={}
    for short,mid in [("c1","MODEL-C1"),("c4","MODEL-C4")]:
        ref=gold[gold.model_id.eq(mid)].set_index("sample_id");exp=pd.read_csv(TEST/f"stage14_{short}_outputs.csv").set_index("sample_id");tol=cfg["tolerances"];score_limit=tol[mid]["score_max_absolute_error"];prob_limit=tol[mid]["probability_max_absolute_error"]
        maxprea=maxprer=maxscore=maxprob=maxnorm=0.;agreements=[];bagreements=[]
        for sid,e in exp.iterrows():
            r=ref.loc[sid];zref=np.array([r[f"transformed_feature_{i:03d}"] for i in range(128)]);zexp=np.array([e[f"z_{i:03d}"] for i in range(128)]);ae=np.abs(zref-zexp);re=relerr(zref,zexp);maxprea=max(maxprea,float(ae.max()));maxprer=max(maxprer,float(re.max()))
            for i in range(128):prep_rows.append({"experiment_id":EID,"model_id":mid,"sample_id":sid,"feature_id":f"F{i:03d}","reference_value":zref[i],"exported_value":zexp[i],"absolute_error":ae[i],"relative_error":re[i],"pass":bool(ae[i]<=tol["preprocessing"]["max_absolute_error"] and re[i]<=tol["preprocessing"]["max_relative_error"])})
            rs=np.asarray(json.loads(r.decision_scores),float);rp=np.asarray(json.loads(r.probabilities),float);es=np.array([e[f"score_{c}"] for c in range(6)]);ep=np.array([e[f"prob_{c}"] for c in range(6)]);se=np.abs(rs-es);pe=np.abs(rp-ep);maxscore=max(maxscore,float(se.max()));maxprob=max(maxprob,float(pe.max()));norm=abs(ep.sum()-1);maxnorm=max(maxnorm,float(norm))
            for c in range(6):out_rows.append({"experiment_id":EID,"model_id":mid,"sample_id":sid,"class_label":c+1,"reference_score":rs[c],"exported_score":es[c],"score_absolute_error":se[c],"score_pass":bool(se[c]<=score_limit),"reference_probability":rp[c],"exported_probability":ep[c],"probability_absolute_error":pe[c],"probability_pass":bool(pe[c]<=prob_limit),"probability_sum":ep.sum(),"normalization_error":norm,"normalization_pass":bool(norm<=tol["probability_normalization_absolute_error"])})
            agree=int(e.prediction)==int(r.predicted_label);agreements.append(agree);isbound=sid in boundary
            if isbound:bagreements.append(agree)
            order=np.argsort(ep);emargin=ep[order[-1]]-ep[order[-2]]
            d={"experiment_id":EID,"sample_id":sid,"model_id":mid,"batch":int(r.batch),"true_class":int(r.true_label),"reference_prediction":int(r.predicted_label),"export_prediction":int(e.prediction),"reference_margin":r.margin,"reference_confidence":r.confidence,"agreement":agree,"boundary_case":isbound};dec_rows.append(d)
            if isbound:bound_rows.append(d|{"reference_top_class":int(r.predicted_label),"export_top_class":int(e.prediction),"export_runner_up_class":int(order[-2]+1),"exported_margin":emargin,"margin_error":abs(float(r.margin)-emargin),"probability_vector_max_error":pe.max(),"analysis_status":"EXECUTED_CANDIDATE"})
            if mid=="MODEL-C1":
                pipe=joblib.load(ROOT/"artifacts/models/BASE-FIXED-C1-001.joblib");ci=int(r.predicted_label)-1;attrs_ref=pipe.named_steps["model"].coef_[ci]*zref;attrs_exp=np.array([e[f"attribution_{i:03d}"] for i in range(128)]);aa=np.abs(attrs_ref-attrs_exp);ar=relerr(attrs_ref,attrs_exp);zero=tol["c1_xai"]["sign_reference_zero_threshold"]
                rankings={k:len(set(np.argsort(-np.abs(attrs_ref))[:k])&set(np.argsort(-np.abs(attrs_exp))[:k]))/k for k in tol["c1_xai"]["top_k"]}
                for i in range(128):xai_rows.append({"experiment_id":EID,"sample_id":sid,"feature_id":f"F{i:03d}","reference_attribution":attrs_ref[i],"exported_attribution":attrs_exp[i],"absolute_error":aa[i],"relative_error":ar[i],"sign_agreement":bool(abs(attrs_ref[i])<=zero or np.sign(attrs_ref[i])==np.sign(attrs_exp[i])),**{f"top_{k}_overlap":v for k,v in rankings.items()},"pass":bool(aa[i]<=tol["c1_xai"]["attribution_max_absolute_error"] and ar[i]<=tol["c1_xai"]["attribution_max_relative_error"] and (abs(attrs_ref[i])<=zero or np.sign(attrs_ref[i])==np.sign(attrs_exp[i])) and all(v==1 for v in rankings.values()))})
        mandatory=maxprea<=tol["preprocessing"]["max_absolute_error"] and maxprer<=tol["preprocessing"]["max_relative_error"] and maxscore<=score_limit and maxprob<=prob_limit and maxnorm<=tol["probability_normalization_absolute_error"] and all(agreements) and all(bagreements)
        summ[mid]={"status":"PASS" if mandatory else "FAIL","max_preprocessing_absolute_error":maxprea,"max_preprocessing_relative_error":maxprer,"max_score_absolute_error":maxscore,"max_probability_absolute_error":maxprob,"max_probability_normalization_error":maxnorm,"golden_agreement":sum(agreements)/len(agreements),"boundary_agreement":sum(bagreements)/len(bagreements)}
    # Preserve the complete frozen 24-vector boundary manifest. C2/C3 are explicitly retained
    # as out-of-scope, never silently omitted or treated as exported implementations.
    boundary_frame=pd.read_csv(ROOT/"data/manifests/embedded_boundary_vectors.csv")
    covered={r["sample_id"] for r in bound_rows}
    for r in boundary_frame.itertuples():
        if r.sample_id not in covered:bound_rows.append({"experiment_id":EID,"sample_id":r.sample_id,"model_id":r.model_id,"batch":r.batch,"true_class":r.true_label,"reference_prediction":r.predicted_label,"export_prediction":"NOT_APPLICABLE","reference_margin":r.margin,"reference_confidence":r.confidence,"agreement":"NOT_APPLICABLE","boundary_case":True,"reference_top_class":r.predicted_label,"export_top_class":"NOT_APPLICABLE","export_runner_up_class":"NOT_APPLICABLE","exported_margin":"NOT_APPLICABLE","margin_error":"NOT_APPLICABLE","probability_vector_max_error":"NOT_APPLICABLE","analysis_status":"NOT_APPLICABLE_STAGE14_C2_C3_OUT_OF_SCOPE"})
    write("stage14_preprocessing_equivalence.csv",prep_rows);write("stage14_output_equivalence.csv",out_rows);write("stage14_decision_equivalence.csv",dec_rows);write("stage14_boundary_analysis.csv",bound_rows);write("stage14_c1_xai_equivalence.csv",xai_rows);return summ


def finalize(generated:list[Path],runtime:list[Path],summ:dict[str,dict[str,Any]])->None:
    storage=[];buffers=[]
    for mid in ["MODEL-C1","MODEL-C4"]:
        conv=pd.read_csv(OUT/"stage14_parameter_conversion.csv");c=conv[conv.model_id.eq(mid)];short=mid[-2:].lower();src=list((ROOT/f"embedded/generated/{short}").glob("*.c"))+list((ROOT/f"embedded/generated/{short}").glob("*.h"))
        storage.append({"experiment_id":EID,"model_id":mid,"source_constant_bytes":int(c.elements.sum()*4),"coefficient_or_weight_bytes":int(c[c.parameter_array.str.contains("coefficient|weights")].elements.sum()*4),"bias_bytes":int(c[c.parameter_array.str.contains("intercept|biases")].elements.sum()*4),"preprocessing_constant_bytes":int(c[c.parameter_array.str.contains("scaler")].elements.sum()*4),"generated_source_file_bytes":sum(p.stat().st_size for p in src),"measurement_type":"DERIVED_FROM_EXPORT","measured_mcu_flash":"NOT_MEASURED"})
    buffers=[{"experiment_id":EID,"model_id":"MODEL-C1","layout":"STRAIGHTFORWARD","elements":128+128+6+6+128,"bytes_fp32":(128+128+6+6+128)*4,"measurement_type":"DERIVED_WORKING_BUFFER_REQUIREMENT"},{"experiment_id":EID,"model_id":"MODEL-C1","layout":"MINIMAL_REUSE","elements":128+6+6+128,"bytes_fp32":(128+6+6+128)*4,"measurement_type":"DERIVED_WORKING_BUFFER_REQUIREMENT"},{"experiment_id":EID,"model_id":"MODEL-C4","layout":"STRAIGHTFORWARD","elements":128+128+64+32+6+6,"bytes_fp32":(128+128+64+32+6+6)*4,"measurement_type":"DERIVED_WORKING_BUFFER_REQUIREMENT"},{"experiment_id":EID,"model_id":"MODEL-C4","layout":"MINIMAL_REUSE","elements":128+128+64+6,"bytes_fp32":(128+128+64+6)*4,"measurement_type":"DERIVED_WORKING_BUFFER_REQUIREMENT","note":"64-element hidden buffer reused for 32-element layer; input and transformed input retained separately."}]
    write("stage14_export_storage.csv",storage);write("stage14_working_buffers.csv",buffers)
    xai=pd.read_csv(OUT/"stage14_c1_xai_equivalence.csv");xpass=bool(xai["pass"].all());claims=[{"claim_id":"C-EMBED-FP32-01","experiment_id":EID,"status":"SUPPORTED" if summ["MODEL-C1"]["status"]=="PASS" else "UNSUPPORTED","evidence":json.dumps(summ["MODEL-C1"],sort_keys=True)},{"claim_id":"C-EMBED-FP32-02","experiment_id":EID,"status":"SUPPORTED" if summ["MODEL-C4"]["status"]=="PASS" else "UNSUPPORTED","evidence":json.dumps(summ["MODEL-C4"],sort_keys=True)},{"claim_id":"C-EMBED-FP32-XAI-01","experiment_id":EID,"status":"SUPPORTED" if xpass else "UNSUPPORTED","evidence":f"all feature/sample criteria pass={xpass}"}];write("stage14_claim_evaluation.csv",claims)
    outcome="PASSED_BOTH" if all(x["status"]=="PASS" for x in summ.values()) else "FAILED" if all(x["status"]=="FAIL" for x in summ.values()) else "PARTIAL"
    (OUT/"stage14_summary.json").write_text(json.dumps({"experiment_id":EID,"scientific_execution_status":"PASSED" if outcome=="PASSED_BOTH" else outcome,"scientific_outcome":outcome,"candidates":summ,"c1_xai_status":"PASS" if xpass else "FAIL","quantization":"NOT_EXECUTED","mcu_deployment":"NOT_EXECUTED","compiled_flash":"NOT_MEASURED","mcu_sram":"NOT_MEASURED","mcu_latency":"NOT_MEASURED","energy":"NOT_MEASURED","public_deployment":"BLOCKED_CREDENTIALS"},indent=2)+"\n",encoding="utf-8")
    paths=generated+runtime+[ROOT/"configs/fp32_export_equivalence.yaml",ROOT/"docs/embedded/STAGE14_FP32_EXPORT_EQUIVALENCE_PROTOCOL.md",ROOT/"docs/embedded/STAGE14_FP32_EXPORT_EQUIVALENCE.md",OUT/"stage14_input_manifest.csv",OUT/"stage14_parameter_conversion.csv",OUT/"stage14_preprocessing_equivalence.csv",OUT/"stage14_output_equivalence.csv",OUT/"stage14_decision_equivalence.csv",OUT/"stage14_boundary_analysis.csv",OUT/"stage14_c1_xai_equivalence.csv",OUT/"stage14_export_storage.csv",OUT/"stage14_working_buffers.csv",OUT/"stage14_build_environment.json",OUT/"stage14_claim_evaluation.csv",OUT/"stage14_summary.json"]
    rows=[]
    for p in paths:
        rows.append({"experiment_id":EID,"artifact_path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"source_model_sha256":sha(ROOT/f"artifacts/models/BASE-FIXED-{('C1' if 'c1' in p.as_posix().lower() else 'C4')}-001.joblib") if ('c1' in p.as_posix().lower() or 'c4' in p.as_posix().lower()) else "MULTIPLE_OR_NOT_APPLICABLE","generator":"src/embedded/export_fp32_common.py" if "embedded/generated" in p.as_posix() else "scripts/run_stage14_fp32_equivalence.py","git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"evidence_state":"EXECUTED_HOST_EQUIVALENCE"})
    write("stage14_manifest.csv",rows);print(json.dumps({"outcome":outcome,"candidates":summ,"c1_xai":"PASS" if xpass else "FAIL"},indent=2))


def main():
    verify_inputs();generated=conversion_and_generation();_,runtime=build_and_run(generated);summ=compare();finalize(generated,runtime,summ)
if __name__=="__main__":main()
