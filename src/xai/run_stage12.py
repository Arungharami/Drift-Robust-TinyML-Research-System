"""Stage 12 runner: host-side latency of local explanation methods."""
from __future__ import annotations
import argparse, csv, gc, sys, time
from pathlib import Path
from typing import Any, Callable
import joblib, numpy as np, pandas as pd, yaml

REPO_ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(REPO_ROOT))
from src.data.loader import batch_number, discover_batches, load_batch  # noqa: E402
from src.utils.hashing import sha256_file, stable_hash  # noqa: E402
from src.utils.reproducibility import capture_environment  # noqa: E402
from src.xai.intrinsic import build_intrinsic_explainers  # noqa: E402
from src.xai.local_ablation import SingleFeatureAblationExplainer  # noqa: E402
from src.xai.manifest import write_json  # noqa: E402

def benchmark_callable(call: Callable[[], Any], warmups: int, repeats: int) -> list[int]:
    if warmups < 0 or repeats <= 0: raise ValueError("warmups must be nonnegative and repeats positive")
    for _ in range(warmups): call()
    durations=[]; enabled=gc.isenabled()
    if enabled: gc.disable()
    try:
        for _ in range(repeats):
            start=time.perf_counter_ns(); call(); durations.append(time.perf_counter_ns()-start)
    finally:
        if enabled: gc.enable()
    return durations

def summarize(rows: list[dict[str,Any]]) -> list[dict[str,Any]]:
    frame=pd.DataFrame(rows); out=[]
    for keys,g in frame.groupby(["experiment_id","model_id","method"],sort=True):
        values=g["latency_ns"].astype(float).to_numpy()
        out.append({"experiment_id":keys[0],"model_id":keys[1],"method":keys[2],
          "n_measurements":len(values),"mean_latency_ms":float(values.mean()/1e6),
          "std_latency_ms":float(values.std(ddof=1)/1e6),"median_latency_ms":float(np.median(values)/1e6),
          "p95_latency_ms":float(np.percentile(values,95)/1e6),"minimum_latency_ms":float(values.min()/1e6),
          "maximum_latency_ms":float(values.max()/1e6)})
    return out

def _config(path:Path)->dict[str,Any]:
    c=yaml.safe_load(path.read_text()); required={"protocol_version","experiment_id","dataset_hash","split_hash","eligible_model_ids","model_artifact_paths","sample_path","output_paths"}
    missing=required-set(c)
    if missing: raise ValueError(f"missing config keys: {sorted(missing)}")
    return c

def _csv(path:Path):
    with path.open(newline="",encoding="utf-8") as h:return list(csv.DictReader(h))
def _write(path:Path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def _sample_id(value:str):
    a,b=value.removeprefix("B").split(":");return int(a),int(b)

def run(config_path:Path):
    c=_config(config_path); sample_path=REPO_ROOT/c["sample_path"]; samples=_csv(sample_path)
    locations={_sample_id(r["sample_id"]) for r in samples}; batches_needed={1}|{b for b,_ in locations}
    paths={batch_number(p):p for p in discover_batches(REPO_ROOT/"data"/"raw")}
    data={b:load_batch(paths[b]) for b in batches_needed}; baseline=data[1][0].mean(axis=0)
    raw=[]; warmups=int(c["warmups"]);repeats=int(c["repeats_per_sample"]);limit=int(c["samples_per_model"])
    for model_id in c["eligible_model_ids"]:
        model=joblib.load(REPO_ROOT/c["model_artifact_paths"][model_id])
        chosen=sorted([r for r in samples if r["model_id"]==model_id],key=lambda r:_sample_id(r["sample_id"]))[:limit]
        ablation=SingleFeatureAblationExplainer(model,model_id,baseline)
        intrinsic=next((e for e in build_intrinsic_explainers(model,model_id) if e.method_name=="INTRINSIC_COEFFICIENT" and e.supports_local),None)
        for record in chosen:
            batch,row=_sample_id(record["sample_id"]); x=data[batch][0][row]
            methods={"PREDICT_PROBA_SINGLE":lambda x=x:model.predict_proba(x.reshape(1,-1)),
                     "SINGLE_FEATURE_ABLATION_LOCAL":lambda x=x:ablation.explain_local(x)}
            if intrinsic is not None: methods["INTRINSIC_COEFFICIENT"]=lambda x=x:intrinsic.explain_local(x)
            for method,call in methods.items():
                for repeat,ns in enumerate(benchmark_callable(call,warmups,repeats),1):
                    raw.append({"experiment_id":c["experiment_id"],"model_id":model_id,"method":method,
                      "sample_id":record["sample_id"],"batch":batch,"row_index_in_batch":row,"repeat":repeat,"latency_ns":ns})
    summary=summarize(raw)
    if len(raw)!=int(c["expected_raw_rows"]) or len(summary)!=int(c["expected_summary_rows"]):raise ValueError("unexpected Stage 12 output size")
    raw_path=REPO_ROOT/c["output_paths"]["raw"];summary_path=REPO_ROOT/c["output_paths"]["summary"];artifact=REPO_ROOT/c["output_paths"]["artifact_dir"]
    _write(raw_path,raw);_write(summary_path,summary);artifact.mkdir(parents=True,exist_ok=True)
    write_json(artifact/"config.json",c);(artifact/"config.yaml").write_text(yaml.safe_dump(c,sort_keys=False))
    env=capture_environment(artifact/"environment.json",seed=int(c["random_seed"]))
    (artifact/"run.log").write_text(f"[stage12] raw_rows={len(raw)} summary_rows={len(summary)}\n")
    manifest={"experiment_id":c["experiment_id"],"stage":"12","status":"EXECUTED","created_at":env["timestamp_utc"],"git_commit":env["git_commit"],
      "protocol_version":c["protocol_version"],"config_hash":stable_hash(c),"dataset_hash":c["dataset_hash"],"split_hash":c["split_hash"],
      "host_only":True,"n_raw_rows":len(raw),"n_summary_rows":len(summary),"models":c["eligible_model_ids"],
      "interpretation":"Shared GitHub runner host timing only; not on-device latency.",
      "input_artifacts":{str(sample_path.relative_to(REPO_ROOT)):sha256_file(sample_path)},
      "output_artifacts":{str(raw_path.relative_to(REPO_ROOT)):sha256_file(raw_path),str(summary_path.relative_to(REPO_ROOT)):sha256_file(summary_path)}}
    write_json(artifact/"manifest.json",manifest);print(f"[stage12] status=EXECUTED raw={len(raw)} summaries={len(summary)}");return manifest

def main():
    p=argparse.ArgumentParser();p.add_argument("--config",type=Path,default=Path("configs/xai/stage12_host_latency_v1.yaml"));p.add_argument("--check-config",action="store_true");a=p.parse_args()
    path=a.config if a.config.is_absolute() else REPO_ROOT/a.config
    if a.check_config: print(f"[stage12] config valid: {_config(path)['protocol_version']}")
    else: run(path)
if __name__=="__main__":main()
