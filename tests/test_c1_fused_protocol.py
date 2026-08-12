from __future__ import annotations
import hashlib,re
from pathlib import Path
import joblib,numpy as np,pandas as pd,yaml
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"results/embedded"

def test_gate_frozen_but_performance_not_executed():
 d=pd.read_csv(OUT/"c1_fused_gate_decision.csv").iloc[0];assert d.gate_status=="FROZEN";assert d.performance_experiment_status=="NOT_EXECUTED";assert d.future_experiment_id=="EXP-EMBED-C1-FUSED-EQUIV-001"
 assert not (ROOT/"embedded/generated/c1_fused").exists()

def test_immutable_lineage_verified():
 rows=pd.read_csv(OUT/"c1_fused_protocol_input_manifest.csv");assert rows.verification_status.eq("VERIFIED").all()
 for r in rows.itertuples():
  if ":" not in r.artifact_path:assert hashlib.sha256((ROOT/r.artifact_path).read_bytes()).hexdigest()==r.sha256

def test_reference_shapes_class_and_feature_order():
 p=joblib.load(ROOT/"artifacts/models/BASE-FIXED-C1-001.joblib");s=p.named_steps["scaler"];m=p.named_steps["model"]
 assert s.mean_.shape==s.scale_.shape==(128,);assert m.coef_.shape==(6,128) and m.intercept_.shape==(6,);assert list(m.classes_)==[1,2,3,4,5,6]
 fmap=pd.read_csv(ROOT/"results/xai/stage09_feature_map.csv").sort_values("feature_index");assert list(fmap.feature_index)==list(range(1,129)) and len(fmap.original_name.unique())==128

def test_fused_math_and_tolerances_are_explicit():
 cfg=yaml.safe_load((ROOT/"configs/c1_fused_equivalence.yaml").read_text(encoding="utf-8"));assert cfg["candidate"]["count"]==1 and cfg["candidate"]["id"]=="C1-FUSED-F0"
 assert cfg["tolerances"]["score"]["max_absolute_error"]==2e-3;assert cfg["tolerances"]["probability"]["max_absolute_error"]==1e-3
 assert cfg["tolerances"]["decision"]["golden_class_agreement"]==cfg["tolerances"]["decision"]["boundary_class_agreement"]==1.0
 assert "EXPLICIT_STANDARDIZED_FEATURE_EQUIVALENCE" not in cfg["equivalence_levels"]
 algebra=pd.read_csv(OUT/"c1_fused_algebraic_spec.csv");assert set(algebra.component)>={"FUSED_WEIGHT","FUSED_BIAS","FUSED_SCORE"}

def test_fp_policy_raw_type_and_reference_distinction():
 cfg=yaml.safe_load((ROOT/"configs/c1_fused_equivalence.yaml").read_text(encoding="utf-8"));assert cfg["raw_input"]["primary_dtype"]=="FLOAT32";assert cfg["parameter_generation"]["runtime_dtype"]=="FLOAT32"
 assert cfg["parameter_generation"]["derivation_dtype"]=="FLOAT64" and cfg["floating_point_policy"]["runtime_fp64"]=="FORBIDDEN"
 assert cfg["references"]["secondary_may_replace_primary"] is False;assert cfg["floating_point_policy"]["fp_contract"] is False or cfg["floating_point_policy"]["fp_contract"]=="OFF"

def test_xai_is_not_conflated_with_inference():
 cfg=yaml.safe_load((ROOT/"configs/c1_fused_equivalence.yaml").read_text(encoding="utf-8"));x=cfg["xai_dependency"];assert x["selected_scope"]=="A_INFERENCE_FIRST_WITHOUT_XAI" and x["fused_inference_pass_does_not_establish_xai"] is True
 semantics=pd.read_csv(OUT/"c1_fused_xai_semantics.csv");assert semantics.raw_domain_equivalent.str.contains("x_i-mean_i",regex=False).any();assert semantics.incorrect_conflation.str.contains("w_raw[c,i]*x_i",regex=False).any()

def test_analytical_counts_and_hardware_labels():
 op=pd.read_csv(OUT/"c1_fused_operation_analysis.csv").set_index("architecture");assert op.loc["FUSED_MINUS_EXPLICIT","scaler_subtractions"]==-128 and op.loc["FUSED_MINUS_EXPLICIT","scaler_divisions"]==-128 and op.loc["C1-FUSED-F0","transformed_buffer_elements"]==0
 storage=pd.read_csv(OUT/"c1_fused_storage_analysis.csv");assert set(storage.evidence_state)<={"DERIVED_FROM_ARCHITECTURE","DERIVED_BUFFER_REDUCTION"}
 d=pd.read_csv(OUT/"c1_fused_gate_decision.csv").iloc[0];assert d.compiled_flash==d.mcu_sram==d.mcu_latency==d.energy=="NOT_MEASURED"

def test_claims_begin_unsupported_and_history_not_relabeled():
 claims=pd.read_csv(OUT/"c1_fused_claim_registry.csv");assert len(claims)==3 and claims.initial_status.eq("UNSUPPORTED").all()
 assert pd.read_csv(OUT/"stage14_claim_evaluation.csv").status.eq("UNSUPPORTED").all();assert pd.read_csv(OUT/"stage14r_claim_evaluation.csv").status.eq("UNSUPPORTED").all()

def test_no_training_quantization_or_fused_execution_authorized():
 text=(ROOT/"scripts/freeze_c1_fused_protocol.py").read_text(encoding="utf-8");assert ".fit(" not in text and ".partial_fit(" not in text
 cfg=(ROOT/"configs/c1_fused_equivalence.yaml").read_text(encoding="utf-8");assert not re.search(r"\b(INT8|INT16|FP16|PTQ|QAT)\s*:\s*(EXECUTED|AUTHORIZED)",cfg)
 stages=yaml.safe_load((ROOT/"configs/pipeline_stages.yaml").read_text(encoding="utf-8"))["stages"];assert next(s for s in stages if s["id"]=="14F-GATE")["status"]=="PROTOCOL_FROZEN";assert next(s for s in stages if s["id"]=="15")["status"]!="EXECUTED"
