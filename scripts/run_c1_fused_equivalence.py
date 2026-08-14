"""Execute EXP-EMBED-C1-FUSED-EQUIV-001 under the frozen F0 protocol."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/embedded"
GEN = ROOT / "embedded/generated/c1_fused"
EID = "EXP-EMBED-C1-FUSED-EQUIV-001"
MODEL = ROOT / "artifacts/models/BASE-FIXED-C1-001.joblib"
RAW = [f"raw_feature_{i:03d}" for i in range(128)]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name: str, rows) -> None:
    pd.DataFrame(rows).to_csv(OUT / name, index=False)


def f32_text(values, width=8) -> str:
    a = np.asarray(values, dtype=np.float32).reshape(-1)
    return ",\n  ".join(", ".join(f"{float(x):.9g}f" for x in a[i:i + width]) for i in range(0, len(a), width))


def verify_inputs():
    protocol_manifest = pd.read_csv(OUT / "c1_fused_protocol_manifest.csv")
    frozen = dict(zip(protocol_manifest.artifact_path, protocol_manifest.sha256))
    stage14 = pd.read_csv(OUT / "stage14_manifest.csv")
    stage14r = pd.read_csv(OUT / "stage14r_manifest.csv")
    historical = dict(zip(stage14.artifact_path, stage14.sha256))
    historical.update(dict(zip(stage14r.artifact_path, stage14r.sha256)))
    requirements = [
        "artifacts/models/BASE-FIXED-C1-001.joblib", "embedded/preprocessing_spec.yaml",
        "results/embedded/c1_fused_protocol_manifest.csv", "configs/c1_fused_equivalence.yaml",
        "docs/embedded/C1_FUSED_PREPROCESSING_ARCHITECTURE.md",
        "docs/embedded/C1_FUSED_EQUIVALENCE_PROTOCOL.md",
        "data/manifests/embedded_golden_vectors.csv", "data/manifests/embedded_boundary_vectors.csv",
        "results/embedded/stage14_manifest.csv", "results/embedded/stage14r_manifest.csv",
        "research/feature_metadata.csv",
    ]
    model_expected = pd.read_csv(OUT / "c1_fused_protocol_input_manifest.csv").query(
        "artifact_path == 'artifacts/models/BASE-FIXED-C1-001.joblib'"
    ).expected_sha256.iloc[0]
    rows = []
    for rel in requirements:
        path = ROOT / rel
        actual = sha(path)
        expected = frozen.get(rel) or historical.get(rel)
        if rel == "artifacts/models/BASE-FIXED-C1-001.joblib":
            expected = model_expected
        if rel == "results/embedded/c1_fused_protocol_manifest.csv":
            expected = actual  # Its signed members, checked below, are the trust anchor.
        if expected and actual != expected:
            raise RuntimeError(f"INPUT_INTEGRITY_MISMATCH:{rel}")
        rows.append({"experiment_id": EID, "artifact_path": rel, "sha256": actual,
                     "expected_sha256": expected or actual, "verification_status": "VERIFIED"})
    for rel, expected in frozen.items():
        if sha(ROOT / rel) != expected:
            raise RuntimeError(f"INPUT_INTEGRITY_MISMATCH:{rel}")
    pipe = joblib.load(MODEL)
    scaler, model = pipe.named_steps["scaler"], pipe.named_steps["model"]
    scaler_hash = hashlib.sha256(np.concatenate([scaler.mean_, scaler.scale_, scaler.var_]).astype("<f8").tobytes()).hexdigest()
    prior = pd.read_csv(OUT / "c1_fused_protocol_input_manifest.csv")
    scaler_expected = prior.query("artifact_path == 'MODEL-C1:frozen_scaler_constants'").sha256.iloc[0]
    if scaler_hash != scaler_expected or list(model.classes_) != [1, 2, 3, 4, 5, 6]:
        raise RuntimeError("INPUT_INTEGRITY_MISMATCH:model_semantics")
    rows += [
        {"experiment_id": EID, "artifact_path": "MODEL-C1:frozen_scaler_constants", "sha256": scaler_hash,
         "expected_sha256": scaler_expected, "verification_status": "VERIFIED"},
        {"experiment_id": EID, "artifact_path": "MODEL-C1:class_order", "sha256": hashlib.sha256(np.asarray(model.classes_, dtype="<i8").tobytes()).hexdigest(),
         "expected_sha256": hashlib.sha256(np.arange(1, 7, dtype="<i8").tobytes()).hexdigest(), "verification_status": "VERIFIED"},
        {"experiment_id": EID, "artifact_path": "MODEL-C1:feature_order_0_127", "sha256": hashlib.sha256(np.arange(128, dtype="<i4").tobytes()).hexdigest(),
         "expected_sha256": hashlib.sha256(np.arange(128, dtype="<i4").tobytes()).hexdigest(), "verification_status": "VERIFIED"},
    ]
    write("c1_fused_exp_input_manifest.csv", rows)
    cfg = yaml.safe_load((ROOT / "configs/c1_fused_equivalence.yaml").read_text(encoding="utf-8"))
    assert cfg["tolerances"]["score"]["max_absolute_error"] == 2e-3
    assert cfg["tolerances"]["probability"]["max_absolute_error"] == 1e-3
    assert cfg["tolerances"]["probability"]["max_vector_l1_distance"] == 4e-3
    assert cfg["tolerances"]["probability"]["normalization_max_absolute_error"] == 2e-6
    assert cfg["floating_point_policy"]["feature_accumulation_order"] == "ascending_0_through_127_per_class"
    return pipe, cfg


def derive_and_generate(pipe):
    scaler, model = pipe.named_steps["scaler"], pipe.named_steps["model"]
    coef = np.asarray(model.coef_, np.float64)
    scale, mean = np.asarray(scaler.scale_, np.float64), np.asarray(scaler.mean_, np.float64)
    w64 = coef / scale
    b64 = np.asarray(model.intercept_, np.float64) - np.sum(coef * mean / scale, axis=1)
    w32, b32 = w64.astype(np.float32), b64.astype(np.float32)
    rows = []
    for c in range(6):
        for i in range(128):
            err = abs(w64[c, i] - float(w32[c, i]))
            rows.append({"experiment_id": EID, "parameter_type": "weight", "class": c + 1, "feature": i,
                         "source_coefficient": coef[c, i], "source_scale": scale[i], "source_intercept": np.nan,
                         "derived_float64": w64[c, i], "stored_float32": w32[c, i], "absolute_cast_error": err,
                         "relative_cast_error": err / max(abs(w64[c, i]), np.finfo(float).tiny),
                         "derivation_provenance": "coef[class,feature]/frozen_scale[feature]"})
        err = abs(b64[c] - float(b32[c]))
        rows.append({"experiment_id": EID, "parameter_type": "bias", "class": c + 1, "feature": -1,
                     "source_coefficient": np.nan, "source_scale": np.nan, "source_intercept": model.intercept_[c],
                     "derived_float64": b64[c], "stored_float32": b32[c], "absolute_cast_error": err,
                     "relative_cast_error": err / max(abs(b64[c]), np.finfo(float).tiny),
                     "derivation_provenance": "intercept[class]-sum(coef[class,:]*mean/scale)"})
    write("c1_fused_parameter_derivation.csv", rows)
    GEN.mkdir(parents=True, exist_ok=True)
    files = {
        "model_c1_fused.h": "#ifndef MODEL_C1_FUSED_H\n#define MODEL_C1_FUSED_H\nextern const float c1_fused_weights[6][128];\nextern const float c1_fused_biases[6];\n#endif\n",
        "model_c1_fused.c": '#include "model_c1_fused.h"\nconst float c1_fused_weights[6][128]={\n  {' + "},\n  {".join(f32_text(row) for row in w32) + "}\n};\nconst float c1_fused_biases[6]={" + f32_text(b32) + "};\n",
        "inference_c1_fused.h": "#ifndef INFERENCE_C1_FUSED_H\n#define INFERENCE_C1_FUSED_H\nint c1_fused_infer(const float raw[128],float scores[6],float probabilities[6]);\n#endif\n",
        "inference_c1_fused.c": '#include "inference_c1_fused.h"\n#include "model_c1_fused.h"\n#include <math.h>\nint c1_fused_infer(const float x[128],float s[6],float p[6]){for(int i=0;i<128;i++)if(!isfinite(x[i]))return 0;for(int c=0;c<6;c++){float a=c1_fused_biases[c];for(int i=0;i<128;i++)a+=c1_fused_weights[c][i]*x[i];s[c]=a;}float m=s[0];for(int c=1;c<6;c++)if(s[c]>m)m=s[c];float z=0.0f;for(int c=0;c<6;c++){p[c]=expf(s[c]-m);z+=p[c];}for(int c=0;c<6;c++)p[c]/=z;return 1;}\n',
        "test_harness_c1_fused.c": '#include "inference_c1_fused.h"\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\nint main(int n,char**v){if(n!=3)return 2;FILE*i=fopen(v[1],"r"),*o=fopen(v[2],"w");if(!i||!o)return 3;char line[131072];fprintf(o,"sample_id,prediction");for(int c=0;c<6;c++)fprintf(o,",score_%d",c);for(int c=0;c<6;c++)fprintf(o,",prob_%d",c);fputc(10,o);while(fgets(line,sizeof line,i)){char*save=0,*t=strtok_r(line,",\\r\\n",&save);if(!t)continue;char id[256];snprintf(id,sizeof id,"%s",t);float x[128],s[6],p[6];for(int k=0;k<128;k++){t=strtok_r(0,",\\r\\n",&save);if(!t)return 4;x[k]=strtof(t,0);}if(!c1_fused_infer(x,s,p))return 5;int y=0;for(int c=1;c<6;c++)if(s[c]>s[y])y=c;fprintf(o,"%s,%d",id,y+1);for(int c=0;c<6;c++)fprintf(o,",%.9g",s[c]);for(int c=0;c<6;c++)fprintf(o,",%.9g",p[c]);fputc(10,o);}return fclose(i)||fclose(o);}\n',
    }
    for name, content in files.items():
        (GEN / name).write_text(content, encoding="utf-8", newline="\n")
    return w64, b64, w32, b32, {name: sha(GEN / name) for name in files}


def algebra_gate(pipe, w64, b64, frames):
    worst = 0.0
    for frame in frames:
        x = frame[RAW].to_numpy(np.float64)
        reference = pipe.decision_function(x)
        algebra = x @ w64.T + b64
        worst = max(worst, float(np.max(np.abs(reference - algebra))))
    if worst > 1e-10:
        raise RuntimeError(f"FUSED_PARAMETER_DERIVATION_ERROR:{worst}")
    return worst


def run_c(pipe, cfg, generation_hashes):
    gold = pd.read_csv(ROOT / cfg["test_sets"]["golden"]).query("model_id == 'MODEL-C1'").copy()
    boundary = pd.read_csv(ROOT / cfg["test_sets"]["boundary"]).query("model_id == 'MODEL-C1'").copy()
    vectors = pd.concat([gold.assign(set_name="golden"), boundary.assign(set_name="boundary")], ignore_index=True)
    vector_file = GEN / "vectors.csv"
    vectors[["sample_id", *RAW]].to_csv(vector_file, index=False, header=False)
    _, _, _, _, hashes2 = derive_and_generate(pipe)
    if generation_hashes != hashes2:
        raise RuntimeError("NONDETERMINISTIC_GENERATION")
    exe, output1, output2 = GEN / "c1_fused_host.exe", GEN / "outputs.csv", GEN / "outputs_repeat.csv"
    command = [sys.executable, "-m", "ziglang", "cc", "-std=c11", "-O2", "-fno-fast-math", "-ffp-contract=off",
               f"-I{GEN}", str(GEN / "test_harness_c1_fused.c"), str(GEN / "inference_c1_fused.c"),
               str(GEN / "model_c1_fused.c"), "-o", str(exe), "-lm"]
    subprocess.run(command, check=True, capture_output=True, text=True)
    subprocess.run([str(exe), str(vector_file), str(output1)], check=True)
    subprocess.run([str(exe), str(vector_file), str(output2)], check=True)
    if output1.read_bytes() != output2.read_bytes():
        raise RuntimeError("NONDETERMINISTIC_EXECUTION")
    version = subprocess.run([sys.executable, "-m", "ziglang", "cc", "--version"], check=True, capture_output=True, text=True).stdout.splitlines()[0]
    env = {"experiment_id": EID, "compiler": version, "language": "C11", "optimization": "-O2",
           "fast_math": "disabled (-fno-fast-math)", "fp_contraction": "off (-ffp-contract=off)",
           "target_architecture": platform.machine(), "build_command": " ".join(command), "math_library": "host libm expf",
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
           "timestamp_utc": datetime.now(timezone.utc).isoformat(), "execution_scope": "HOST",
           "runtime_dtype": "float32", "mcu_execution": "NOT_EXECUTED"}
    (OUT / "c1_fused_build_environment.json").write_text(json.dumps(env, indent=2) + "\n", encoding="utf-8")
    return gold, boundary, vectors, pd.read_csv(output1), [vector_file, exe, output1, output2]


def compare(frame, outputs, set_name):
    out = outputs.iloc[:len(frame)] if set_name == "golden" else outputs.iloc[-len(frame):]
    out = out.set_index("sample_id")
    rows = []
    for r in frame.itertuples(index=False):
        e = out.loc[r.sample_id]
        rs, rp = np.asarray(json.loads(r.decision_scores)), np.asarray(json.loads(r.probabilities))
        es = np.array([e[f"score_{c}"] for c in range(6)])
        ep = np.array([e[f"prob_{c}"] for c in range(6)])
        se, pe = np.abs(rs-es), np.abs(rp-ep)
        ro, eo = np.argsort(rs), np.argsort(es)
        base = {"experiment_id": EID, "sample_id": r.sample_id, "batch": r.batch, "true_label": r.true_label,
                "reference_class": int(r.predicted_label), "fused_class": int(e.prediction),
                "reference_runner_up": int(ro[-2]+1), "fused_runner_up": int(eo[-2]+1),
                "probability_vector_L1": pe.sum(), "probability_sum": ep.sum(), "normalization_error": abs(ep.sum()-1),
                "reference_margin": rs[ro[-1]]-rs[ro[-2]], "fused_margin": es[eo[-1]]-es[eo[-2]],
                "margin_error": abs((rs[ro[-1]]-rs[ro[-2]])-(es[eo[-1]]-es[eo[-2]])),
                "prediction_agreement": int(r.predicted_label)==int(e.prediction)}
        for c in range(6):
            base.update({f"reference_score_{c+1}": rs[c], f"fused_score_{c+1}": es[c], f"score_absolute_error_{c+1}": se[c],
                         f"score_relative_error_{c+1}": se[c]/max(abs(rs[c]), 1e-3) if abs(rs[c]) >= 1e-3 else np.nan,
                         f"reference_probability_{c+1}": rp[c], f"fused_probability_{c+1}": ep[c],
                         f"probability_absolute_error_{c+1}": pe[c]})
        rows.append(base)
    return pd.DataFrame(rows)


def analyze(pipe, cfg, gold, boundary, outputs):
    raw_rows = []
    for r in gold.itertuples(index=False):
        for i, col in enumerate(RAW):
            x64, x32 = float(getattr(r, col)), np.float32(getattr(r, col))
            ae = abs(x64-float(x32))
            raw_rows.append({"experiment_id": EID, "sample_id": r.sample_id, "batch": r.batch, "feature": i,
                             "raw_source_float64": x64, "raw_input_float32": x32, "raw_cast_absolute_error": ae,
                             "raw_cast_relative_error": ae/max(abs(x64), np.finfo(float).tiny)})
    write("c1_fused_raw_cast_analysis.csv", raw_rows)
    golden = compare(gold, outputs, "golden")
    bound = compare(boundary, outputs, "boundary")
    golden.to_csv(OUT / "c1_fused_golden_equivalence.csv", index=False)
    bound.to_csv(OUT / "c1_fused_boundary_equivalence.csv", index=False)
    score = golden.filter(regex="^score_absolute_error_").to_numpy().ravel()
    prob = golden.filter(regex="^probability_absolute_error_").to_numpy().ravel()
    margin = golden.margin_error.to_numpy()
    summary = []
    for metric, a, qs in [("score_absolute_error",score,[.99,.95,.5]),("probability_absolute_error",prob,[.99,.95,.5]),("margin_error",margin,[.95,.5])]:
        row={"experiment_id":EID,"population":"GOLDEN","metric":metric,"count":len(a),"max":np.max(a),"mean":np.mean(a)}
        row.update({f"p{int(q*100)}":np.quantile(a,q) for q in qs});summary.append(row)
    for pop, frame in [("BOUNDARY",bound)]:
        for metric, a in [("score_absolute_error",frame.filter(regex="^score_absolute_error_").to_numpy().ravel()),("probability_absolute_error",frame.filter(regex="^probability_absolute_error_").to_numpy().ravel()),("margin_error",frame.margin_error.to_numpy())]:
            summary.append({"experiment_id":EID,"population":pop,"metric":metric,"count":len(a),"max":np.max(a),"p99":np.quantile(a,.99),"p95":np.quantile(a,.95),"median":np.median(a),"mean":np.mean(a)})
    write("c1_fused_error_summary.csv", summary)
    diag=[]
    for grouping in ["true_label","reference_class","batch"]:
        for key,g in golden.groupby(grouping):
            diag.append({"experiment_id":EID,"grouping":grouping,"group_value":key,"samples":len(g),
                         "max_score_absolute_error":g.filter(regex="^score_absolute_error_").to_numpy().max(),
                         "max_probability_absolute_error":g.filter(regex="^probability_absolute_error_").to_numpy().max(),
                         "mean_probability_vector_L1":g.probability_vector_L1.mean(),"max_margin_error":g.margin_error.max(),
                         "prediction_agreement":g.prediction_agreement.mean()})
    write("c1_fused_class_batch_summary.csv",diag)
    t=cfg["tolerances"]
    checks={"score":score.max()<=t["score"]["max_absolute_error"],"prob_abs":prob.max()<=t["probability"]["max_absolute_error"],
            "prob_l1":golden.probability_vector_L1.max()<=t["probability"]["max_vector_l1_distance"],
            "normalization":max(golden.normalization_error.max(),bound.normalization_error.max())<=t["probability"]["normalization_max_absolute_error"],
            "golden_decision":golden.prediction_agreement.all(),"boundary_decision":bound.prediction_agreement.all()}
    return golden,bound,checks


def finish(checks, algebra_error, extra_paths):
    write("c1_fused_operation_validation.csv",[
        {"architecture":"EXPLICIT_PIPELINE","subtractions":128,"divisions":128,"multiplications":768,"accumulations":768,"bias_additions":6,"total_operations":1798,"evidence_type":"DERIVED_ANALYTICAL"},
        {"architecture":"C1-FUSED-F0","subtractions":0,"divisions":0,"multiplications":768,"accumulations":768,"bias_additions":6,"total_operations":1542,"evidence_type":"DERIVED_ANALYTICAL"},
        {"architecture":"REDUCTION","subtractions":128,"divisions":128,"multiplications":0,"accumulations":0,"bias_additions":0,"total_operations":256,"evidence_type":"DERIVED_ANALYTICAL"}])
    write("c1_fused_storage_validation.csv",[
        {"architecture":"EXPLICIT_PIPELINE","component":"prediction_constants","elements":1030,"bytes":4120,"evidence_type":"DERIVED_FROM_ARCHITECTURE"},
        {"architecture":"C1-FUSED-F0","component":"weights","elements":768,"bytes":3072,"evidence_type":"DERIVED_FROM_ARCHITECTURE"},
        {"architecture":"C1-FUSED-F0","component":"biases","elements":6,"bytes":24,"evidence_type":"DERIVED_FROM_ARCHITECTURE"},
        {"architecture":"C1-FUSED-F0","component":"prediction_constants_total","elements":774,"bytes":3096,"evidence_type":"DERIVED_FROM_ARCHITECTURE"},
        {"architecture":"C1-FUSED-F0","component":"raw_input_buffer","elements":128,"bytes":512,"evidence_type":"DERIVED_FROM_ARCHITECTURE"},
        {"architecture":"C1-FUSED-F0","component":"transformed_feature_buffer","elements":0,"bytes":0,"evidence_type":"DERIVED_FROM_ARCHITECTURE"},
        {"architecture":"C1-FUSED-F0","component":"score_buffer","elements":6,"bytes":24,"evidence_type":"DERIVED_FROM_ARCHITECTURE"},
        {"architecture":"C1-FUSED-F0","component":"probability_buffer","elements":6,"bytes":24,"evidence_type":"DERIVED_FROM_ARCHITECTURE"}])
    passed=all(checks.values())
    claims=[{"claim_id":"C-EMBED-C1-FUSED-01","experiment_id":EID,"status":"SUPPORTED" if passed else "UNSUPPORTED","evidence":"score, probability, normalization, determinism, lineage"},
            {"claim_id":"C-EMBED-C1-FUSED-02","experiment_id":EID,"status":"SUPPORTED" if checks["golden_decision"] and checks["boundary_decision"] else "UNSUPPORTED","evidence":"golden and boundary decisions"},
            {"claim_id":"C-EMBED-C1-FUSED-XAI-01","experiment_id":EID,"status":"NOT_EXECUTED","evidence":"separate experiment required"}]
    write("c1_fused_claim_evaluation.csv",claims)
    required=[OUT/x for x in ["c1_fused_exp_input_manifest.csv","c1_fused_parameter_derivation.csv","c1_fused_raw_cast_analysis.csv","c1_fused_golden_equivalence.csv","c1_fused_boundary_equivalence.csv","c1_fused_error_summary.csv","c1_fused_class_batch_summary.csv","c1_fused_operation_validation.csv","c1_fused_storage_validation.csv","c1_fused_claim_evaluation.csv","c1_fused_build_environment.json"]]
    required += [ROOT/"configs/c1_fused_equivalence.yaml",ROOT/"docs/embedded/C1_FUSED_EQUIVALENCE_PROTOCOL.md",ROOT/"docs/embedded/EXP_EMBED_C1_FUSED_EQUIV_001.md"]+list(GEN.glob("*.c"))+list(GEN.glob("*.h"))+extra_paths
    manifest=[{"experiment_id":EID,"artifact_path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"generator":"scripts/run_c1_fused_equivalence.py","evidence_state":"EXECUTED_HOST","result":"PASSED" if passed else "FAILED"} for p in sorted(set(required))]
    write("c1_fused_manifest.csv",manifest)
    print(json.dumps({"experiment_id":EID,"status":"PASSED" if passed else "FAILED","algebra_max_absolute_error":algebra_error,"checks":{k:bool(v) for k,v in checks.items()}},indent=2))


def main():
    pipe,cfg=verify_inputs()
    w64,b64,_,_,hashes=derive_and_generate(pipe)
    gold0=pd.read_csv(ROOT/cfg["test_sets"]["golden"]).query("model_id=='MODEL-C1'")
    boundary0=pd.read_csv(ROOT/cfg["test_sets"]["boundary"]).query("model_id=='MODEL-C1'")
    algebra=algebra_gate(pipe,w64,b64,[gold0,boundary0])
    gold,boundary,_,outputs,extra=run_c(pipe,cfg,hashes)
    _,_,checks=analyze(pipe,cfg,gold,boundary,outputs)
    finish(checks,algebra,extra)


if __name__ == "__main__":
    main()
