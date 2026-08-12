# Stage 14R C1 FP32 preprocessing-repair protocol — frozen before execution

`EXP-EMBED-C1-PREPROC-REPAIR-001` investigates whether a prospectively defined, explicit, all-FP32 representation of the immutable MODEL-C1 StandardScaler can meet every already-frozen Stage-13/14 criterion. Historical experiment `EXP-EMBED-FP32-EQUIV-001 = FAILED` remains unchanged. C4 is not modified or tested.

The five candidates are evaluated in fixed order: P0 baseline division; P1 multiplication by an FP32 reciprocal derived from the float64 reference scale; P2 FP32 affine constants `a=1/scale`, `b=-mean/scale`; P3 a two-term FP32 mean with `delta=(x-mean_hi)-mean_lo` followed by division; and preregistered P4 with two-term mean and reciprocal, `z=delta*inv_hi + delta*inv_lo`. P4 uses no FMA. Every stored constant and runtime operation is FP32.

The primary compiler is Zig 0.16.0 C11 on the x86-64 Windows host with `-O2 -fno-fast-math -ffp-contract=off`. Input and output are FP32. FP64 is used only offline for frozen references, deterministic constant derivation, and error analysis.

Every candidate is evaluated against all C1 golden vectors and all six applicable C1 boundary vectors. No small-magnitude row is excluded. Frozen requirements remain: preprocessing maximum absolute error ≤`2e-5` and relative error ≤`2e-6` for every row; score error ≤`1e-4`; probability error ≤`1e-5`; normalization error ≤`2e-6`; and 100% golden/boundary class agreement. Local contribution requirements remain `2e-4` absolute, `2e-5` relative, sign preservation outside the frozen zero region, and exact top-k sets for K 1/3/5/10/20.

Candidate selection is lexicographic. A candidate is eligible only after every mandatory prediction and XAI rule passes. Among eligible candidates, choose lowest representation-complexity rank, then constant bytes, runtime operations, then fixed candidate order. Numerical error magnitude cannot displace a simpler passing candidate. If none passes, report `STRICT_FP32_EXPLICIT_STANDARDIZATION_REPAIR_NOT_DEMONSTRATED` and propose—but do not execute—a separately frozen fused preprocessing/inference experiment.

Diagnostics decompose raw-input casting, mean casting, scale casting, subtraction, division/reciprocal interaction, FP32 ULP error, cancellation ratio, and reference-magnitude bins. They explain failures but never alter pass/fail rows.
