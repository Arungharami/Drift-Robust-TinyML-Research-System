# Stage 10 — XAI fidelity execution

Status: `EXECUTED`; scientific outcome: mixed. Experiment: `EXP-XAI-FIDELITY-001`.

All seven Stage 09 CSVs and four frozen model artifacts passed SHA-256 verification. No model or preprocessing object was fitted. The perturbation reference was each saved pipeline's Batch-1 `StandardScaler.mean_`.

The experiment produced 270 global feature-deletion rows, 1,096 local rows, 162 sensor-group rows, 216 feature-family rows, 45,840 matched random controls, and 688 bootstrap intervals. Averaged across batch and K, selected-minus-random macro-F1 damage was 0.037/0.041 for MODEL-C1 coefficient/permutation, 0.178/0.105 for MODEL-C2 impurity/permutation, 0.028 for MODEL-C3 permutation, and 0.063 for MODEL-C4 permutation. These averages do not imply every batch/K interval was positive.

Local selected-minus-random target-score reduction averaged 0.141 for MODEL-C1 coefficient importance. Cumulative ablation consistency averaged 0.127, 0.085, 0.061, and 0.108 for MODEL-C1..C4. Because single-feature ablation generated the ranking, those latter results are consistency evidence, not independent fidelity validation.

Sensor-group evidence was strongest on average for MODEL-C2 (0.205 impurity; 0.142 permutation selected-minus-random macro-F1 damage) and weak/mixed for MODEL-C1 and MODEL-C3. MODEL-C3 permutation sensor groups averaged -0.001, a negative result. Correct-representative samples had larger average local selected-minus-random score change (0.165) than misclassified (0.067) or near-boundary samples (0.046); overlapping misclassified/near-boundary samples averaged -0.145, but only 16 rows support that estimate.

No universal fidelity claim is supported. Results vary by model, method, batch, K, scope, and error condition. Feature replacement can create correlated-sensor states that are not physically realizable. The experiment establishes model dependence under controlled perturbation, not chemical causality, human interpretability, or model correctness.
