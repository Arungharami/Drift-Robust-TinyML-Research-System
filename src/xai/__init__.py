"""Stage 09 — resource-aware explainability.

Explanation methods for the four frozen, evidence-selected FIXED_ORIGIN classical models
(MODEL-C1..C4; see configs/classical_baselines.yaml and artifacts/models/). Nothing here
retrains a model or modifies the chronological split. This stage prepares explanation
artifacts for Stage 10 (fidelity) and Stage 11 (stability) — it does not itself report
fidelity or stability conclusions.
"""
