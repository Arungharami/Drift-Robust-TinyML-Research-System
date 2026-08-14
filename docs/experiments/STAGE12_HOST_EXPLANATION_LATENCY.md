# Stage 12 — Host-side explanation latency

**Status: EXECUTED.** Experiment `EXP-LAT-0001`; execution commit
`fca7eef8424991d9ce8a8aa75400d824b619d591`.

## Protocol

The run used 12 deterministic Stage 09 samples per model, two unmeasured warmups, and five
measured repetitions. It timed single-input prediction and vectorized single-feature ablation
for all models, plus intrinsic coefficient explanation for MODEL-C1. Every duration was recorded
with `perf_counter_ns` on a captured shared GitHub-hosted Ubuntu runner.

## Results

| Model | Method | n | Median ms | p95 ms |
|---|---|---:|---:|---:|
| MODEL-C1 | prediction | 60 | 0.352 | 0.418 |
| MODEL-C1 | intrinsic coefficient | 60 | 0.539 | 0.552 |
| MODEL-C1 | local ablation | 60 | 0.834 | 0.870 |
| MODEL-C2 | prediction | 60 | 34.553 | 35.354 |
| MODEL-C2 | local ablation | 60 | 81.815 | 90.502 |
| MODEL-C3 | prediction | 60 | 0.383 | 0.455 |
| MODEL-C3 | local ablation | 60 | 2.263 | 2.559 |
| MODEL-C4 | prediction | 60 | 0.475 | 0.504 |
| MODEL-C4 | local ablation | 60 | 1.166 | 1.206 |

The manifest validates 540 raw rows and nine summaries. Output SHA-256 values are
`0b5bc60290b22ef553dd0c482201dac8a2dce76067c8ad1c9b55c061d3404ac3` (raw) and
`4f8bb75ff5f8c19136b142c3b67afaa3911f1eb73289ae1c417bef2ac37424e6` (summary).

## Boundary

These values are host-side comparative evidence from one shared runner. They are not nRF52840
latency, real-time guarantees, or embedded-feasibility evidence. Stage 17 physical inference
latency remains `NOT_EXECUTED`.

## Artifacts

- `results/xai/stage12_host_latency_raw.csv`
- `results/xai/stage12_host_latency_summary.csv`
- `artifacts/explanations/EXP-LAT-0001/manifest.json`
