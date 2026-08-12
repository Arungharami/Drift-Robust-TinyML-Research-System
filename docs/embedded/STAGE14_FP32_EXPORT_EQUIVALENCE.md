# Stage 14 — FP32 embedded-style export equivalence results

`EXP-EMBED-FP32-EQUIV-001` completed with scientific outcome **FAILED**: both C1 and C4 failed at least one mandatory frozen preprocessing criterion. The result was not repaired by changing tolerances.

## What executed

Deterministic generators created standalone C11 FP32 constants and inference code for C1 and C4. Zig 0.16.0's bundled Clang-compatible compiler built host x86-64 executables at primary `-O2 -std=c11 -fno-fast-math` and secondary `-O0`. Both optimization levels produced byte-identical CSV outputs. Repeated primary execution was also byte-identical.

No scikit-learn/Python runtime is embedded in the C implementations. C1 contains frozen scaler values, 6×128 coefficients, six intercepts, class labels, affine scores, stable softmax, and Stage-09 local coefficient contributions. C4 contains frozen scaler values, matrices in confirmed `(input, output)` C-order shapes `(128,64)`, `(64,32)`, `(32,6)`, biases, ReLU, and confirmed softmax output activation.

## Mandatory results

| Candidate | Preprocessing max abs | Preprocessing max rel | Score max abs | Probability max abs | Golden decisions | Boundary decisions | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| C1 | 7.995e-6 | 2.744e-3 | 8.315e-5 | 1.510e-6 | 100% | 100% | FAIL |
| C4 | 4.845e-4 | 1.392e-5 | 3.596e-7 | 3.596e-7 | 100% | 100% | FAIL |

C1 passed the `2e-5` preprocessing absolute limit but failed the `2e-6` relative limit on 41 of 3,712 feature comparisons, principally near zero. C4 failed the `2e-5` absolute preprocessing limit and relative criterion on 27 of 3,712 comparisons; the maximum absolute deviation occurred where transformed magnitudes amplify FP32 casting of large scaler constants. Scores, probabilities, normalization, golden decisions, and all 24 boundary decisions passed for both candidates.

The failure taxonomy is `PREPROCESSING_MISMATCH`. It is not a parameter-orientation, activation, softmax, decision, nondeterminism, or build failure.

## C1 local XAI

C1 attribution maximum absolute error was `1.651e-6`, every sign agreed, and top-k sets matched exactly for K `{1,3,5,10,20}`. Nevertheless, seven of 3,712 feature rows exceeded the frozen `2e-5` relative limit near zero. Therefore `C-EMBED-FP32-XAI-01` is **UNSUPPORTED** under the preregistered conjunctive rule.

## FP64 to FP32 conversion

Scaler means and scales had maximum absolute cast errors of `3.884e-3` and `3.946e-3`, with relative errors below `5.64e-8`. Model-array cast errors were much smaller: C1 coefficient error at most `4.473e-8`; C4 weights at most `1.455e-8`. All source/export array hashes and shapes are retained.

## Derived storage and buffers

Export-derived constants are 4,120 bytes for C1 and 43,160 bytes for C4. Minimal derived working-buffer requirements are 1,072 bytes for C1 and 1,304 bytes for C4. These are `DERIVED_FROM_EXPORT` and `DERIVED_WORKING_BUFFER_REQUIREMENT`, not measured MCU Flash or SRAM.

## Interpretation and next decision

The transparent FP32 model arithmetic is numerically strong enough to retain all observed decisions, including boundary cases, but the frozen Stage-13 preprocessing tolerances reject both candidates. The correct next decision is **REPAIR C1 EXPORT** and **REPAIR C4 EXPORT** through a separately preregistered preprocessing-arithmetic investigation—not by retroactively loosening criteria. Quantization remains unauthorized.

Compiled MCU Flash, SRAM, MCU latency, explanation latency, and energy remain `NOT_MEASURED`.
