# TinyML candidate-development protocol

Status: `PLANNED`; physical resource fields remain `BLOCKED` until measured.

The first candidates are the frozen logistic-regression and small-MLP artifacts already produced by Stage 05. Selection precedes any new training. For each saved pipeline, extract estimator structure, tensor shapes, parameter counts, raw FP32 parameter bytes, and prospective INT8 parameter bytes. These are `DERIVED`, never Flash or SRAM.

An export experiment must freeze preprocessing, class ordering, numerical tolerances, representative calibration data drawn only from allowed historical batches, compiler/toolchain, and golden host-vs-embedded vectors. INT8 PTQ is evaluated first. QAT is permitted only after a predefined meaningful degradation threshold is exceeded. Physical Flash, static RAM, peak SRAM, latency, and energy require firmware/build/map files or device traces and may not be populated from Python serialization or host timing.

Explicit initial budgets: model parameters <= 50,000; compiled Flash <= 512 KiB; peak SRAM <= 128 KiB. These are design constraints, not measurements.
