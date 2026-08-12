"""Deterministic C11 FP32 source generator for Stage-14 Tier-A candidates."""
from __future__ import annotations

import hashlib
from pathlib import Path

import joblib
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def f32(values) -> np.ndarray: return np.asarray(values, dtype=np.float32)
def initializer(values, width=8) -> str:
    flat = f32(values).reshape(-1)
    chunks = [", ".join(f"{float(x):.9g}f" for x in flat[i:i+width]) for i in range(0, len(flat), width)]
    return ",\n  ".join(chunks)
def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content.replace("\r\n", "\n"), encoding="utf-8", newline="\n")
def guard(name: str) -> str: return name.upper().replace(".", "_").replace("/", "_")


def export_model(model_id: str) -> list[Path]:
    short = model_id[-2:].lower(); out = ROOT / f"embedded/generated/{short}"
    pipeline = joblib.load(ROOT / f"artifacts/models/BASE-FIXED-{model_id[-2:]}-001.joblib")
    scaler, model = pipeline.named_steps["scaler"], pipeline.named_steps["model"]
    prefix = short.upper(); files=[]
    ph = out / f"preprocessing_{short}.h"; pc = out / f"preprocessing_{short}.c"
    write(ph, f"#ifndef PREPROCESSING_{prefix}_H\n#define PREPROCESSING_{prefix}_H\n#define {prefix}_INPUTS 128\nextern const float {short}_mean[128];\nextern const float {short}_scale[128];\nint {short}_preprocess(const float raw[128], float z[128]);\n#endif\n")
    write(pc, f'#include "preprocessing_{short}.h"\n#include <math.h>\nconst float {short}_mean[128]={{\n  {initializer(scaler.mean_)}\n}};\nconst float {short}_scale[128]={{\n  {initializer(scaler.scale_)}\n}};\nint {short}_preprocess(const float raw[128],float z[128]){{for(int i=0;i<128;i++){{if(!isfinite(raw[i]))return 0;z[i]=(raw[i]-{short}_mean[i])/{short}_scale[i];}}return 1;}}\n')
    files += [ph, pc]
    mh = out / f"model_{short}.h"; mc = out / f"model_{short}.c"; ih = out / f"inference_{short}.h"; ic = out / f"inference_{short}.c"
    if model_id == "MODEL-C1":
        write(mh, "#ifndef MODEL_C1_H\n#define MODEL_C1_H\nextern const float c1_coef[6*128];\nextern const float c1_intercept[6];\nextern const int c1_classes[6];\n#endif\n")
        write(mc, f'#include "model_c1.h"\nconst float c1_coef[6*128]={{\n  {initializer(model.coef_)}\n}};\nconst float c1_intercept[6]={{ {initializer(model.intercept_)} }};\nconst int c1_classes[6]={{1,2,3,4,5,6}};\n')
        write(ih, "#ifndef INFERENCE_C1_H\n#define INFERENCE_C1_H\nint c1_infer(const float raw[128],float z[128],float scores[6],float probs[6],float contributions[128]);\n#endif\n")
        body = '#include "inference_c1.h"\n#include "preprocessing_c1.h"\n#include "model_c1.h"\n#include <math.h>\nint c1_infer(const float raw[128],float z[128],float s[6],float p[6],float a[128]){if(!c1_preprocess(raw,z))return -1;int best=0;for(int c=0;c<6;c++){float v=c1_intercept[c];for(int i=0;i<128;i++)v+=c1_coef[c*128+i]*z[i];s[c]=v;if(v>s[best])best=c;}float m=s[0];for(int c=1;c<6;c++)if(s[c]>m)m=s[c];float sum=0;for(int c=0;c<6;c++){p[c]=expf(s[c]-m);sum+=p[c];}for(int c=0;c<6;c++)p[c]/=sum;best=0;for(int c=1;c<6;c++)if(p[c]>p[best])best=c;for(int i=0;i<128;i++)a[i]=c1_coef[best*128+i]*z[i];return best;}\n'
    elif model_id == "MODEL-C4":
        assert [x.shape for x in model.coefs_] == [(128,64),(64,32),(32,6)]
        assert [x.shape for x in model.intercepts_] == [(64,),(32,),(6,)] and model.out_activation_ == "softmax"
        write(mh, "#ifndef MODEL_C4_H\n#define MODEL_C4_H\nextern const float c4_w1[128*64],c4_b1[64],c4_w2[64*32],c4_b2[32],c4_w3[32*6],c4_b3[6];\nextern const int c4_classes[6];\n#endif\n")
        write(mc, f'#include "model_c4.h"\nconst float c4_w1[128*64]={{\n  {initializer(model.coefs_[0])}\n}};\nconst float c4_b1[64]={{\n  {initializer(model.intercepts_[0])}\n}};\nconst float c4_w2[64*32]={{\n  {initializer(model.coefs_[1])}\n}};\nconst float c4_b2[32]={{\n  {initializer(model.intercepts_[1])}\n}};\nconst float c4_w3[32*6]={{\n  {initializer(model.coefs_[2])}\n}};\nconst float c4_b3[6]={{ {initializer(model.intercepts_[2])} }};\nconst int c4_classes[6]={{1,2,3,4,5,6}};\n')
        write(ih, "#ifndef INFERENCE_C4_H\n#define INFERENCE_C4_H\nint c4_infer(const float raw[128],float z[128],float scores[6],float probs[6]);\n#endif\n")
        body = '#include "inference_c4.h"\n#include "preprocessing_c4.h"\n#include "model_c4.h"\n#include <math.h>\nint c4_infer(const float raw[128],float z[128],float s[6],float p[6]){float h1[64],h2[32];if(!c4_preprocess(raw,z))return -1;for(int j=0;j<64;j++){float v=c4_b1[j];for(int i=0;i<128;i++)v+=z[i]*c4_w1[i*64+j];h1[j]=v>0?v:0;}for(int j=0;j<32;j++){float v=c4_b2[j];for(int i=0;i<64;i++)v+=h1[i]*c4_w2[i*32+j];h2[j]=v>0?v:0;}for(int j=0;j<6;j++){float v=c4_b3[j];for(int i=0;i<32;i++)v+=h2[i]*c4_w3[i*6+j];s[j]=v;}float m=s[0];for(int j=1;j<6;j++)if(s[j]>m)m=s[j];float sum=0;for(int j=0;j<6;j++){p[j]=expf(s[j]-m);sum+=p[j];}for(int j=0;j<6;j++){p[j]/=sum;s[j]=p[j];}int best=0;for(int j=1;j<6;j++)if(p[j]>p[best])best=j;return best;}\n'
    else: raise ValueError(model_id)
    write(ic, body); files += [mh,mc,ih,ic]
    lineage = out / "lineage.json"
    model_path = ROOT / f"artifacts/models/BASE-FIXED-{model_id[-2:]}-001.joblib"
    write(lineage, '{\n  "model_id": "'+model_id+'",\n  "source_sha256": "'+hashlib.sha256(model_path.read_bytes()).hexdigest()+'",\n  "generator": "src/embedded/export_fp32_common.py",\n  "dtype": "float32",\n  "quantization": "NOT_EXECUTED"\n}\n'); files.append(lineage)
    return files
