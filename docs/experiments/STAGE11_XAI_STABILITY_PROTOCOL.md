# Stage 11 explanation-stability protocol — frozen before execution

`EXP-XAI-STABILITY-001` separates raw explanation change from input change and frozen-model output change. It defines no universal stability score.

Only Stage 09 permutation importance has chronological global vectors for Batches 2–10. Intrinsic coefficient and impurity vectors marked `ALL` are not silently replicated across batches and are `NOT_APPLICABLE` to global chronological analysis. Local coefficient and ablation-contribution vectors support rank, magnitude, and signed comparisons.

Global comparisons are adjacent B2↔B3 through B9↔B10 and anchor-to-future B2↔B3 through B2↔B10. Metrics are full-vector Spearman, Kendall tau-b, Jaccard@5/10/20, cosine similarity, and L1 distance after per-vector absolute-L1 normalization. Sensor aggregation sums absolute importance across each sensor's eight features; family aggregation uses the frozen ontology.

Input change is the absolute difference in the already-validated Batch-1-referenced normalized-Wasserstein trajectory. It is not a direct pairwise Wasserstein distance. Model change includes absolute macro-F1 change and L1 distance between mean class-probability vectors. Relative ratios retain numerator and denominator and are reported at epsilons 1e-8, 1e-6, and 1e-4.

Within-context local robustness uses up to three naturally observed frozen Stage 09 audit samples with the same model, batch, true class, and predicted class, nearest in saved Batch-1-standardized space. Cross-batch analysis uses one-to-one Hungarian matching within true class for B2↔B6, B6↔B10, and B2↔B10. It is cross-sectional, not longitudinal, and concentration is not controlled because trustworthy metadata is unavailable.

Bootstrap intervals use 1,000 deterministic replicates, seed 1142. Statistical units are chronological batch pairs or natural-neighbor/matched sample pairs, never the 128 features within one vector. Candidate-claim thresholds are frozen in `configs/xai_stability_protocol.yaml`.
