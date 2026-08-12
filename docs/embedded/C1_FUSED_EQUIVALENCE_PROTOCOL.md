# Prospective C1 fused FP32 equivalence protocol

Future experiment `EXP-EMBED-C1-FUSED-EQUIV-001` is authorized only after this gate freezes. This document contains no fused performance result.

F0 is the sole candidate: float64 offline derivation → one float32 cast per final constant → float32 raw input → float32 ascending-order accumulation → stable float32 softmax. Reference A is the immutable float64 scientific pipeline. Reference B passes float32-cast raw values through the scientific pipeline only to diagnose raw-input sensitivity and may never replace Reference A.

The future test has five levels: parameter-derivation integrity; raw-input score equivalence; probability equivalence; decision equivalence; and boundary-stress equivalence. Explicit standardized-feature equivalence is intentionally absent because the architecture does not construct standardized features.

The prospective primary score limit is maximum absolute error `2e-3`. Before fused outputs existed, the frozen golden-input/parameter magnitudes gave a conservative FP32 error budget of `1.588e-3`: the standard `γ129` sequential-accumulation bound plus float32 raw-input, fused-weight, and fused-bias casting terms. The threshold is rounded upward to accommodate the bound while remaining strict enough to expose indexing, class-order, or formula errors. Score relative error is diagnostic only for `|reference score|≥1e-3` and uses a `1e-3` denominator floor.

Probability requirements are maximum component error `1e-3`, vector L1 distance `4e-3`, normalization error `2e-6`, exact class order, and stable maximum-subtracted softmax. Golden and all applicable boundary predictions require 100% agreement. One flip fails. Boundary records retain top and second scores, margins, errors, and predictions individually.

The compiler must use C11, feature order 0→127, `-O2`, `-fno-fast-math`, and `-ffp-contract=off`. No post-hoc numeric variant search is allowed. Failures use the fused-specific taxonomy, never `PREPROCESSING_MISMATCH`.

Inference is tested first. Fused XAI remains a separate future experiment whose contribution must preserve centering and intercept/baseline semantics.
