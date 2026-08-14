from __future__ import annotations

import hashlib, json, re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"results/embedded"


def test_stage13_inputs_immutable_and_verified():
    rows=pd.read_csv(OUT/"stage14_input_manifest.csv");assert rows.verification_status.eq("VERIFIED").all()
    for r in rows.itertuples():
        if ":frozen_scaler_constants" not in r.artifact_path:assert hashlib.sha256((ROOT/r.artifact_path).read_bytes()).hexdigest()==r.sha256


def test_generated_parameter_counts_orientation_and_classes():
    conv=pd.read_csv(OUT/"stage14_parameter_conversion.csv");counts=dict(zip(zip(conv.model_id,conv.parameter_array),conv.elements))
    assert counts[("MODEL-C1","coefficients")]==6*128 and counts[("MODEL-C1","intercepts")]==6
    assert counts[("MODEL-C4","weights_1")]==128*64 and counts[("MODEL-C4","weights_2")]==64*32 and counts[("MODEL-C4","weights_3")]==32*6
    assert counts[("MODEL-C4","biases_1")]==64 and counts[("MODEL-C4","biases_2")]==32 and counts[("MODEL-C4","biases_3")]==6
    for model in ["c1","c4"]:
        text=(ROOT/f"embedded/generated/{model}/model_{model}.c").read_text(encoding="utf-8")
        assert "{1,2,3,4,5,6}" in text


def test_generation_and_host_execution_are_deterministic():
    manifest=pd.read_csv(OUT/"stage14_manifest.csv")
    for r in manifest.itertuples():assert hashlib.sha256((ROOT/r.artifact_path).read_bytes()).hexdigest()==r.sha256
    for model in ["c1","c4"]:
        a=(ROOT/f"embedded/tests/fp32_equivalence/stage14_{model}_outputs.csv").read_bytes();b=(ROOT/f"embedded/tests/fp32_equivalence/stage14_{model}_outputs_repeat.csv").read_bytes();o0=(ROOT/f"embedded/tests/fp32_equivalence/stage14_{model}_outputs_o0.csv").read_bytes()
        assert a==b==o0


def test_probability_normalization_and_decisions():
    outputs=pd.read_csv(OUT/"stage14_output_equivalence.csv");dec=pd.read_csv(OUT/"stage14_decision_equivalence.csv");boundary=pd.read_csv(OUT/"stage14_boundary_analysis.csv")
    assert outputs.normalization_pass.all() and outputs.probability_pass.all() and outputs.score_pass.all()
    applicable=boundary[boundary.analysis_status.eq("EXECUTED_CANDIDATE")]
    assert dec.agreement.all() and len(boundary)==24 and len(applicable)==12 and applicable.agreement.astype(bool).all()
    assert (boundary[~boundary.analysis_status.eq("EXECUTED_CANDIDATE")].analysis_status=="NOT_APPLICABLE_STAGE14_C2_C3_OUT_OF_SCOPE").all()


def test_preregistered_preprocessing_failure_is_preserved():
    pre=pd.read_csv(OUT/"stage14_preprocessing_equivalence.csv");summary=json.loads((OUT/"stage14_summary.json").read_text())
    assert (~pre["pass"]).any()
    assert summary["scientific_outcome"]=="FAILED"
    assert summary["candidates"]["MODEL-C1"]["status"]=="FAIL" and summary["candidates"]["MODEL-C4"]["status"]=="FAIL"
    assert summary["candidates"]["MODEL-C1"]["golden_agreement"]==1 and summary["candidates"]["MODEL-C4"]["boundary_agreement"]==1


def test_c1_xai_negative_result_and_exact_topk_are_preserved():
    x=pd.read_csv(OUT/"stage14_c1_xai_equivalence.csv");assert (~x["pass"]).any();assert x.sign_agreement.all()
    for k in [1,3,5,10,20]:assert (x[f"top_{k}_overlap"]==1).all()


def test_no_training_quantization_fast_math_or_hardware_claims():
    sources="\n".join((ROOT/p).read_text(encoding="utf-8") for p in ["src/embedded/export_fp32_common.py","src/embedded/export_c1_fp32.py","src/embedded/export_c4_fp32.py","scripts/run_stage14_fp32_equivalence.py"])
    assert ".fit(" not in sources and ".partial_fit(" not in sources
    generated="\n".join(p.read_text(encoding="utf-8") for p in (ROOT/"embedded/generated").rglob("*.[ch]"))
    assert not re.search(r"\b(int8_t|uint8_t|int16_t|float16|zero_point|quantization_scale)\b",generated)
    config=yaml.safe_load((ROOT/"configs/fp32_export_equivalence.yaml").read_text(encoding="utf-8"));assert "-fno-fast-math" in config["compiler"]["primary_flags"] and "-ffast-math" not in config["compiler"]["primary_flags"]
    summary=json.loads((OUT/"stage14_summary.json").read_text());assert summary["quantization"]=="NOT_EXECUTED" and summary["mcu_deployment"]=="NOT_EXECUTED"
    assert summary["compiled_flash"]==summary["mcu_sram"]==summary["mcu_latency"]==summary["energy"]=="NOT_MEASURED"


def test_stage15_did_not_execute():
    stages=yaml.safe_load((ROOT/"configs/pipeline_stages.yaml").read_text(encoding="utf-8"))["stages"]
    assert next(s for s in stages if s["id"]=="14")["status"]=="FAILED"
    assert next(s for s in stages if s["id"]=="15")["status"]!="EXECUTED"
