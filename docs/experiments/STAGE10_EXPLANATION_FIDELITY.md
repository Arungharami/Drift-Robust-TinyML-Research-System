# Stage 10 — Explanation fidelity

**Status: EXECUTED.** Experiment ID `EXP-FID-0001` (registry rows
`EXP-FID-0001-C1..C4`). Execution commit `54ab3e7711324187d99a476ff25958ac9f2e6996`.
The GitHub Actions run downloaded and verified the canonical dataset, executed all four frozen
models, validated the output counts, uploaded the evidence bundle, and committed the named
artifacts.

## Research question

How much of each frozen model's full-input behavior is retained by the Stage 09 top-k local
explanation, relative to the complete single-feature-ablation ranking?

## Frozen inputs

- Source explanation experiment: `EXP-XAI-0001`.
- Models: the four fitted FIXED_ORIGIN artifacts from Stage 05; no retraining.
- Samples: the Stage 09 local samples from chronological batches 2, 6, and 10.
- Candidate ranking: Stage 09 `candidate_features`.
- Reference ranking: Stage 09 full single-feature-ablation `reference_features`.
- Feature-removal baseline: the feature-wise mean of training batch 1 only.
- Values of k: 1, 3, 5, and 10.
- Seed: 42.
- Config hash: `c39882f58b574027d0e221825676d3c82e79b78a41317e6159355190b2ea2105`.

Input hashes, package versions, and output hashes are recorded in
`artifacts/explanations/EXP-FID-0001/manifest.json`.

## Behavioral tests

For each model, sample, and k, the runner creates two perturbations for both candidate and
reference features:

1. Keep-only: begin with the training baseline and restore the selected features.
2. Delete-selected: begin with the sample and replace the selected features with the training
   baseline.

Probabilities are measured for the class predicted on the unmodified sample. The outputs report
rank overlap at k, keep-only prediction preservation, keep-only target-probability closeness,
absolute sufficiency gap, and comprehensiveness drop. Raw signed sufficiency and
comprehensiveness values are retained; negative values are not clipped.

## Execution evidence

- 880 per-sample rows: 220 model/sample cases × 4 values of k.
- 16 aggregate rows: 4 models × 4 values of k.
- 54 samples for MODEL-C1, 53 for MODEL-C2, 54 for MODEL-C3, and 59 for MODEL-C4.
- All configured models and k values were present.
- Manifest status: `EXECUTED`.
- Output SHA-256 values:
  - per-sample: `1e42b24da0f527e6ea2696f6491ca3811fc873bc453ca2a5c8c7fd33643bd54f`
  - summary: `08a94f2fb529315d4869fca8ba6a17d454ccf144abbfd2eb3790f18cbb29c4a5`

## Selected aggregate results

All values below come from `results/xai/stage10_fidelity_summary.csv`.

| Model | Candidate | k | Rank overlap | Prediction preserved | Probability closeness | Abs. sufficiency gap | Comprehensiveness drop |
|---|---|---:|---:|---:|---:|---:|---:|
| MODEL-C1 | intrinsic coefficient | 1 | 0.611 | 0.481 | 0.628 | 0.372 | 0.059 |
| MODEL-C1 | intrinsic coefficient | 3 | 0.630 | 0.630 | 0.692 | 0.308 | 0.133 |
| MODEL-C1 | intrinsic coefficient | 5 | 0.600 | 0.630 | 0.715 | 0.285 | 0.177 |
| MODEL-C1 | intrinsic coefficient | 10 | 0.643 | 0.574 | 0.723 | 0.277 | 0.264 |
| MODEL-C2 | ablation identity | 10 | 1.000 | 0.623 | 0.844 | 0.156 | 0.164 |
| MODEL-C3 | ablation identity | 10 | 1.000 | 0.352 | 0.712 | 0.288 | 0.125 |
| MODEL-C4 | ablation identity | 10 | 1.000 | 0.695 | 0.815 | 0.185 | 0.198 |

For MODEL-C1, the independent intrinsic-coefficient candidate overlaps 0.600-0.643 with the
ablation reference across k. Its mean keep-only probability closeness rises from 0.628 at k=1
to 0.723 at k=10, while prediction preservation is not monotonic. These are observations, not
a threshold-based adequacy claim.

For MODEL-C2, MODEL-C3, and MODEL-C4, Stage 09 assigned the single-feature-ablation ranking as
both candidate and reference because no independent local intrinsic explainer was available.
Their overlap of 1.0 and zero candidate-reference deltas are therefore identity checks, not
independent confirmation of fidelity. Their perturbation metrics still quantify how their
reference top-k sets preserve full-model behavior.

## Interpretation boundary

No pass/fail threshold was preregistered. Stage 10 is descriptive and does not declare any
model or explanation "faithful enough." It measures host-side behavior only; it does not
establish embedded feasibility, on-device latency, memory use, or energy consumption.

## Artifacts

- `results/xai/stage10_fidelity_per_sample.csv`
- `results/xai/stage10_fidelity_summary.csv`
- `artifacts/explanations/EXP-FID-0001/config.yaml`
- `artifacts/explanations/EXP-FID-0001/environment.json`
- `artifacts/explanations/EXP-FID-0001/manifest.json`
- `artifacts/explanations/EXP-FID-0001/run.log`

## Next experiment

Stage 11 — explanation stability across chronological drift is now `EXECUTED`; see
`docs/experiments/STAGE11_EXPLANATION_STABILITY.md`. Stage 12 host-side explanation latency is next.
