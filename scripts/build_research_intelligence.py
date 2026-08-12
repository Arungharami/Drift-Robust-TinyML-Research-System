"""Build normalized evidence registries from existing, immutable research artifacts."""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "results" / "registry"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(path: Path, fieldnames: list[str], data: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN"


def feature_metadata() -> None:
    fmap = rows(ROOT / "results/xai/stage09_feature_map.csv")
    output = []
    for r in fmap:
        kind = r["feature_type"]
        alpha = kind.rsplit("_", 1)[-1] if kind.startswith("EMA") else ""
        if kind == "dR":
            family, phase, meaning = "steady_state_resistance_change", "steady_state", "Absolute resistance change from baseline"
        elif kind == "dR_norm":
            family, phase, meaning = "normalized_resistance_response", "steady_state", "Resistance change normalized to baseline"
        elif kind.startswith("EMAi"):
            family, phase, meaning = "rising_transient_ema", "rising", "Exponential moving average of the rising transient"
        else:
            family, phase, meaning = "decaying_transient_ema", "decaying", "Exponential moving average of the decaying transient"
        output.append({"feature_id": f"F{int(r['feature_index']):03d}", "sensor_id": f"S{r['sensor_id']}", "feature_family": family, "response_phase": phase, "alpha_if_applicable": alpha, "physical_interpretation": meaning, "source_column": r["original_name"]})
    write(ROOT / "research/feature_metadata.csv", ["feature_id", "sensor_id", "feature_family", "response_phase", "alpha_if_applicable", "physical_interpretation", "source_column"], output)


def normalized_registries() -> None:
    legacy = rows(REG / "experiment_registry.csv")
    experiments = []
    artifacts: dict[str, dict[str, object]] = {}
    measurements = []
    rq_map = {"DRIFT-FIXED-B1-001": "RQ1"}
    for r in legacy:
        eid = r["experiment_id"]
        if "IID" in eid: rq = "RQ2"
        elif "EXPAND" in eid: rq = "RQ3"
        elif "XAI" in eid: rq = "RQ5"
        else: rq = rq_map.get(eid, "RQ1")
        xai_stage = "12" if "LATENCY" in eid else "11" if "STABILITY" in eid else "10" if "FIDELITY" in eid else "09"
        experiments.append({"experiment_id": eid, "research_question_id": rq, "hypothesis_id": f"H{rq[2:]}", "stage": xai_stage if "XAI" in eid else "07" if eid.startswith("DRIFT") else "06", "model_id": r["model"], "protocol": r["protocol"], "train_batches": r["train_batches"], "test_batches": r["test_batches"], "seed": r["seed"], "dataset_id": "UCI_GAS_DRIFT_224_V1", "status": "EXECUTED" if r["status"] == "COMPLETED" else r["status"], "git_commit": r["git_commit"], "timestamp": r["timestamp"]})
        for key in ("metrics_artifact", "model_artifact"):
            rel = r.get(key, "").replace("\\", "/")
            path = ROOT / rel
            if rel and path.is_file():
                aid = "ART-" + sha256(path)[:12].upper()
                artifacts[aid] = {"artifact_id": aid, "path": rel, "sha256": sha256(path), "producer_experiment": eid, "git_commit": r["git_commit"], "created_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}
    metric_sources = [ROOT / "results/baselines/fixed_origin_metrics.csv", ROOT / "results/baselines/expanding_window_metrics.csv", ROOT / "results/baselines/iid_diagnostic_metrics.csv"]
    for source in metric_sources:
        if not source.exists(): continue
        aid = "ART-" + sha256(source)[:12].upper()
        artifacts.setdefault(aid, {"artifact_id": aid, "path": source.relative_to(ROOT).as_posix(), "sha256": sha256(source), "producer_experiment": "MULTIPLE", "git_commit": git_commit(), "created_at": datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat()})
        for r in rows(source):
            for metric in ("accuracy", "macro_f1", "balanced_accuracy", "macro_precision", "macro_recall"):
                if r.get(metric, ""):
                    measurements.append({"experiment_id": r["experiment_id"], "metric_name": metric, "value": r[metric], "unit": "proportion", "ci_low": "", "ci_high": "", "n": "", "model_id": r.get("model", ""), "method": "", "batch": r.get("test_batch", ""), "k": "", "measurement_type": "EXECUTED", "evidence_state": "EXECUTED", "artifact_id": aid})
    stage10_manifest = ROOT / "results/xai/stage10_manifest.csv"
    if stage10_manifest.exists():
        for r in rows(stage10_manifest):
            path = ROOT / r["artifact_path"]
            aid = "ART-" + r["sha256"][:12].upper()
            artifacts[aid] = {"artifact_id": aid, "path": r["artifact_path"], "sha256": r["sha256"], "producer_experiment": "EXP-XAI-FIDELITY-001", "git_commit": git_commit(), "created_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}
        ci_path = ROOT / "results/xai/stage10_bootstrap_ci.csv"; ci_aid = "ART-" + sha256(ci_path)[:12].upper()
        for r in rows(ci_path):
            measurements.append({"experiment_id": r["experiment_id"], "metric_name": r["metric_name"], "value": r["estimate"], "unit": r["unit"], "ci_low": r["ci_low"], "ci_high": r["ci_high"], "n": r["n"], "model_id": r["model_id"], "method": r["method"], "batch": r["batch"], "k": r["k"], "measurement_type": r["measurement_type"], "evidence_state": "DERIVED", "artifact_id": ci_aid})
    stage11_manifest = ROOT / "results/xai/stage11_manifest.csv"
    if stage11_manifest.exists():
        for r in rows(stage11_manifest):
            path = ROOT / r["artifact_path"]; aid = "ART-" + r["sha256"][:12].upper()
            artifacts[aid] = {"artifact_id": aid, "path": r["artifact_path"], "sha256": r["sha256"], "producer_experiment": "EXP-XAI-STABILITY-001", "git_commit": git_commit(), "created_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}
        ci_path = ROOT / "results/xai/stage11_bootstrap_ci.csv"; ci_aid = "ART-" + sha256(ci_path)[:12].upper()
        for r in rows(ci_path):
            measurements.append({"experiment_id": r["experiment_id"], "metric_name": r["metric_name"], "value": r["estimate"], "unit": r["unit"], "ci_low": r["ci_low"], "ci_high": r["ci_high"], "n": r["n"], "model_id": r["model_id"], "method": r["method"], "batch": r["comparison"], "k": "", "measurement_type": r["status"], "evidence_state": "DERIVED", "artifact_id": ci_aid})
    stage12_manifest = ROOT / "results/xai/stage12_manifest.csv"
    if stage12_manifest.exists():
        for r in rows(stage12_manifest):
            path = ROOT / r["artifact_path"]; aid = "ART-" + r["sha256"][:12].upper()
            artifacts[aid] = {"artifact_id": aid, "path": r["artifact_path"], "sha256": r["sha256"], "producer_experiment": "EXP-XAI-LATENCY-001", "git_commit": git_commit(), "created_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}
        ci_path = ROOT / "results/xai/stage12_bootstrap_ci.csv"; ci_aid = "ART-" + sha256(ci_path)[:12].upper()
        for r in rows(ci_path):
            measurements.append({"experiment_id": r["experiment_id"], "metric_name": r["metric_name"], "value": r["estimate"], "unit": r["unit"], "ci_low": r["ci_low"], "ci_high": r["ci_high"], "n": r["n"], "model_id": r["model_id"], "method": r["method"], "batch": r["batch"], "k": "", "measurement_type": "MEASURED", "evidence_state": "MEASURED", "artifact_id": ci_aid})
    stage14_manifest = ROOT / "results/embedded/stage14_manifest.csv"
    if stage14_manifest.exists():
        for r in rows(stage14_manifest):
            path = ROOT / r["artifact_path"]; aid = "ART-" + r["sha256"][:12].upper()
            artifacts[aid] = {"artifact_id": aid, "path": r["artifact_path"], "sha256": r["sha256"], "producer_experiment": "EXP-EMBED-FP32-EQUIV-001", "git_commit": r["git_commit"], "created_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}
    write(REG / "experiments.csv", ["experiment_id", "research_question_id", "hypothesis_id", "stage", "model_id", "protocol", "train_batches", "test_batches", "seed", "dataset_id", "status", "git_commit", "timestamp"], experiments)
    write(REG / "measurements.csv", ["experiment_id", "metric_name", "value", "unit", "ci_low", "ci_high", "n", "model_id", "method", "batch", "k", "measurement_type", "evidence_state", "artifact_id"], measurements)
    write(REG / "artifacts.csv", ["artifact_id", "path", "sha256", "producer_experiment", "git_commit", "created_at"], list(artifacts.values()))
    claims = rows(ROOT / "paper/claim_evidence_matrix.csv")
    write(REG / "claims.csv", ["claim_id", "claim_text", "status", "required_evidence", "supporting_artifacts"], [{"claim_id": r.get("claim_id", ""), "claim_text": r.get("candidate_claim", ""), "status": r.get("status", "UNSUPPORTED"), "required_evidence": r.get("metric", ""), "supporting_artifacts": r.get("result_artifact", "")} for r in claims])


def main() -> None:
    feature_metadata()
    normalized_registries()
    print(json.dumps({"status": "EXECUTED", "generated": ["research/feature_metadata.csv", "results/registry/experiments.csv", "results/registry/measurements.csv", "results/registry/artifacts.csv", "results/registry/claims.csv"]}, indent=2))


if __name__ == "__main__":
    main()
