# C1 fused local-XAI equivalence protocol

`EXP-EMBED-C1-FUSED-XAI-EQUIV-001` evaluates all 54 frozen MODEL-C1 Stage-09 local audit samples. Stage 09 explains the frozen predicted class with 128 signed values `coef[c,i] * standardized_x[i]`; ranking is descending absolute magnitude with ascending feature index as the deterministic tie break. The intercept is not emitted as a feature attribution.

The equivalent raw-domain FP32 expression is `w_raw[c,i] * (x_i - mean_i)`. It preserves Stage-09 centering; `w_raw*x` is forbidden. Explanation additivity uses the original class intercept, while fused prediction uses the algebraically shifted fused bias.

The prospective universal limits are attribution maximum absolute error `2e-5`, vector L1 error `5e-4`, and additivity error `2e-4`. Sign must agree for every reference attribution with magnitude at least `1e-6`. Top-K sets must agree exactly for K 1, 3, 5, 10, and 20. All near-zero rows are retained; raw and `1e-5`-floored relative errors are diagnostic only.

Runtime arithmetic and constants are float32. C11 host compilation uses `-O2 -fno-fast-math -ffp-contract=off`. Fused inference lineage is checked but prediction portability is not re-evaluated. No XAI repair search, quantization, MCU work, or hardware measurement is authorized.
