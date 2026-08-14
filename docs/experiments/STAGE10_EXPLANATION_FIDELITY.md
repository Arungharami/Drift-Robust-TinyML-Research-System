# Stage 10 — Explanation fidelity

## Status

Protocol and executable runner are implemented. This document does not claim an outcome. Stage 10 becomes executed only when the dataset-backed workflow produces the per-sample table, aggregate table, provenance environment, and manifest.

## Research question

How much of each frozen model's full-input behavior is retained by the Stage 09 top-k local explanation, relative to the complete single-feature-ablation ranking?

## Frozen inputs

- Source explanation experiment: EXP-XAI-0001.
- Models: the four fitted FIXED_ORIGIN artifacts from Stage 05; no retraining.
- Samples: the Stage 09 local samples from chronological batches 2, 6, and 10.
- Candidate ranking: Stage 09 candidate_features.
- Reference ranking: Stage 09 full single-feature-ablation reference_features.
- Feature-removal baseline: the feature-wise mean of training batch 1 only.
- Values of k: 1, 3, 5, and 10.

The input and model file hashes are recorded in the Stage 10 manifest.

## Behavioral tests

For each model, sample, and k, the runner creates two perturbations for both candidate and reference features:

1. Keep-only: begin with the training baseline and restore the selected features.
2. Delete-selected: begin with the sample and replace the selected features with the training baseline.

Probabilities are measured for the class predicted on the unmodified sample. The outputs report:

- rank overlap at k;
- keep-only prediction preservation;
- keep-only target-probability closeness;
- absolute sufficiency gap;
- comprehensiveness drop;
- candidate-minus-reference differences.

Raw signed sufficiency and comprehensiveness values are retained in the per-sample artifact. Negative values are possible and must not be silently clipped.

## Interpretation boundary

This protocol preregisters no pass/fail threshold. Results are descriptive. A high rank overlap does not by itself prove behavioral fidelity, and identical candidate/reference rankings for a model should be described as identity with the reference rather than independent corroboration.

Stage 10 measures host-side model behavior. It does not establish embedded feasibility, on-device latency, memory use, or energy consumption.

## Execute

    python scripts/download_dataset.py
    python -m src.xai.run_stage10 --config configs/xai/stage10_fidelity_v1.yaml

Expected evidence:

- results/xai/stage10_fidelity_per_sample.csv
- results/xai/stage10_fidelity_summary.csv
- artifacts/explanations/EXP-FID-0001/config.yaml
- artifacts/explanations/EXP-FID-0001/environment.json
- artifacts/explanations/EXP-FID-0001/manifest.json
- artifacts/explanations/EXP-FID-0001/run.log

The dedicated GitHub Actions workflow runs the same commands, validates the expected 880 per-sample rows and 16 aggregate rows, uploads a workflow artifact, and commits only these named evidence files back to its research branch.
