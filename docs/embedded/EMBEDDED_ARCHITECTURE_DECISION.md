# Embedded architecture decision

## Decision

Stage 13 status is `PROTOCOL_FROZEN`; every export and hardware status remains `NOT_EXECUTED`. The next separately authorized experiment should be an **FP32 export equivalence test**, beginning with MODEL-C1 and MODEL-C4. This does not authorize quantization.

## Deterministic tiers

- **TIER A — EXPORT FIRST:** MODEL-C1 using direct static coefficients and MODEL-C4 using direct static dense FP32 arrays. Both offer transparent deterministic arithmetic and modest analytical storage. C1 may additionally test its already-defined local coefficient contribution; C4 begins with no on-device XAI.
- **TIER B — EXPORT IF RESOURCES ALLOW:** MODEL-C2 using generated/static tree traversal. It is retained because its scientific explanation evidence is relevant, not rejected for host speed. Its 200 trees, 10,230 nodes, and representation metadata make compiled-size evidence essential.
- **TIER C — RESEARCH COMPARATOR:** MODEL-C3. Its 131-vector RBF prediction rule is analytically representable, but kernel, multiclass coupling, and probability calibration are difficult to reproduce, while current sensor-level XAI evidence is weak. Prediction deployability remains separate from explanation deployability.

No weighted score was used. Tiering applies hard considerations: faithful static representation, structural size, verification difficulty, current explanation evidence, and whether FP32 equivalence can be tested transparently.

## Explanation architecture

- C1 global coefficient importance and C2 global impurity importance can be stored as `PRECOMPUTED_STATIC_EXPLANATION`; they are global, never local.
- C1 local contribution retains the Stage-09 multiclass coefficient definition. It needs transformed features, class coefficients, a contribution vector, and optional top-k ranking.
- Local feature ablation remains deferred. Streamed ablation needs one perturbed feature vector and 129 sequential predictions; microbatching trades RAM for fewer calls; a full batch requires 129×128 values and is not assumed feasible.
- Sensor views may aggregate eight already-validated feature attributions per physical sensor as `DERIVED_SENSOR_GROUP_VIEW`. A grouped perturbation algorithm would be a new scientific method and needs a later experiment.
- Host-only or no-on-device XAI remains valid when prediction export is plausible but explanation deployment is not.

## Deferred paths

ONNX is validation-only, not an nRF52840 runtime. CMSIS-DSP is optional for later transparent kernels. CMSIS-NN is considered only for the confirmed MLP after direct FP32 equivalence. TFLite Micro and external runtimes remain deferred until versions, licenses, operator support, runtime overhead, and target compatibility are frozen.

