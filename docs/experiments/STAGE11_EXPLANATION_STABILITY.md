# Stage 11 — Chronological explanation stability

## Status

Protocol and executable runner are implemented. No outcome is claimed until the repository
workflow generates and validates the Stage 11 evidence artifacts.

## Research question

How stable are each frozen model's global permutation-importance explanations as the evaluation
data advances from chronological batch 2 through batch 10?

## Frozen scope

- Source: Stage 09 global importance rows.
- Comparable method: PERMUTATION_IMPORTANCE_MACRO_F1 only.
- Models: MODEL-C1 through MODEL-C4.
- Batches: 2 through 10.
- Features: all 128.
- Comparisons: every batch against batch 2, plus each adjacent batch pair.
- Top-k values: 1, 3, 5, and 10.

Intrinsic rankings use batch ALL and therefore cannot measure chronological change; they are
intentionally excluded. Local samples are not longitudinally matched physical observations, so
this stage does not compare local explanations across batches.

## Metrics

- Spearman correlation of complete feature ranks.
- Kendall correlation of complete feature ranks.
- Cosine similarity of signed importance vectors.
- Top-k feature-set Jaccard overlap.

The batch-2 self-comparison is retained as an implementation identity check but excluded from
aggregate reference statistics.

## Interpretation boundary

No pass/fail threshold is preregistered. Results are descriptive and do not establish that an
explanation is sufficiently stable for deployment. This stage does not measure explanation
latency, embedded memory, or energy.

## Execute

    python -m src.xai.run_stage11 --config configs/xai/stage11_stability_v1.yaml

Expected outputs:

- results/xai/stage11_stability_pairwise.csv
- results/xai/stage11_stability_summary.csv
- artifacts/explanations/EXP-STAB-0001/manifest.json
