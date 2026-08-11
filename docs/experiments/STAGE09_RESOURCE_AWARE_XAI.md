# Stage 09 — Resource-Aware Explainability

**Status: EXECUTED.** Experiment ID `EXP-XAI-0001` (registry rows `EXP-XAI-0001-C1..C4`).
Artifacts: `artifacts/explanations/EXP-XAI-0001/`. Result tables: `results/xai/`.

## Objective

What lightweight explanation representations can be generated for the existing drift-robust
model candidates, and which representations are practical enough to evaluate later for
fidelity (Stage 10), stability (Stage 11), and latency (Stage 12) — as a precursor to TinyML
deployment evidence (Stages 13-19)?

This stage does **not** answer whether those representations are faithful, stable, or fast — it
prepares the artifacts that let Stages 10-12 answer those questions with real data instead of
assumption.

## Hypothesis

None asserted yet. Stage 09 is preparatory; Stages 10 and 11 will test hypotheses about
fidelity and drift-stability using the artifacts produced here.

## Protocol

Frozen in `configs/xai/stage09_resource_aware_xai_v1.yaml` (protocol version
`stage09_resource_aware_xai_v1`). Summary:

- **Models**: the four evidence-selected FIXED_ORIGIN classifiers with a saved fitted artifact
  — `MODEL-C1` (Logistic Regression), `MODEL-C2` (Random Forest), `MODEL-C3` (RBF-SVM),
  `MODEL-C4` (MLP Classifier). Verified from `results/registry/experiment_registry.csv` and
  `artifacts/models/*.joblib`, not assumed from any prompt. `EXPANDING_WINDOW` and
  `IID_DIAGNOSTIC` models were never serialized and are therefore **not** eligible.
- **No retraining.** Every model is `joblib.load()`-ed from its frozen `BASE-FIXED-C{n}-001.joblib`
  artifact and used strictly in inference mode.
- **Chronological split unchanged.** Training data is Batch 1 only (as it was for the source
  models); explanations are computed against Batches 2-10, matching `FIXED_ORIGIN`
  (`configs/chronological_protocol.yaml`).
- **Dataset/config hashes**: `dataset_hash=dc9dbcfc4c8e...`, `split_hash=5f3ceed0e1c1...` — both
  identical to the values already recorded for `BASE-FIXED-C1-001..C4-001`, confirming Stage 09
  runs against the exact same data and split as the source models.
- **Seed**: 42 (project-standard), recorded in every manifest.

## Inputs

- `artifacts/models/BASE-FIXED-C{1..4}-001.joblib` — frozen fitted pipelines.
- `data/raw/extracted/Dataset/batch{1..10}.dat` — raw chronological batches.
- `data/manifests/dataset_manifest.json` — archive SHA-256 provenance.

## Explanation methods actually executed

| Method | Scope | Applicable models | Resource class |
|---|---|---|---|
| `INTRINSIC_COEFFICIENT` | global + local | MODEL-C1 only | `INTRINSIC_ZERO_COST` |
| `INTRINSIC_IMPURITY` | global only | MODEL-C2 only | `INTRINSIC_ZERO_COST` |
| `PERMUTATION_IMPORTANCE_MACRO_F1` | global, per evaluation batch | all 4 | `MODEL_AGNOSTIC_MULTI_INFERENCE` |
| `SINGLE_FEATURE_ABLATION_LOCAL` | local | all 4 (all expose `predict_proba`) | `MODEL_AGNOSTIC_SINGLE_INSTANCE_MULTI_INFERENCE` |

Capability is detected by `isinstance`/`hasattr` checks on the *fitted estimator*
(`src/xai/intrinsic.py`, `src/xai/base.py`), never assumed from the model_id string. The full
per-(model, method, scope) applicability matrix — including every `NOT_APPLICABLE` decision and
its reason — is saved verbatim at `results/xai/stage09_manifest.csv`.

### Models/methods skipped, and why

- `INTRINSIC_COEFFICIENT` on MODEL-C2/C3/C4: `NOT_APPLICABLE` — none of Random Forest, SVC, or
  MLPClassifier expose a `coef_` in the sense this method requires.
