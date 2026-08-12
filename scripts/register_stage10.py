"""Register executed Stage 10 exactly once after output validation."""
from __future__ import annotations
import csv, hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; EID="EXP-XAI-FIDELITY-001"
def rows(p):
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def append(p,fields,row):
    exists=p.exists() and p.stat().st_size>0
    with p.open("a",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); (not exists) and w.writeheader(); w.writerow(row)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
legacy=ROOT/"results/registry/experiment_registry.csv"; old=rows(legacy)
if not any(r["experiment_id"]==EID for r in old):
    fields=list(old[0]); append(legacy,fields,{"experiment_id":EID,"timestamp":datetime.now(timezone.utc).isoformat(),"research_question":"Do Stage-09 explanations faithfully identify features that alter frozen model behavior under chronological drift?","protocol":"FIXED_ORIGIN_FROZEN_STAGE10","model":"MODEL-C1..C4","representation":"GLOBAL_LOCAL_SENSOR_FAMILY","train_batches":"1_REFERENCE_ONLY","validation_batches":"","test_batches":"2-10","seed":"42","dataset_hash":old[0]["dataset_hash"],"split_hash":next(r["split_hash"] for r in old if r["experiment_id"]=="BASE-FIXED-C1-001"),"config_hash":sha(ROOT/"configs/xai_fidelity_protocol.yaml"),"git_commit":commit,"environment":"artifacts/explanations/EXP-XAI-0001/environment.json","status":"COMPLETED","metrics_artifact":"results/xai/stage10_fidelity_summary.csv","model_artifact":"","notes":"Frozen models and Batch-1 scaler means; 30 matched controls; 1000 bootstrap replicates; ablation results labelled consistency."})
claims=ROOT/"paper/claim_evidence_matrix.csv"; cr=rows(claims); fields=list(cr[0])
candidate=[
 ("C-XAI-FID-01","Top-ranked features produced greater predictive degradation than matched random features for every tested model/method/batch/K combination.","selected_minus_random with CI","results/xai/stage10_fidelity_global.csv","UNSUPPORTED"),
 ("C-XAI-FID-02","Explanation fidelity was constant across chronological drift batches.","batch-conditioned bootstrap CI","results/xai/stage10_bootstrap_ci.csv","UNSUPPORTED"),
 ("C-XAI-FID-03","Explanation fidelity was equivalent for correct and misclassified predictions.","category-conditioned local fidelity","results/xai/stage10_fidelity_local.csv","UNSUPPORTED")]
for cid,text,metric,artifact,status in candidate:
    if not any(r["claim_id"]==cid for r in cr): append(claims,fields,{"claim_id":cid,"candidate_claim":text,"experiment_id":EID,"dataset_hash":old[0]["dataset_hash"],"split_hash":next(r["split_hash"] for r in old if r["experiment_id"]=="BASE-FIXED-C1-001"),"config_hash":sha(ROOT/"configs/xai_fidelity_protocol.yaml"),"metric":metric,"result_artifact":artifact,"figure":"","git_commit":commit,"status":status})
dec=ROOT/"results/decisions/research_decisions.csv"; dr=rows(dec); fields=list(dr[0])
if not any(r["decision_id"]=="DEC-STAGE10-001" for r in dr): append(dec,fields,{"decision_id":"DEC-STAGE10-001","timestamp":datetime.now(timezone.utc).isoformat(),"research_question":"RQ5","experiment_id":EID,"observation":"Fidelity evidence is positive on average but heterogeneous across model method batch K scope and error condition.","evidence_artifacts":"results/xai/stage10_fidelity_global.csv|results/xai/stage10_fidelity_local.csv|results/xai/stage10_bootstrap_ci.csv","interpretation":"Rankings often identify model-dependent inputs, but no universal explanation-fidelity claim is supported.","limitations":"Mean-reference perturbations may be off-manifold; ablation consistency is partly circular; selected local samples are not the full population.","decision":"Proceed to Stage 11 only as a separate preregistered stability experiment while preserving method-specific fidelity caveats.","next_experiment":"EXP-XAI-STABILITY-001","git_commit":commit})
print(json.dumps({"registered":EID,"claims":"UNSUPPORTED","decision":"DEC-STAGE10-001"}))
