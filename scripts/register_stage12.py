"""Register Stage 12 evidence, evaluated claims, and exactly one decision."""
from __future__ import annotations

import csv
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EID = "EXP-XAI-LATENCY-001"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def append(path: Path, fields: list[str], row: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=fields).writerow(row)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
legacy = ROOT / "results/registry/experiment_registry.csv"
existing = read(legacy)
fields = list(existing[0])
if not any(row["experiment_id"] == EID for row in existing):
    append(legacy, fields, {
        "experiment_id": EID, "timestamp": datetime.now(timezone.utc).isoformat(),
        "research_question": "What is the reproducible controlled host cost and computational accounting of each Stage-09 explanation?",
        "protocol": "FROZEN_STAGE12_HOST_COST_V2", "model": "MODEL-C1..C4",
        "representation": "GLOBAL_AND_LOCAL_SEPARATE", "train_batches": "1_REFERENCE_ONLY",
        "validation_batches": "", "test_batches": "2,6,10", "seed": "42",
        "dataset_hash": existing[0]["dataset_hash"],
        "split_hash": next(row["split_hash"] for row in existing if row["experiment_id"] == "BASE-FIXED-C1-001"),
        "config_hash": sha(ROOT / "configs/xai_latency_protocol.yaml"), "git_commit": commit,
        "environment": "results/xai/stage12_host_environment.json", "status": "COMPLETED",
        "metrics_artifact": "results/xai/stage12_latency_summary.csv", "model_artifact": "",
        "notes": "Controlled single-thread host timing only; raw ns retained; operation counts separate; MCU latency, energy, Flash, and SRAM not measured.",
    })

claim_defs = {
    "C-XAI-COST-01": "Local explanation methods differ materially in host computational overhead relative to corresponding baseline inference.",
    "C-XAI-COST-02": "A substantial fraction of local ablation cost is explained by repeated model evaluations.",
    "C-XAI-COST-03": "Intrinsic extraction has lower recurring host cost than perturbation-based generation within comparable global scope.",
    "C-XAI-COST-04": "No single method dominates simultaneously on fidelity, stability, and host computational cost.",
}
evaluated = {row["claim_id"]: row for row in read(ROOT / "results/xai/stage12_claim_evaluation.csv")}
claims_path = ROOT / "paper/claim_evidence_matrix.csv"
claims = read(claims_path)
claim_fields = list(claims[0])
for claim_id, text in claim_defs.items():
    if not any(row["claim_id"] == claim_id for row in claims):
        append(claims_path, claim_fields, {
            "claim_id": claim_id, "candidate_claim": text, "experiment_id": EID,
            "dataset_hash": existing[0]["dataset_hash"],
            "split_hash": next(row["split_hash"] for row in existing if row["experiment_id"] == "BASE-FIXED-C1-001"),
            "config_hash": sha(ROOT / "configs/xai_latency_protocol.yaml"),
            "metric": evaluated[claim_id]["evidence_summary"],
            "result_artifact": "results/xai/stage12_claim_evaluation.csv", "figure": "", "git_commit": commit,
            "status": evaluated[claim_id]["status"],
        })

decisions = ROOT / "results/decisions/research_decisions.csv"
decision_rows = read(decisions)
decision_fields = list(decision_rows[0])
if not any(row["decision_id"] == "DEC-STAGE12-001" for row in decision_rows):
    append(decisions, decision_fields, {
        "decision_id": "DEC-STAGE12-001", "timestamp": datetime.now(timezone.utc).isoformat(),
        "research_question": "RQ9", "experiment_id": EID,
        "observation": "Host cost is reproducibly heterogeneous; intrinsic global extraction is static and cheap, while ablation and permutation costs are dominated by repeated frozen-model evaluation.",
        "evidence_artifacts": "results/xai/stage12_raw_timings.csv|results/xai/stage12_operation_counts.csv|results/xai/stage12_claim_evaluation.csv",
        "interpretation": "The evidence is sufficient to freeze an embedded export protocol, but it does not establish MCU latency, memory, energy, or feasibility.",
        "limitations": "One workstation; warm steady state; permutation uses preregistered 256-sample stratified subsets; no physical hardware measurements.",
        "decision": "PROCEED TO EMBEDDED EXPORT PROTOCOL; do not execute export or hardware stages automatically.",
        "next_experiment": "EMBEDDED_EXPORT_PROTOCOL_PREREGISTRATION", "git_commit": commit,
    })

print("Stage 12 registered; four claims evaluated; DEC-STAGE12-001 appended exactly once.")
