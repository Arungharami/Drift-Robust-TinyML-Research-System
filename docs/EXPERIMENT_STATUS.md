# Experiment status

This summary is derived from `configs/pipeline_stages.yaml`, which is authoritative. Update the
registry first, then reconcile this document and regenerate portal evidence.

| Area | Status |
|---|---|
| Dataset validation | EXECUTED |
| Chronological drift characterization | EXECUTED (`DRIFT-FIXED-B1-001`) |
| Fixed-origin classical models | EXECUTED |
| Expanding-window adaptation | EXECUTED |
| IID diagnostic | EXECUTED / DIAGNOSTIC_ONLY |
| Resource-aware XAI preparation (Stage 09) | EXECUTED (`EXP-XAI-0001`) |
| Explanation fidelity (Stage 10) | EXECUTED (`EXP-XAI-FIDELITY-001`) — claims predominantly UNSUPPORTED, see `paper/claim_evidence_matrix.csv` |
| Explanation stability (Stage 11) | EXECUTED (`EXP-XAI-STABILITY-001`) — claims predominantly UNSUPPORTED |
| Explanation latency (Stage 12) | EXECUTED (`EXP-XAI-LATENCY-001`) — host-side computational cost only, not MCU latency |
| Deep learning | NOT_EXECUTED |
| Embedded export / numerical equivalence (Stages 13–14F) | PROTOCOL_FROZEN (13, 14F-GATE); FAILED (14, 14R); EXECUTED, host-only, PASSED (14F-EXEC, 14F-XAI) |
| Quantization | NOT_EXECUTED at any tier — RQ9 / `EXP-TINYML-QUANT-001` remains BLOCKED |
| Physical MCU measurements (Stages 15–20) | BLOCKED (`BLOCKED_HARDWARE` — no nRF52840/J-Link/PPK2 detected) |
