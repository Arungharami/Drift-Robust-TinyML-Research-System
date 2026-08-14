# Stage 14 FP32 export-equivalence protocol — frozen before generation

`EXP-EMBED-FP32-EQUIV-001` tests transparent standalone C11 FP32 representations of only MODEL-C1 and MODEL-C4 against the immutable Python/scikit-learn reference. It authorizes host compilation and numerical comparison, not quantization, MCU deployment, physical resource measurement, latency, or energy.

The primary host compiler is Zig 0.16.0's bundled Clang-compatible C driver on x86-64 Windows using `-O2 -std=c11 -fno-fast-math`. `-O0` is a preregistered secondary robustness build. Unsafe fast math is prohibited. Both builds use ordinary float arrays and bundled libc/libm.

C1 performs frozen FP32 standardization, six affine class scores in class order `[1,2,3,4,5,6]`, and maximum-subtracted softmax. C4 performs frozen standardization, dense matrices stored in scikit-learn C-order `(input, output)`, ReLU at 64 and 32 units, six output logits, and confirmed `softmax` output activation.

Mandatory acceptance criteria are copied unchanged from Stage 13: preprocessing errors at most `2e-5` absolute and `2e-6` relative; C1 score/probability errors at most `1e-4`/`1e-5`; C4 at most `2e-4`/`2e-5`; probability normalization error at most `2e-6`; and 100% golden and boundary decision agreement. Deterministic generation and execution, exact lineage, and no upstream changes are also mandatory.

C1 local attribution uses exactly `coefficient[predicted_class, i] × transformed_feature[i]`. Its separately frozen limits are `2e-4` absolute and `2e-5` relative attribution error, no sign reversal outside a `2e-4` reference-zero region, and exact top-k set agreement for K `{1,3,5,10,20}`. C1 prediction export can pass independently, but local XAI cannot be called equivalent unless these criteria pass.

Any single mandatory failure produces candidate `FAIL`; boundary mismatches cannot be averaged away. The scientific outcome is `PASSED_BOTH`, `PARTIAL`, `FAILED`, or `BLOCKED`.