- `INTRINSIC_IMPURITY` on MODEL-C1/C3/C4: `NOT_APPLICABLE` — only `RandomForestClassifier`
  exposes `feature_importances_` via mean decrease in impurity.
- `INTRINSIC_COEFFICIENT` local scope on MODEL-C2/C3/C4: `NOT_APPLICABLE`, same reason as global.
- `INTRINSIC_IMPURITY` local scope on MODEL-C2: not attempted at all — a per-instance
  decomposition of a random-forest prediction requires tree-path attribution, which was not
  implemented (see Limitations); reporting it as `NOT_APPLICABLE` was judged more honest than
  approximating it.

No eligible model was excluded entirely — every one of the four received at least
`PERMUTATION_IMPORTANCE_MACRO_F1` (global) and `SINGLE_FEATURE_ABLATION_LOCAL` (local).

## SHAP / LIME policy

Neither was run. `shap_enabled: false`, `lime_enabled: false` in the frozen config.
Permutation importance (already the project's frozen feature-importance metric per
`configs/classical_baselines.yaml: feature_importance.method`) serves as the **global**
reference method; single-feature ablation serves as the **local** reference method. SHAP was
considered as an optional off-device reference explainer and deliberately not added this pass —
it is not part of the frozen protocol, adds a new dependency and non-trivial compute cost
(particularly for MODEL-C3/RBF-SVM and MODEL-C4/MLP, which have no fast closed-form SHAP path),
and the mission brief explicitly warns against adding it "merely because this is an XAI
project." If a future stage needs a Shapley-value reference, it should be added as its own
protocol version with its own justification, not folded silently into this one.

## Resource-aware top-k policy

For every (model, method, batch) global ranking, top-1/3/5/10 subsets were extracted
(`src/xai/schema.py::build_reduced_rows`) and saved both as JSON
(`artifacts/explanations/EXP-XAI-0001/reduced/<model_id>/top_<k>.json` and
`batch_<n>_top_<k>.json`) and as rows in `results/xai/stage09_reduced_explanations.csv`. These
are **candidate resource-aware representations only** — nothing here claims they are
TinyML-deployable; that claim can only be made after Stages 13-19 produce physical evidence.

## Chronological data policy

Local samples were drawn from three batches — **2** (earliest post-training / least drifted),
**6** (mid-sequence), and **10** (latest / most drifted) — a deterministic, disclosed choice of
early/mid/late spread rather than all nine batches, to keep the local-explanation compute
bounded. Per (model, batch): up to 2 correctly-classified samples per class, up to 5
misclassified samples, up to 5 near-decision-boundary samples (smallest top-1/top-2 probability
margin), selected by sorted `(batch, row_index)` order — never by unconstrained randomness — so
re-running produces the identical sample set. Total local samples actually selected: MODEL-C1
54, MODEL-C2 53, MODEL-C3 54, MODEL-C4 59 (220 total); by category: 103
`CORRECT_REPRESENTATIVE`, 57 `MISCLASSIFIED`, 57 `NEAR_DECISION_BOUNDARY`, 3 rows satisfying
both `MISCLASSIFIED` and `NEAR_DECISION_BOUNDARY`. Exact `sample_id`s (`B<batch>:<row_index>`)
are saved in `results/xai/stage09_local_samples.csv` so Stage 10/11 reproduce the identical cases.

## Random seeds

`42` throughout — model loading requires none (frozen artifacts), permutation importance uses
it for its internal shuffling, and the sampling policy records it for provenance even though
selection is itself deterministic by sort order.

## Artifact locations

- `artifacts/explanations/EXP-XAI-0001/` — `manifest.json`, `config.yaml`/`config.json`,
  `environment.json`, `feature_map.csv`, per-model `global/`, `local/`, `reduced/`, `logs/`.
