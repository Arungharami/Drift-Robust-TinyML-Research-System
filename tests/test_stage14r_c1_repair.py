from __future__ import annotations
import hashlib,re
from pathlib import Path
import pandas as pd,yaml
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"results/embedded";EXP=ROOT/"embedded/experimental/c1_preprocessing_repair"

def test_lineage_and_stage14_immutability():
 rows=pd.read_csv(OUT/"stage14r_input_manifest.csv");assert rows.verification_status.eq("VERIFIED").all()
 for r in rows.itertuples():
  if ":frozen_scaler_constants" not in r.artifact_path:assert hashlib.sha256((ROOT/r.artifact_path).read_bytes()).hexdigest()==r.sha256
 stage14=pd.read_csv(OUT/"stage14_manifest.csv")
 for r in stage14[stage14.artifact_path.str.contains("embedded/generated/c4/")].itertuples():assert hashlib.sha256((ROOT/r.artifact_path).read_bytes()).hexdigest()==r.sha256

def test_baseline_failure_reproduced_exactly():
 old=pd.read_csv(OUT/"stage14_preprocessing_equivalence.csv").query("model_id=='MODEL-C1'");new=pd.read_csv(OUT/"stage14r_preprocessing_equivalence.csv").query("candidate_id=='C1-PREPROC-P0-BASELINE'")
 assert len(old)==len(new)==3712;assert (~old["pass"]).sum()==(~new["pass"]).sum()==41
 assert old.absolute_error.max()==new.absolute_error.max();assert old.relative_error.max()==new.relative_error.max()

def test_all_candidates_retain_every_row_and_near_zero_values():
 rows=pd.read_csv(OUT/"stage14r_preprocessing_equivalence.csv");assert len(rows)==5*3712
 assert (rows.groupby("candidate_id").size()==3712).all();assert (rows.abs_reference_z<1e-4).any()
 assert rows.relative_error_denominator.min()>=1e-8

def test_no_candidate_passes_and_frozen_selection_rule_applied():
 summary=pd.read_csv(OUT/"stage14r_candidate_summary.csv");selection=pd.read_csv(OUT/"stage14r_candidate_selection.csv")
 assert len(summary)==5 and not summary.mandatory_pass.any();assert not selection.eligible_for_selection.any()
 assert set(selection.selection_rank)=={"NOT_SELECTED"};assert set(selection.repair_state)=={"STRICT_FP32_EXPLICIT_STANDARDIZATION_REPAIR_NOT_DEMONSTRATED"}

def test_model_outputs_and_boundary_decisions_pass_for_every_candidate():
 outputs=pd.read_csv(OUT/"stage14r_output_equivalence.csv");boundary=pd.read_csv(OUT/"stage14r_boundary_equivalence.csv")
 assert outputs.score_pass.all() and outputs.probability_pass.all() and outputs.normalization_pass.all()
 assert len(boundary)==5*6 and boundary.agreement.all()

def test_root_cause_decomposition_complete():
 d=pd.read_csv(OUT/"stage14r_error_decomposition.csv");assert len(d)==41
 required=["raw_cast_error","mean_cast_error","scale_cast_error","subtraction_error","ULP_error","cancellation_indicator","raw_rounding_contribution","mean_rounding_contribution","scale_rounding_contribution"]
 assert d[required].notna().all().all()

def test_all_runtime_code_is_fp32_no_quantization_or_training():
 c=(EXP/"repair_candidates.c").read_text(encoding="utf-8")+(EXP/"harness.c").read_text(encoding="utf-8")
 assert "double" not in c and "float " in c
 assert not re.search(r"\b(int8_t|uint8_t|int16_t|float16|zero_point|quantiz)\b",c,re.I)
 script=(ROOT/"scripts/run_stage14r_c1_repair.py").read_text(encoding="utf-8");assert ".fit(" not in script and ".partial_fit(" not in script
 cfg=yaml.safe_load((ROOT/"configs/c1_fp32_preprocessing_repair.yaml").read_text(encoding="utf-8"));assert "-fno-fast-math" in cfg["compiler"]["flags"] and "-ffp-contract=off" in cfg["compiler"]["flags"]

def test_hardware_and_c4_remain_out_of_scope():
 stages=yaml.safe_load((ROOT/"configs/pipeline_stages.yaml").read_text(encoding="utf-8"))["stages"];assert next(x for x in stages if x["id"]=="14R")["status"]=="FAILED";assert next(x for x in stages if x["id"]=="15")["status"]!="EXECUTED"
 doc=(ROOT/"docs/embedded/STAGE14R_C1_PREPROCESSING_REPAIR.md").read_text(encoding="utf-8");assert "NOT_MEASURED" in doc and "C4 remains" in doc
