"""Freeze GATE-C1-INT8-QUANT-001 without executing any quantization, inference, or accuracy claim.

Scope is deliberately narrow: WEIGHTS-ONLY INT8 (the fused C1 weight matrix), per-tensor
symmetric, zero_point=0. Bias and all activations/inputs remain FLOAT32 in this freeze — full
activation quantization is a distinct, NOT_AUTHORIZED future tier. This script computes only
(a) the quantization mapping specification (a formula, not a measurement) and (b) a pure
byte-counting storage estimate from real frozen parameters. It never quantizes, dequantizes, or
runs the model — computing a roundtrip/rounding error would itself be a quantization-behavior
result, which belongs to the future experiment this gate authorizes, not this freeze.
"""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import joblib, numpy as np, pandas as pd, yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/embedded"
GATE = "GATE-C1-INT8-QUANT-001"
FUTURE = "EXP-TINYML-QUANT-001"  # already registered against RQ9 in research/questions.yaml


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(name: str, rows) -> None:
    pd.DataFrame(rows).to_csv(OUT / name, index=False)


def main() -> None:
    # --- 1. Integrity chain: this gate depends on the real, executed 14F-EXEC/14F-XAI evidence,
    # not just the frozen 14F-GATE protocol. Verify the actual artifacts exist and are unchanged.
    fused_gate = pd.read_csv(OUT / "c1_fused_gate_decision.csv").iloc[0]
    if fused_gate.gate_status != "FROZEN":
        raise RuntimeError("BLOCKED_UPSTREAM_GATE_NOT_FROZEN 14F-GATE")
    req = [
        "artifacts/models/BASE-FIXED-C1-001.joblib",
        "results/embedded/c1_fused_algebraic_spec.csv",
        "results/embedded/c1_fused_storage_analysis.csv",
        "results/embedded/c1_fused_gate_decision.csv",
        "results/embedded/c1_fused_golden_equivalence.csv",
        "results/embedded/c1_fused_boundary_equivalence.csv",
        "results/embedded/c1_fused_xai_attribution_equivalence.csv",
        "configs/embedded_equivalence_protocol.yaml",
    ]
    manifest_rows = [{"gate_id": GATE, "artifact_path": rel, "sha256": sha(ROOT / rel), "verification_status": "PRESENT"} for rel in req]
    write("c1_int8_quant_protocol_input_manifest.csv", manifest_rows)

    # --- 2. Re-derive the real fused C1 parameters (same algebra as 14F-GATE) — never refit.
    pipe = joblib.load(ROOT / req[0])
    s, m = pipe.named_steps["scaler"], pipe.named_steps["model"]
    assert s.mean_.shape == s.scale_.shape == (128,)
    assert m.coef_.shape == (6, 128) and m.intercept_.shape == (6,)
    assert list(m.classes_) == [1, 2, 3, 4, 5, 6]
    w_raw = (m.coef_ / s.scale_[None, :]).astype("float64")
    b_raw = (m.intercept_ - (m.coef_ * s.mean_[None, :] / s.scale_[None, :]).sum(axis=1)).astype("float64")

    # --- 3. Quantization mapping SPECIFICATION only — a formula over real frozen numbers, not a
    # measurement of any resulting error. Symmetric per-tensor INT8: scale = max(|w|) / 127, zero_point = 0.
    weight_abs_max = float(np.abs(w_raw).max())
    per_tensor_scale = weight_abs_max / 127.0
    scheme = [
        {
            "gate_id": GATE,
            "tensor": "C1_FUSED_WEIGHT",
            "dtype": "INT8",
            "granularity": "PER_TENSOR",
            "symmetric": True,
            "zero_point": 0,
            "scale": per_tensor_scale,
            "scale_formula": "max(abs(w_raw)) / 127",
            "source_weight_abs_max": weight_abs_max,
            "elements": int(w_raw.size),
            "status": "SPECIFIED_NOT_EXECUTED",
        },
        {
            "gate_id": GATE,
            "tensor": "C1_FUSED_BIAS",
            "dtype": "FLOAT32",
            "granularity": "NOT_APPLICABLE",
            "symmetric": None,
            "zero_point": None,
            "scale": None,
            "scale_formula": "NOT_QUANTIZED",
            "source_weight_abs_max": None,
            "elements": int(b_raw.size),
            "status": "RETAINED_FP32",
        },
        {
            "gate_id": GATE,
            "tensor": "RAW_INPUT_AND_ALL_ACTIVATIONS",
            "dtype": "FLOAT32",
            "granularity": "NOT_APPLICABLE",
            "symmetric": None,
            "zero_point": None,
            "scale": None,
            "scale_formula": "NOT_QUANTIZED",
            "source_weight_abs_max": None,
            "elements": None,
            "status": "OUT_OF_SCOPE_FOR_THIS_GATE — full activation quantization is a distinct, NOT_AUTHORIZED future tier",
        },
    ]
    write("c1_int8_quant_scheme_spec.csv", scheme)

    # --- 4. Pure byte-counting storage estimate — arithmetic on real element counts, no execution.
    fp32_weight_bytes = w_raw.size * 4
    int8_weight_bytes = w_raw.size * 1
    scale_overhead_bytes = 4  # one FLOAT32 scale; zero_point is fixed at 0, nothing to store
    fp32_bias_bytes = b_raw.size * 4
    fp32_total = fp32_weight_bytes + fp32_bias_bytes
    mixed_total = int8_weight_bytes + scale_overhead_bytes + fp32_bias_bytes
    storage = [
        {"component": "C1_FUSED_WEIGHT", "representation": "FLOAT32 (current, 14F-EXEC)", "elements": int(w_raw.size), "bytes": fp32_weight_bytes, "evidence_state": "DERIVED_FROM_ARCHITECTURE"},
        {"component": "C1_FUSED_WEIGHT", "representation": "INT8 per-tensor symmetric (this gate, unexecuted)", "elements": int(w_raw.size), "bytes": int8_weight_bytes, "evidence_state": "DERIVED_FROM_SPECIFICATION_NOT_MEASURED"},
        {"component": "C1_FUSED_WEIGHT_SCALE", "representation": "FLOAT32 scalar", "elements": 1, "bytes": scale_overhead_bytes, "evidence_state": "DERIVED_FROM_SPECIFICATION_NOT_MEASURED"},
        {"component": "C1_FUSED_BIAS", "representation": "FLOAT32 (unchanged, not quantized)", "elements": int(b_raw.size), "bytes": fp32_bias_bytes, "evidence_state": "DERIVED_FROM_ARCHITECTURE"},
        {"component": "TOTAL_CURRENT_FP32", "representation": "FLOAT32 weights + FLOAT32 bias", "elements": int(w_raw.size + b_raw.size), "bytes": fp32_total, "evidence_state": "DERIVED_FROM_ARCHITECTURE"},
        {"component": "TOTAL_SPECIFIED_MIXED", "representation": "INT8 weights + scale + FLOAT32 bias", "elements": int(w_raw.size + b_raw.size), "bytes": mixed_total, "evidence_state": "DERIVED_FROM_SPECIFICATION_NOT_MEASURED"},
    ]
    write("c1_int8_quant_storage_analysis.csv", storage)

    # --- 5. Inherit (never re-declare) the already-frozen Stage-13 numerical tolerances that a
    # future quantized experiment must satisfy — copied verbatim from the single source of truth.
    eqp = yaml.safe_load((ROOT / "configs/embedded_equivalence_protocol.yaml").read_text(encoding="utf-8"))
    inherited = [{
        "gate_id": GATE,
        "source_file": "configs/embedded_equivalence_protocol.yaml",
        "source_gate_id": eqp["gate_id"],
        "score_max_absolute_error": eqp["levels"]["level_2_model_numerical"]["quantized_future_only"]["score_max_absolute_error"],
        "probability_max_absolute_error": eqp["levels"]["level_2_model_numerical"]["quantized_future_only"]["probability_max_absolute_error"],
        "macro_f1_absolute_degradation_max": eqp["levels"]["level_2_model_numerical"]["quantized_future_only"]["macro_f1_absolute_degradation_max"],
        "all_vector_class_agreement_min": eqp["levels"]["level_3_decision"]["quantized_all_vector_class_agreement_min"],
        "boundary_vector_class_agreement": eqp["levels"]["level_3_decision"]["quantized_boundary_vector_class_agreement"],
    }]
    write("c1_int8_quant_inherited_tolerances.csv", inherited)

    # --- 6. Claims begin UNSUPPORTED — this gate authorizes the future experiment, it does not answer it.
    claims = [
        {"claim_id": "C-EMBED-C1-QUANT-01", "future_experiment_id": FUTURE, "claim": "INT8 weights-only quantized C1-FUSED-F0 satisfies the Stage-13 quantized numerical tolerances.", "initial_status": "UNSUPPORTED", "required_evidence": "quantized inference run against golden/boundary vectors"},
        {"claim_id": "C-EMBED-C1-QUANT-02", "future_experiment_id": FUTURE, "claim": "INT8 weights-only quantized C1-FUSED-F0 preserves class decisions within the Stage-13 quantized agreement thresholds.", "initial_status": "UNSUPPORTED", "required_evidence": "decision agreement vs. FP32 fused reference"},
        {"claim_id": "C-EMBED-C1-QUANT-03", "future_experiment_id": FUTURE, "claim": "INT8 weights-only quantization reduces stored parameter bytes relative to the FP32 fused representation.", "initial_status": "UNSUPPORTED", "required_evidence": "compiled artifact size, not the analytical estimate in this gate"},
    ]
    write("c1_int8_quant_claim_registry.csv", claims)

    # --- 7. Gate decision — everything performance-related stays NOT_EXECUTED / NOT_MEASURED.
    decision = [{
        "gate_id": GATE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gate_status": "FROZEN",
        "scope": "WEIGHTS_ONLY_INT8_PER_TENSOR_SYMMETRIC",
        "base_architecture": "C1-FUSED-F0",
        "performance_experiment_status": "NOT_EXECUTED",
        "future_experiment_id": FUTURE,
        "decision": f"AUTHORIZE {FUTURE} (weights-only INT8 tier only; full activation quantization NOT_AUTHORIZED)",
        "quantization": "NOT_EXECUTED",
        "mcu_execution": "NOT_EXECUTED",
        "compiled_flash": "NOT_MEASURED",
        "mcu_sram": "NOT_MEASURED",
        "mcu_latency": "NOT_MEASURED",
        "energy": "NOT_MEASURED",
    }]
    write("c1_int8_quant_gate_decision.csv", decision)

    # --- 8. Manifest of everything this gate freezes, including the docs/config that define it.
    artifacts = [
        "docs/embedded/C1_INT8_QUANTIZATION_PROTOCOL.md",
        "configs/c1_int8_quantization_protocol.yaml",
    ] + [f"results/embedded/{n}" for n in [
        "c1_int8_quant_protocol_input_manifest.csv",
        "c1_int8_quant_scheme_spec.csv",
        "c1_int8_quant_storage_analysis.csv",
        "c1_int8_quant_inherited_tolerances.csv",
        "c1_int8_quant_claim_registry.csv",
        "c1_int8_quant_gate_decision.csv",
    ]]
    manifest = [{"gate_id": GATE, "artifact_path": rel, "sha256": sha(ROOT / rel), "evidence_state": "PROTOCOL_FROZEN", "performance_result": "NOT_EXECUTED"} for rel in artifacts]
    write("c1_int8_quant_protocol_manifest.csv", manifest)

    print(json.dumps(decision[0], indent=2))


if __name__ == "__main__":
    main()
