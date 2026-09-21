# GATE-C1-INT8-QUANT-001 — C1 weights-only INT8 quantization protocol

Status: `PROTOCOL_FROZEN`. Depends on `GATE-C1-FUSED-PREPROC-001` (Stage 14F-GATE), which is
itself `PROTOCOL_FROZEN` and built on the executed, host-only, PASSED FP32 equivalence
(Stage 14F-EXEC / 14F-XAI — see `paper/claim_evidence_matrix.csv`). This document, its companion
config `configs/c1_int8_quantization_protocol.yaml`, and the freeze script
`scripts/freeze_c1_int8_quantization_protocol.py` together define what a future quantization
experiment is authorized to do — they do not run that experiment.

## What this gate does and does not do

This gate:

- Fixes a **quantization mapping specification** for the C1-FUSED-F0 weight tensor only:
  INT8, per-tensor symmetric, `zero_point = 0`, `scale = max(abs(w_raw)) / 127`, where `w_raw`
  is the real fused weight matrix already frozen and verified in Stage 14F-GATE.
- Computes a **pure byte-counting storage estimate** from the real element counts of that
  matrix (768 weight elements, 6 bias elements) — arithmetic on known quantities, not a
  measurement of anything executed.
- Inherits, without modification, the quantized-tier numerical and decision tolerances already
  frozen in `configs/embedded_equivalence_protocol.yaml` (`quantized_future_only`,
  `quantized_all_vector_class_agreement_min`, `quantized_boundary_vector_class_agreement`).
- Registers the claims a future experiment (`EXP-TINYML-QUANT-001`, RQ9) would need to support,
  all beginning `UNSUPPORTED`.

This gate explicitly does **not**:

- Quantize, dequantize, or run the model in any form. No rounding error, degradation, or
  accuracy number is computed here — that is quantization *behavior*, which belongs to the
  future experiment, not this freeze.
- Touch the bias vector or any activation/input. Those remain FLOAT32 in this tier; full
  activation quantization is a distinct, **not-authorized** future tier (see
  `docs/TINYML_CANDIDATE_DEVELOPMENT_PROTOCOL.md`, which also gates QAT behind a predefined PTQ
  degradation threshold — not addressed here since no PTQ has run).
- Produce or imply any physical measurement. Compiled Flash, SRAM, on-device latency, and
  energy remain `NOT_MEASURED` until real nRF52840/J-Link/PPK2 evidence exists, per
  `AGENTS.md`'s non-negotiable evidence rules.

## Why weights-only, per-tensor symmetric, INT8 first

- Weights dominate the storage of this model (768 of 774 total parameters); quantizing them
  first captures nearly all the available storage reduction while leaving inference numerically
  simplest to reason about (bias and activations stay FLOAT32, so no accumulator/activation
  scale chain needs to be specified yet).
- Per-tensor (not per-channel) symmetric quantization is the simplest scheme with a
  zero-overhead zero-point, matching the "evaluate PTQ first, escalate only on measured
  degradation" ordering in `docs/TINYML_CANDIDATE_DEVELOPMENT_PROTOCOL.md`.
- This mirrors the Stage 13 / 14F-GATE pattern exactly: freeze a specification and an integrity
  chain against real artifacts, authorize exactly one future experiment ID, and leave every
  performance number `NOT_EXECUTED` / `NOT_MEASURED` until that experiment actually runs.

## Generated artifacts (all `results/embedded/`, written only by the freeze script)

| File | Contents |
|---|---|
| `c1_int8_quant_protocol_input_manifest.csv` | SHA-256 of every upstream artifact this gate depends on |
| `c1_int8_quant_scheme_spec.csv` | The quantization mapping specification per tensor |
| `c1_int8_quant_storage_analysis.csv` | Byte-counting estimate: current FP32 vs. specified mixed INT8/FP32 |
| `c1_int8_quant_inherited_tolerances.csv` | Tolerances copied verbatim from Stage 13's frozen protocol |
| `c1_int8_quant_claim_registry.csv` | Claims this gate authorizes a future experiment to attempt, all `UNSUPPORTED` |
| `c1_int8_quant_gate_decision.csv` | The frozen decision row; all performance/hardware fields `NOT_EXECUTED`/`NOT_MEASURED` |
| `c1_int8_quant_protocol_manifest.csv` | SHA-256 of every artifact this gate itself produces, including this doc and its config |

## Next authorized experiment

`EXP-TINYML-QUANT-001` (RQ9) may apply the scheme in `c1_int8_quant_scheme_spec.csv` to produce
an actual quantized weight tensor, run it against the Stage 13 golden and boundary vectors, and
report real score/probability/decision-agreement numbers against the inherited tolerances. Until
that experiment executes and produces a saved artifact, `docs/EXPERIMENT_STATUS.md` and
`paper/claim_evidence_matrix.csv` must continue to report quantization as `NOT_EXECUTED`.
