# Stage 14R — C1 FP32 explicit-preprocessing repair results

`EXP-EMBED-C1-PREPROC-REPAIR-001` completed with outcome **FAILED**. The Stage-14 C1 baseline failure reproduced exactly: maximum absolute preprocessing error `7.994910077968598e-06`, maximum relative error `0.0027443441751280892`, 41 failed feature rows across 18 samples and 38 features. Historical Stage-14 artifacts remain unchanged.

## Root cause

The 41 baseline failures were dominated by the interaction of FP32 raw-input and mean representation under subtraction. Mean rounding was the largest isolated diagnostic contribution for 24 rows; raw-input rounding was largest for 17. Scale-rounding contributions were at most `2.174e-09` in standardized space and arithmetic-interaction residuals at most `1.152e-09`, much smaller than raw/mean contributions.

For failing rows, median raw cast error was `1.001e-07`, median mean cast error `1.721e-07`, median subtraction error `2.777e-07`, and median standardized absolute error `5.380e-08`. The cancellation indicator had median `0.00912`; ULP error had median 48.36 and maximum 25,856. Failures were not deleted: 23 occurred for `|z|` in `[0.01,0.1)`, 14 in `[0.001,0.01)`, two in `[0.0001,0.001)`, and two below `0.0001`.

## Candidate results

| Candidate | Max abs | Max rel | Failed rows | Samples | Features | Score max abs | Probability max abs | Golden/boundary | XAI failed rows |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 baseline | 7.995e-6 | 2.744e-3 | 41 | 18 | 38 | 8.315e-5 | 1.510e-6 | 100% / 100% | 7 |
| P1 reciprocal | 7.995e-6 | 2.744e-3 | 41 | 18 | 38 | 8.315e-5 | 2.017e-6 | 100% / 100% | 7 |
| P2 affine | 7.995e-6 | 1.558e-2 | 60 | 21 | 49 | 8.315e-5 | 2.017e-6 | 100% / 100% | 9 |
| P3 split mean | 7.995e-6 | 5.453e-4 | 29 | 13 | 26 | 8.315e-5 | 2.017e-6 | 100% / 100% | 5 |
| P4 compensated | 7.995e-6 | 5.452e-4 | 29 | 13 | 26 | 8.315e-5 | 2.017e-6 | 100% / 100% | 5 |

Every candidate passed score, probability, normalization, golden-decision, and six applicable C1 boundary-decision criteria. Every candidate failed the universal preprocessing relative-error requirement. P3/P4 improved but did not repair it; P2 was materially worse. All local-XAI variants retained 100% sign and top-1/3/5/10/20 set agreement, but failed their frozen relative criterion on 5–9 rows.

## Complexity and selection

P0/P1/P2 store 256 FP32 constants (1,024 bytes). P3 stores 384 (1,536 bytes) and uses 384 operations across 128 features. P4 stores 512 (2,048 bytes) and uses 640 operations. These are `DERIVED_COMPUTATIONAL_STRUCTURE`, not MCU measurements.

No candidate was eligible under the frozen rule, so no representation was selected. The formal conclusion is `STRICT_FP32_EXPLICIT_STANDARDIZATION_REPAIR_NOT_DEMONSTRATED`. Claims `C-EMBED-C1-REPAIR-01` and `C-EMBED-C1-REPAIR-XAI-01` remain **UNSUPPORTED**.

## Decision

The next scientific decision is **AUTHORIZE C1 FUSED-PREPROCESSING PROTOCOL**. A future, separately frozen experiment may algebraically fold the scaler into C1's linear coefficients and bias, avoiding explicit standardized-vector materialization. It cannot retroactively satisfy Stage-13 explicit preprocessing equivalence and was not executed here.

C4 remains `FAILED_PREPROCESSING_MISMATCH`. Quantization, Cortex-M compilation, and firmware remain `NOT_EXECUTED`. Compiled MCU Flash, MCU SRAM, MCU latency, MCU explanation latency, and physical energy remain `NOT_MEASURED`.
