# Stage 10 XAI fidelity protocol — frozen before execution

Experiment: `EXP-XAI-FIDELITY-001`. Source: frozen `EXP-XAI-0001` explanations and `BASE-FIXED-C1-001..C4-001` pipelines. Models are never retrained and preprocessing is never refitted.

Global fidelity tests whether deleting top-ranked features, sensors, or feature families damages macro-F1, balanced accuracy, and prediction agreement more than matched random or bottom-ranked deletion. Local fidelity separately tests necessity (target-score reduction) and sufficiency (target-score retention) on the exact Stage 09 samples. Local single-feature ablation is evaluated only as cumulative multi-feature `ABLATION_CONSISTENCY`, because an identical one-feature test would be circular.

All replacements use the saved `StandardScaler.mean_`, fitted on Batch 1. Thus the raw training mean maps to the existing transformed zero baseline without consulting Batches 2–10. Random controls use 30 deterministic repetitions (seed 42). Confidence intervals use 1,000 bootstrap replicates (seed 1042). Global matched-control repetitions and local samples are the resampling units; features within a sample are not independent units.

Feature K is 1, 3, 5, 10, 20 globally and 1, 3, 5, 10 locally. Sensor K is 1, 2, 3. Results stay separated by model, method, batch, K, perturbation, and local category. No universal fidelity score is defined.

Perturbed inputs may not be chemically realizable because correlated sensor features are independently replaced. Distances diagnose model-input displacement, not chemical causality. Fidelity here means dependence of the frozen model on ranked inputs; it does not mean human interpretability, causal truth, chemical causality, or accuracy.
