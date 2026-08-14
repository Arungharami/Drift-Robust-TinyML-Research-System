# Stage 11 — explanation stability under chronological drift

Scientific execution: `EXECUTED`; evidence: mixed and method-specific. Public deployment: `BLOCKED_CREDENTIALS`.

Only permutation importance had chronological global vectors. Across all pair types, mean normalized explanation L1 distance was 0.545, 0.598, 0.468, and 0.568 for MODEL-C1..C4. Adjacent full-rank Spearman was 0.421, 0.093, 0.175, and 0.069; anchor-to-future Spearman was 0.318, 0.101, 0.026, and 0.050. Top-feature overlap was low and K-sensitive.

Sensor rank stability differed substantially: mean sensor Spearman was 0.018, 0.472, 0.128, and 0.166. This matters alongside Stage 10: MODEL-C2 combined stronger sensor fidelity with moderate sensor stability, whereas MODEL-C3's apparent sensor stability is less informative because its Stage-10 sensor fidelity was near null.

Within-context natural neighbors were more similar than cross-batch matches. Mean local explanation distances ranged 0.173–0.281 for natural neighbors and 0.420–0.553 cross-batch. Natural-neighbor Jaccard@10 ranged 0.468–0.597; cross-batch Jaccard@10 ranged 0.152–0.322. The cross-batch analysis is cross-sectional and never represents repeated measurement of one specimen.

Correct representatives had mean local explanation distance 0.244 versus 0.206 for misclassified and 0.225 for near-boundary cases. The correct-minus-misclassified interval crossed zero, so no error-conditioned stability claim is supported. The overlapping error/boundary category contained only nine neighbor-pair rows.

Explanation distance was positively associated with input-trajectory change for MODEL-C4 (Spearman 0.673; 95% bootstrap CI 0.235–0.952), but intervals crossed zero for C1–C3. Fidelity–stability relationships were inconsistent. Local C1 coefficient fidelity correlated positively with instability (0.371; CI 0.074–0.622), while C2 ablation consistency correlated negatively (-0.340; CI -0.543 to -0.088). No general positive fidelity–stability relationship exists in this evidence.

Limitations: Batch-1-referenced drift-trajectory differences are not direct pairwise Wasserstein distances; local audit samples are selected; concentration is unavailable for matching; some constant attribution vectors yield undefined correlations; matching distances are high for some SVM contexts; explanation stability is neither fidelity nor causality.
