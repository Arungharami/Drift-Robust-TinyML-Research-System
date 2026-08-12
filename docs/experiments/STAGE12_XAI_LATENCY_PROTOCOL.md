# Stage 12 host computational-cost protocol — frozen before timing

`EXP-XAI-LATENCY-001` measures controlled host-side computational cost. It does not measure or estimate nRF52840 latency, physical energy, Flash, SRAM, or battery life.

Protocol amendment: v1 exceeded the 10-minute process ceiling during permutation warm-up before any raw timing artifact existed. No result was observed. Before restarting, v2 froze a deterministic stratified 256-sample subset per batch for permutation timing; batches, repeat counts, seeds, methods, and every other boundary remain unchanged. Total permutation runtime and actual evaluated sample count remain mandatory.

The primary environment is Windows/Python 3.11.9 on an 8-core/16-thread Intel x86-64 host with approximately 16.996 GB RAM. OMP, MKL, OpenBLAS, and BLIS thread variables are fixed to one; `threadpoolctl` limits and inspects effective native threadpools; sklearn `n_jobs` is one.

Timing uses `time.perf_counter_ns()` and `time.process_time_ns()`. Model loading, preprocessing, baseline inference, explanation computation, top-K reduction, and serialization are separate phases. First-call diagnostics and warm-up are separate from steady-state measurements. No timing observation is removed.

Steady-state inference/local operations use 30 repeats after five warm-ups. Intrinsic extraction and reduction use 100 repeats after ten warm-ups. Dataset-level permutation importance uses three measured runs after one warm-up, five feature permutations per run, the frozen macro-F1 scorer, and `n_jobs=1`. The vectorized ablation implementation is measured on every frozen Stage 09 local sample. A naïve 128-call reference is measured five times on the first lexicographic frozen sample per model and batch, selected before timing.

Global and local methods remain separate. Static intrinsic vectors are one-time extraction candidates; permutation importance is a labeled-dataset procedure; coefficient contributions are online arithmetic plus model context; ablation requires baseline plus 128 perturbed evaluations. Sensor-group cost is analytical-only because no frozen grouped explainer exists.

Bootstrap intervals use 1,000 timing-replicate resamples, seed 1242. Raw nanoseconds are authoritative. Median and p95 are primary; IQR, mean, standard deviation, coefficient of variation, minimum, maximum, and N are retained. The complete acceptance criteria and schemas are frozen in `configs/xai_latency_protocol.yaml`.
