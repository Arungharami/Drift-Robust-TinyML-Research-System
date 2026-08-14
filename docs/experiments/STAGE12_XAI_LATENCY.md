# Stage 12 — controlled host-side XAI computational cost

## Status and scope

`EXP-XAI-LATENCY-001` is **EXECUTED** with a mixed scientific outcome. It measures warm, steady-state computation on one controlled workstation and retains 61,550 raw timing rows. It does **not** measure or estimate nRF52840 latency, physical energy, Flash, SRAM, battery life, or embedded feasibility.

The preregistered v1 permutation workload exceeded the 10-minute process ceiling before producing a raw-results artifact. Before observing a scientific result, protocol v2 froze a deterministic, stratified 256-sample subset per batch while retaining all batches, models, seeds, repeats, timers, and timing boundaries. This amendment is recorded in `configs/xai_latency_protocol.yaml` and the protocol document.

## Integrity and benchmark controls

All 12 required Stage-09–11, model, ontology, and dataset inputs passed SHA-256 verification. The benchmark set `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, and `BLIS_NUM_THREADS` to 1; `threadpoolctl` verified every effective pool at one thread; scikit-learn permutation importance used `n_jobs=1`.

Wall time uses monotonic `time.perf_counter_ns()` and CPU time uses `time.process_time_ns()`. Raw nanoseconds are retained. Model loading, preprocessing, baseline inference, explanation compute, top-k reduction, and serialization are distinct phases. Warm-ups are retained but excluded from primary summaries; no timing outlier was deleted.

## Baseline host inference

Across frozen local contexts B2/B6/B10, mean-of-batch medians were 315.9 µs (MODEL-C1), 11,171.0 µs (MODEL-C2), 342.7 µs (MODEL-C3), and 322.9 µs (MODEL-C4) per single-sample end-to-end host inference. Corresponding mean p95 values were 328.7, 11,931.2, 359.8, and 332.4 µs. Fixed-size batch results retain both total time and a derived per-sample diagnostic.

## Global methods — separate scientific scope

Intrinsic global extraction is a one-time static operation: MODEL-C1 coefficient extraction had a 12.8 µs median and MODEL-C2 impurity extraction 21,772.7 µs. These vectors support precomputation/static storage as an architectural possibility; this is not a firmware decision.

Permutation importance is a labeled dataset procedure, not local explanation latency. For 256 samples, five repeats, 128 features, and 641 prediction/scoring calls, mean-of-batch total medians were 1.322 s (C1), 9.500 s (C2), 3.304 s (C3), and 1.454 s (C4). Total runtime remains the primary quantity. Any normalized per-evaluated-sample value is explicitly secondary and must not be compared as a local explanation.

## Local methods

MODEL-C1 coefficient contribution required one model call and had a 444.1 µs mean-of-batch median. Vectorized single-feature ablation used two calls over 129 evaluated samples and had medians of 709.1 µs (C1), 22,425.9 µs (C2), 2,391.0 µs (C3), and 789.4 µs (C4). The bounded naïve reference used 129 separate calls and had medians of 40.057 ms, 1,402.571 ms, 43.580 ms, and 41.194 ms respectively.

Twelve frozen sample/model/batch checks confirmed vectorized and naïve ablation vectors equivalent within absolute tolerance `1e-12`. Vectorization changes execution, not the explanation definition.

## Hardware-independent accounting

The input has 128 features grouped into 16 physical sensors. Local coefficient contribution produces 128 arithmetic contributions with one prediction call. Vectorized ablation evaluates one baseline plus 128 perturbed samples in two calls; naïve ablation makes 129 calls. Permutation importance makes 641 scoring calls per run and requires a labeled evaluation dataset. The 16-group scenario is `ANALYTICAL_ONLY`; no grouped timing was fabricated.

Top-k reduction for K in {1, 3, 5, 10, 20} was measured separately and was approximately 5 µs median. It primarily reduces representation/output size; it does not remove explanation generation cost.

## Fidelity × stability × cost

`stage12_fidelity_stability_cost.csv` joins continuous evidence without a universal trust score or cross-scope leaderboard. Coverage is not fully matched across methods, especially for Stage-11 stability. The resulting view is explicitly `PRE-HARDWARE`: predictive/fidelity/stability/host-cost evidence exists, while MCU cost remains `NOT_MEASURED`.

## Candidate claims

- `C-XAI-COST-01`: **SUPPORTED** under the frozen ≥2× matched local overhead criterion.
- `C-XAI-COST-02`: **UNRESOLVED**. The 128 additional-call criterion holds for naïve ablation, and model-level timing association is positive, but the preregistered positive bootstrap-CI condition is not established with four models.
- `C-XAI-COST-03`: **SUPPORTED**. Intrinsic global extraction is below permutation p05 total latency for both applicable models.
- `C-XAI-COST-04`: **UNRESOLVED** because fidelity/stability coverage is incomplete for a fully matched dominance test.

## Limitations and decision

Results are machine- and implementation-dependent, collected on one warm host environment. Scheduler variation is retained. The permutation subset is controlled but smaller than the full batches. Host latency is not an estimate of nRF52840 latency or energy.

The evidence supports the decision **PROCEED TO EMBEDDED EXPORT PROTOCOL**: freeze that future protocol before any export. Stage 13, quantization, firmware, compilation, physical latency, memory, and energy remain unexecuted/blocked.

Primary artifacts: `results/xai/stage12_raw_timings.csv`, `stage12_latency_summary.csv`, `stage12_operation_counts.csv`, `stage12_claim_evaluation.csv`, and `stage12_manifest.csv`.
