from __future__ import annotations
import re
from pathlib import Path
import joblib,numpy as np,pandas as pd,yaml
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"results/embedded"

def test_gate_frozen_but_performance_not_executed():
 d=pd.read_csv(OUT/"c1_int8_quant_gate_decision.csv").iloc[0];assert d.gate_status=="FROZEN";assert d.performance_experiment_status=="NOT_EXECUTED";assert d.future_experiment_id=="EXP-TINYML-QUANT-001"
 assert d.quantization=="NOT_EXECUTED" and d.mcu_execution=="NOT_EXECUTED"
 assert d.compiled_flash==d.mcu_sram==d.mcu_latency==d.energy=="NOT_MEASURED"

def test_depends_on_frozen_and_executed_upstream_gates():
 rows=pd.read_csv(OUT/"c1_int8_quant_protocol_input_manifest.csv");assert rows.verification_status.eq("PRESENT").all()
 for r in rows.itertuples():assert (ROOT/r.artifact_path).exists()
 fused=pd.read_csv(OUT/"c1_fused_gate_decision.csv").iloc[0];assert fused.gate_status=="FROZEN"

def test_scheme_is_weights_only_per_tensor_symmetric_int8():
 scheme=pd.read_csv(OUT/"c1_int8_quant_scheme_spec.csv").set_index("tensor")
 w=scheme.loc["C1_FUSED_WEIGHT"];assert w["dtype"]=="INT8" and w.granularity=="PER_TENSOR" and bool(w.symmetric) is True and w.zero_point==0
 assert w.scale_formula=="max(abs(w_raw)) / 127"
 assert scheme.loc["C1_FUSED_BIAS","status"]=="RETAINED_FP32"
 assert "OUT_OF_SCOPE" in scheme.loc["RAW_INPUT_AND_ALL_ACTIVATIONS","status"]

def test_scale_matches_real_frozen_weights():
 p=joblib.load(ROOT/"artifacts/models/BASE-FIXED-C1-001.joblib");s=p.named_steps["scaler"];m=p.named_steps["model"]
 assert s.mean_.shape==s.scale_.shape==(128,);assert m.coef_.shape==(6,128) and m.intercept_.shape==(6,);assert list(m.classes_)==[1,2,3,4,5,6]
 w_raw=(m.coef_/s.scale_[None,:]).astype("float64");abs_max=float(np.abs(w_raw).max())
 scheme=pd.read_csv(OUT/"c1_int8_quant_scheme_spec.csv").set_index("tensor").loc["C1_FUSED_WEIGHT"]
 assert abs(scheme.source_weight_abs_max-abs_max)<1e-12;assert abs(scheme.scale-abs_max/127.0)<1e-15;assert int(scheme.elements)==w_raw.size

def test_storage_is_pure_byte_counting_not_measurement():
 by_repr=pd.read_csv(OUT/"c1_int8_quant_storage_analysis.csv")
 fp32_w=by_repr[(by_repr.component=="C1_FUSED_WEIGHT")&(by_repr.representation.str.contains("FLOAT32"))].iloc[0]
 int8_w=by_repr[(by_repr.component=="C1_FUSED_WEIGHT")&(by_repr.representation.str.contains("INT8"))].iloc[0]
 assert int(fp32_w.bytes)==3072 and int(int8_w.bytes)==768
 total_fp32=by_repr[by_repr.component=="TOTAL_CURRENT_FP32"].iloc[0];total_mixed=by_repr[by_repr.component=="TOTAL_SPECIFIED_MIXED"].iloc[0]
 assert int(total_fp32.bytes)==3096 and int(total_mixed.bytes)==796
 assert set(by_repr.evidence_state)<={"DERIVED_FROM_ARCHITECTURE","DERIVED_FROM_SPECIFICATION_NOT_MEASURED"}

def test_tolerances_inherited_verbatim_not_redeclared():
 eqp=yaml.safe_load((ROOT/"configs/embedded_equivalence_protocol.yaml").read_text(encoding="utf-8"))
 inherited=pd.read_csv(OUT/"c1_int8_quant_inherited_tolerances.csv").iloc[0]
 q=eqp["levels"]["level_2_model_numerical"]["quantized_future_only"];d=eqp["levels"]["level_3_decision"]
 assert inherited.score_max_absolute_error==q["score_max_absolute_error"]
 assert inherited.probability_max_absolute_error==q["probability_max_absolute_error"]
 assert inherited.macro_f1_absolute_degradation_max==q["macro_f1_absolute_degradation_max"]
 assert inherited.all_vector_class_agreement_min==d["quantized_all_vector_class_agreement_min"]
 assert inherited.boundary_vector_class_agreement==d["quantized_boundary_vector_class_agreement"]

def test_claims_begin_unsupported():
 claims=pd.read_csv(OUT/"c1_int8_quant_claim_registry.csv");assert len(claims)==3 and claims.initial_status.eq("UNSUPPORTED").all()
 assert claims.future_experiment_id.eq("EXP-TINYML-QUANT-001").all()

def test_no_quantization_execution_or_activation_scope_creep_authorized():
 text=(ROOT/"scripts/freeze_c1_int8_quantization_protocol.py").read_text(encoding="utf-8")
 assert ".fit(" not in text and ".partial_fit(" not in text
 assert "np.round" not in text and "astype(\"int8\")" not in text and "astype('int8')" not in text
 cfg=(ROOT/"configs/c1_int8_quantization_protocol.yaml").read_text(encoding="utf-8")
 assert not re.search(r"\b(INT8|INT16|FP16|PTQ|QAT)\s*:\s*(EXECUTED|AUTHORIZED)",cfg)
 assert "FULL_ACTIVATION_QUANTIZATION" in cfg and "QUANTIZATION_AWARE_TRAINING" in cfg
 stages=yaml.safe_load((ROOT/"configs/pipeline_stages.yaml").read_text(encoding="utf-8"))["stages"]
 g=next(s for s in stages if s["id"]=="14Q-GATE");assert g["status"]=="PROTOCOL_FROZEN";assert set(g["depends_on"])=={"14F-EXEC","14F-XAI"}
 assert next(s for s in stages if s["id"]=="15")["status"]!="EXECUTED"
