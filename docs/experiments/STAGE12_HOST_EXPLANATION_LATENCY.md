# Stage 12 — Host-side explanation latency

## Status

Protocol and runner implemented; no timing result is claimed until the workflow executes.

## Scope

Stage 12 benchmarks single-input prediction, vectorized single-feature local ablation for all
four frozen models, and intrinsic coefficient explanation for MODEL-C1. It uses 12 deterministic
Stage 09 samples per model, two unmeasured warmups, and five measured repetitions.

The raw table records every `perf_counter_ns` duration. The summary reports mean, standard
deviation, median, p95, minimum, and maximum latency.

## Boundary

These measurements run on a shared GitHub-hosted Ubuntu runner whose environment is captured in
the manifest. They are host-side comparative evidence only. They are not nRF52840 timing,
real-time guarantees, or evidence of embedded feasibility. Physical latency remains Stage 17.

## Expected artifacts

- `results/xai/stage12_host_latency_raw.csv`
- `results/xai/stage12_host_latency_summary.csv`
- `artifacts/explanations/EXP-LAT-0001/manifest.json`
