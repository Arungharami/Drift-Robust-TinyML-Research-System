# Stage 11 — Chronological explanation stability

**Status: EXECUTED.** Experiment ID `EXP-STAB-0001` (registry rows
`EXP-STAB-0001-C1..C4`). Execution commit `d571b4301819db27fce1eba9485edac0eb58645d`.

## Research question

How stable are each frozen model's global permutation-importance explanations as the evaluation
data advances from chronological batch 2 through batch 10?

## Frozen scope and provenance

- Source: `EXP-XAI-0001`, `results/xai/stage09_global_importance.csv`.
- Input SHA-256: `aada90323871291056bc7e73fe98ce65be935cde8eb12e995d63da7c1c39dcf5`.
- Dataset hash: `dc9dbcfc4c8eedceae4418d8f2096605ccb2b3bd554a3134f84c46d22b0615e6`.
- Split: FIXED_ORIGIN, hash `5f3ceed0e1c14ff404d9167517b124493d2df882f179fa953c67d5483246a8ae`.
- Config hash: `f9b02fc305dfd41b275a06df079212ed8b1abfa02944d9851fd521e00d0b26a0`.
- Comparable method: `PERMUTATION_IMPORTANCE_MACRO_F1` only.
- Models: MODEL-C1 through MODEL-C4.
- Batches: 2 through 10; all 128 features.
- Comparisons: every batch against batch 2, plus each adjacent batch pair.
- Top-k values: 1, 3, 5, and 10.

Intrinsic rankings use `batch=ALL` and therefore cannot measure chronological change; they were
excluded. Local samples are not longitudinally matched physical observations, so this stage
does not compare local explanations across batches.

## Metrics

- Spearman and Kendall correlation of complete feature ranks.
- Cosine similarity of signed importance vectors.
- Top-k feature-set Jaccard overlap.

The four batch-2 self-comparisons are retained as implementation identity checks but excluded
from aggregate reference statistics.

## Execution evidence

- 68 pairwise rows: 36 batch-2 reference comparisons plus 32 adjacent comparisons.
- 4 aggregate rows: one for each model.
- 128 complete, uniquely ranked features validated for every model/batch.
- Manifest status: `EXECUTED`.
- Output SHA-256:
  - pairwise: `4c7e0d141cb253e157ba1b44286cb93da4b71b6e1de9497c6b5e8287c219b231`
  - summary: `8df1b8fd0aafc46f1fdc43c21a47ee2772b7521e54d6d7c89f68452064b9d7bf`

## Aggregate results

All values are from `results/xai/stage11_stability_summary.csv`; reference comparisons cover
batches 3-10 against batch 2.

| Model | Mean Spearman vs B2 | Minimum vs B2 | Mean adjacent Spearman | Mean cosine vs B2 | Mean top-10 Jaccard vs B2 | Top-1 Jaccard vs B2 |
|---|---:|---:|---:|---:|---:|---:|
| MODEL-C1 | 0.322 | -0.316 | 0.421 | 0.173 | 0.101 | 0.000 |
| MODEL-C2 | 0.101 | -0.225 | 0.106 | 0.101 | 0.135 | 0.000 |
| MODEL-C3 | 0.027 | -0.542 | 0.178 | 0.112 | 0.132 | 0.000 |
| MODEL-C4 | 0.051 | -0.241 | 0.075 | 0.136 | 0.092 | 0.000 |

Across all four models, none of batches 3-10 retained the same top-ranked permutation-importance
feature as batch 2. Mean full-rank Spearman correlation to batch 2 ranged from 0.027 to 0.322,
and each model had at least one negative correlation. Adjacent comparisons were higher for
MODEL-C1 and MODEL-C3 but remained modest. These are dataset- and protocol-specific
observations, not universal claims.

## Interpretation boundary

No pass/fail threshold was preregistered, so the experiment does not declare a model
"sufficiently stable" or "unstable for deployment." Permutation importance is itself sensitive
to the evaluation distribution and to correlated features. The results describe global
ranking variation, not local longitudinal explanation stability.

This stage does not measure explanation latency, memory, or energy.

## Artifacts

- `results/xai/stage11_stability_pairwise.csv`
- `results/xai/stage11_stability_summary.csv`
- `artifacts/explanations/EXP-STAB-0001/config.yaml`
- `artifacts/explanations/EXP-STAB-0001/environment.json`
- `artifacts/explanations/EXP-STAB-0001/manifest.json`
- `artifacts/explanations/EXP-STAB-0001/run.log`

## Next experiment

Stage 12 — host-side explanation latency. Physical/on-device timing remains blocked until
embedded export and deployment are completed.