- `results/xai/stage09_feature_map.csv` — 128-row feature index → sensor/feature-type mapping.
- `results/xai/stage09_global_importance.csv` — 4,864 rows (all methods, all batches, all models).
- `results/xai/stage09_reduced_explanations.csv` — 722 rows (top-k candidate representations).
- `results/xai/stage09_local_samples.csv` — 220 rows (deterministic local sample selection).
- `results/xai/stage09_local_explanations.csv` — 35,072 rows (per-sample, per-feature contributions).
- `results/xai/stage09_fidelity_prep.csv` — 880 rows (reference-vs-candidate schema for Stage 10).
- `results/xai/stage09_manifest.csv` — the full (model, method, scope) applicability matrix.

## Feature naming

`results/xai/stage09_feature_map.csv` maps each of the 128 raw feature indices to a sensor
(1-16) and a within-sensor feature type. The sensor grouping (16 contiguous blocks of 8) was
already verified and committed in `docs/DATA_DICTIONARY.md`. The within-sensor feature-type
*names* (`dR`, `dR_norm`, `EMAi_0.001/0.01/0.1`, `EMAd_0.001/0.01/0.1`) were verified this
session directly against the UCI dataset page
(https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset), which documents the
steady-state (ΔR, |ΔR|) and rising/decaying exponential-moving-average transient features per
sensor. The page does not publish a numbered 1-8 table, so the *within-block order* used here
follows the documented convention rather than an independently re-derived one — disclosed in
`src/xai/feature_map.py`'s module docstring, not hidden. If this order is later found to be
wrong, only that one file needs correcting; no ranking logic depends on the semantic label,
only on the 1-128 `feature_index`.

## Selected result excerpts (real, from the artifacts above — not illustrative)

Top-3 `PERMUTATION_IMPORTANCE_MACRO_F1` features, Batch 2:

| Model | #1 | #2 | #3 |
|---|---|---|---|
| MODEL-C1 | S9:dR_norm | S2:dR_norm | S10:dR_norm |
| MODEL-C2 | S1:EMAd_0.1 | S9:EMAd_0.1 | S2:EMAd_0.001 |
| MODEL-C3 | S9:dR_norm | S13:EMAi_0.01 | S14:EMAi_0.01 |
| MODEL-C4 | S2:EMAd_0.1 | S13:EMAi_0.1 | S4:EMAi_0.1 |

Top-3 intrinsic-explanation features (model-level, `batch=ALL`):

| Model | Method | #1 | #2 | #3 |
|---|---|---|---|---|
| MODEL-C1 | `INTRINSIC_COEFFICIENT` | S9:dR_norm | S10:dR_norm | S2:dR_norm |
| MODEL-C2 | `INTRINSIC_IMPURITY` | S2:dR | S1:dR | S1:dR_norm |

Rankings visibly differ by model and by method — a genuine empirical observation this stage
makes available, not a claim about which ranking is more *correct* (that is a fidelity
question, deferred to Stage 10).

## Limitations

- Impurity-based importance (`MODEL-C2`) is known to be biased toward high-cardinality /
  high-variance features; this is a documented property of the method, not corrected for here.
- No per-instance (local) explanation exists for MODEL-C2/C3/C4 beyond the model-agnostic
  ablation method — a tree-path decomposition for the Random Forest, or a closed-form gradient
  attribution for the MLP, were judged out of scope for this stage rather than implemented
  hastily.
- `SINGLE_FEATURE_ABLATION_LOCAL`'s baseline is the Batch-1 (training-split) per-feature mean —
  a defensible, leakage-free choice, but a different baseline (e.g. per-class conditional mean)
  would likely shift the specific contribution magnitudes, though not the general method.
- Local sampling covers 3 of 9 evaluation batches (2, 6, 10), not all 9 — a disclosed scope
  decision to bound compute, not a hidden limitation.
- No fidelity, stability, latency, quantization, or hardware conclusion is drawn here. Every
  such field remains `NOT_EXECUTED` on the research portal and in `configs/pipeline_stages.yaml`
  until its own stage runs independently.

## Next experiment

**Stage 10 — Explanation fidelity.** `results/xai/stage09_fidelity_prep.csv` already contains
the `(sample_id, model_id, reference_method, candidate_method, top_k, reference_features,
candidate_features)` schema needed to compute a perturbation-based or overlap-based fidelity
score between each model's reference explanation and its resource-reduced top-k candidate,
without recomputing any explanation from scratch.
