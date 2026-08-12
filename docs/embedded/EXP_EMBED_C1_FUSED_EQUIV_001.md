# EXP-EMBED-C1-FUSED-EQUIV-001

This experiment evaluates the prospectively frozen `C1-FUSED-F0` raw-input FP32 affine representation. It does not repair or reinterpret the failed Stage 14 or Stage 14R explicit-preprocessing experiments.

The scientific reference is the frozen float64 `StandardScaler` followed by frozen float64 `MODEL-C1`. Fused weights and biases are derived in float64, cast once to float32, and evaluated from float32-cast raw inputs using 128 sequential float32 multiply-accumulate steps per class and stable float32 softmax.

Before result generation, the maximum score-error threshold was frozen at `2e-3`. The bound accommodates raw-input rounding, final fused-constant rounding, and the standard 129-term sequential FP32 accumulation bound; it was rounded upward from the prospective analytical budget of `1.588e-3`. It remains small enough to distinguish the intended representation error from indexing, class-order, algebra, or implementation defects.

The maximum component probability-error threshold was independently frozen at `1e-3`, together with vector L1 `4e-3` and normalization `2e-6`. Softmax can amplify score perturbations near close decision boundaries, so probability and exact golden/boundary decisions are evaluated separately. These limits were fixed without observing fused outputs.

Execution is host-only C11 with `-O2 -fno-fast-math -ffp-contract=off` and accumulation order 0 through 127. No fused XAI, quantization, MCU compilation, hardware execution, training, or alternate implementation search is in scope.

## Result

The executed experiment passed. Across 29 golden vectors, maximum score error was `4.853313e-05`, maximum component probability error was `9.249905e-07`, maximum probability-vector L1 error was `1.783851e-06`, and maximum normalization error was `8.792948e-08`; prediction agreement was 100%. Across six boundary-stress vectors, maximum score error was `3.682905e-06`, maximum component probability error was `4.580721e-07`, and prediction agreement was 100%. Float64 algebraic fusion agreed with the reference pipeline to `2.273737e-13` maximum absolute score error.

This supports `C-EMBED-C1-FUSED-01` and `C-EMBED-C1-FUSED-02`. `C-EMBED-C1-FUSED-XAI-01` remains `NOT_EXECUTED`.
