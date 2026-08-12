# EXP-EMBED-C1-FUSED-XAI-EQUIV-001

This host-only experiment evaluates whether `C1-FUSED-F0` reproduces the frozen Stage-09 MODEL-C1 local intrinsic-coefficient explanation. It covers every eligible Stage-09 audit sample and retains all 128 signed feature contributions, including near-zero values.

The frozen raw-domain formula is `w_raw[c,i] * (x_i - mean_i)`, where `c` is the frozen Stage-09 predicted class. Feature ranking uses descending absolute contribution and ascending feature index for ties. Explanation reconstruction adds the original class intercept; fused prediction separately uses the fused bias.

The protocol, tolerances, semantic rules, and host floating-point environment are defined in `configs/c1_fused_xai_equivalence.yaml` and `docs/embedded/C1_FUSED_XAI_EQUIVALENCE_PROTOCOL.md`. No quantization, MCU work, hardware measurement, or XAI repair variant is part of this experiment.

## Result

The experiment passed all mandatory criteria across 54 explanations and 6,912 retained feature attributions. Maximum attribution error was `3.305164e-07`; maximum vector L1 error was `5.205205e-06`; all scientifically non-negligible signs agreed; and every ordered Top-K result agreed for K 1, 3, 5, 10, and 20. Maximum explanation-to-fused-score additivity error was `1.52e-05`. Claim `C-EMBED-C1-FUSED-XAI-01` is supported for the validated host representation.
