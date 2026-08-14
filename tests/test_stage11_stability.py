import csv,hashlib
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1];EID="EXP-XAI-STABILITY-001"
def rows(path):
 with (ROOT/path).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def test_stage11_outputs_and_stage12_gate():
 stages=yaml.safe_load((ROOT/"configs/pipeline_stages.yaml").read_text(encoding="utf-8"))["stages"];s11=next(s for s in stages if s["id"]=="11");s12=next(s for s in stages if s["id"]=="12")
 assert s11["status"]=="EXECUTED" and all((ROOT/p).exists() for p in s11["artifact_paths"]);assert s12["status"]=="EXECUTED"
def test_stage10_hashes_unchanged_and_stage11_manifest_valid():
 for r in rows("results/xai/stage10_manifest.csv"):assert hashlib.sha256((ROOT/r["artifact_path"]).read_bytes()).hexdigest()==r["sha256"]
 for r in rows("results/xai/stage11_manifest.csv"):assert r["experiment_id"]==EID and hashlib.sha256((ROOT/r["artifact_path"]).read_bytes()).hexdigest()==r["sha256"]
def test_rank_ranges_order_and_ci():
 for r in rows("results/xai/stage11_global_rank_stability.csv"):
  assert int(r["batch_a"])<int(r["batch_b"]);assert -1<=float(r["spearman"])<=1 and -1<=float(r["kendall_tau_b"])<=1
  assert all(0<=float(r[f"jaccard_at_{k}"])<=1 for k in (5,10,20))
 for r in rows("results/xai/stage11_bootstrap_ci.csv"):
  if r["ci_low"] and r["ci_high"] and r["estimate"]:assert float(r["ci_low"])<=float(r["estimate"])<=float(r["ci_high"])
  assert r["unit"] and int(r["n"])>0
def test_direction_not_applicable_is_not_zero():
 for r in rows("results/xai/stage11_direction_stability.csv"):
  if r["status"]=="NOT_APPLICABLE":assert r["sign_agreement"]==r["top_k_sign_agreement"]==r["sign_flip_frequency"]=="NOT_APPLICABLE"
def test_local_lineage_class_matching_and_no_duplicate_targets():
 source={(r["model_id"],r["sample_id"]):r for r in rows("results/xai/stage09_local_samples.csv")}
 for r in rows("results/xai/stage11_local_neighbor_stability.csv"):
  assert (r["model_id"],r["center_sample_id"]) in source and (r["model_id"],r["neighbor_sample_id"]) in source
 matches=rows("results/xai/stage11_cross_batch_matches.csv");seen=set()
 for r in matches:
  a=source[(r["model_id"],r["source_sample_id"])];b=source[(r["model_id"],r["target_sample_id"])]
  assert a["true_label"]==b["true_label"]==r["true_class"] and int(r["source_batch"])<int(r["target_batch"])
  key=(r["model_id"],r["method"],r["source_batch"],r["target_batch"],r["target_sample_id"]);assert key not in seen;seen.add(key)
def test_figure_sources_and_portal_registry_agree():
 manifest=rows("results/xai/stage11_manifest.csv");paths={r["artifact_path"] for r in manifest}
 for svg in paths:
  if svg.startswith("results/figures/stab_") and svg.endswith(".svg"):assert f"results/figures/sources/{Path(svg).stem}.csv" in paths
 exporter=(ROOT/"scripts/portal/export_evidence.py").read_text(encoding="utf-8");assert '"stability_status": "EXECUTED" if stability_manifest' in exporter
