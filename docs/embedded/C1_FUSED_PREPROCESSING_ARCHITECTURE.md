# C1 fused preprocessing/linear-inference architecture

Gate `GATE-C1-FUSED-PREPROC-001` defines—but does not execute—a raw-input affine representation of the frozen MODEL-C1 pipeline. Historical Stage-14 and Stage-14R explicit-preprocessing failures remain failed and immutable.

The confirmed reference has 128 inputs, six classes ordered `[1,2,3,4,5,6]`, scaler mean/scale shapes `(128,)`, coefficient shape `(6,128)`, and intercept shape `(6,)`. Its scientific equations are `z_i=(x_i-mean_i)/scale_i`, `score_c=intercept_c+Σ coefficient[c,i]z_i`, multinomial stable softmax, and `classes_[argmax(score)]`.

Algebraic substitution defines `w_raw[c,i]=coefficient[c,i]/scale_i` and `b_raw[c]=intercept[c]-Σ coefficient[c,i]mean_i/scale_i`, giving `score_raw_c=b_raw[c]+Σw_raw[c,i]x_i`. This changes deployment representation without changing the real-arithmetic classifier. It removes explicit `z` materialization and therefore has no explicit transformed-feature equivalence level. That distinction is architectural, not a relaxed or retroactive Stage-14 rule.

Future F0 constants are derived entirely offline in float64 from frozen artifacts, then each final fused constant is cast once to float32. Generated C will contain only float32 constants and use float32 raw input, ascending feature accumulation, stable float32 softmax, `-fno-fast-math`, and `-ffp-contract=off`. No fused source or output exists at this gate.

For prediction, runtime scaler constants and the 128-element transformed buffer are analytically eliminated. For future local XAI, the scaler mean remains relevant because the Stage-09 baseline-preserving contribution is `w_raw[c,i](x_i-mean_i)`, not `w_raw[c,i]x_i`. Centering moves into fused prediction bias but must not disappear from explanation semantics.

The dependency order is inference first without XAI. A valid fused inference does not establish fused local-XAI equivalence; that requires its own prospective claim and experiment.

