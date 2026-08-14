# Stage 13 — embedded architecture and export protocol freeze

`GATE-EMBED-EXPORT-001` is a protocol/architecture gate, not a performance experiment. No model conversion, generated production code, ONNX, TFLite, quantization, CMSIS implementation, firmware build, MCU execution, memory measurement, latency measurement, or energy measurement occurred.

## Confirmed frozen inventory

| Model | Frozen estimator | Confirmed structure | Analytical initial path |
|---|---|---|---|
| C1 | `LogisticRegression` | 6×128 coefficients + 6 biases; 768 MACs | manual static FP32 parameters |
| C2 | `RandomForestClassifier` | 200 trees; 10,230 nodes; depth 6–11, mean 7.87 | static/generated tree traversal |
| C3 | RBF `SVC` | 131 support vectors × 128; 15 pairwise intercepts | generated/custom RBF comparator |
| C4 | `MLPClassifier` | 128–64–32–6 ReLU; 10,432 weights + 102 biases | direct static dense FP32 |

Every model is a frozen `StandardScaler → estimator` pipeline using the same 128-feature ordering and original class labels 1–6. Stored means, scales, variances, feature-order hashes, and constant hashes are recorded. MCU refitting and future-batch recalculation are forbidden.

## Analytical complexity and storage

Raw scalar-equivalent FP32 parameter storage is 3,096 bytes (C1), 409,200 bytes (C2), 69,872 bytes (C3), and 42,136 bytes (C4), plus 1,024 bytes for mean and scale. These are `DERIVED_ANALYTICAL`, not compiled Flash or SRAM. C2's count is a neutral structural-equivalent accounting and actual tree code/metadata may differ substantially.

The nRF52840 physical capacity is 1 MiB Flash and 256 KiB RAM. That is not the application budget. The provisional policy reserves at least 20% safety margin until firmware, stack, heap, buffers, logging, instrumentation, map-file, and peak-memory evidence exist. All category allocations remain `TBD_BEFORE_COMPILE`.

## Future toolchain and measurements

The proposed target is nRF52840/Cortex-M4F at 64 MHz. Exact board, Nordic SDK, compiler, build system, optimization, FPU flags, language standard, CMSIS/TFLM versions, runtime, and logging transport must be frozen before export/compile; they are not experimentally validated.

A later compile protocol must retain `.text`, read-only constants, initialized data, BSS, stack, heap, temporary buffers, and peak memory separately using linker map parsing plus runtime high-water instrumentation. Pickle size and analytical bytes may never be labeled Flash.

A later MCU timing protocol must separately trigger and retain preprocessing, inference, explanation, top-k, and total pipeline measurements with raw logs, median, p95, and N. Energy instrumentation must expose IDLE, PREPROCESSING, INFERENCE, EXPLANATION, and POSTPROCESSING trigger regions for later PPK2 segmentation. No host timing is copied into these future tables.

## Frozen outputs and states

All required inventories, path matrices, candidate tiers, analytical counts, preprocessing specification, golden vectors, boundary vectors, numerical criteria, resource policy, and one gate decision are saved under `results/embedded`, `data/manifests`, `configs`, `embedded`, and `docs/embedded`.

- Stage-13 protocol: `FROZEN`
- Model export: `NOT_EXECUTED`
- Quantization: `NOT_EXECUTED`
- Firmware: `NOT_EXECUTED`
- Compiled Flash/SRAM: `NOT_MEASURED`
- MCU latency: `NOT_MEASURED`
- PPK2 energy: `NOT_MEASURED`

The next scientific decision is `AUTHORIZE_FP32_EXPORT_EQUIVALENCE_TEST` as a new, separately scoped experiment. Lossy precision reduction remains unauthorized until FP32/reference equivalence is established.
