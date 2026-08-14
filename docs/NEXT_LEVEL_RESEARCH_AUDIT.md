# Next-Level Research Audit

Audit date: 2026-08-11. Scope: repository, generated portal evidence, and attempted public deployment inspection. The configured public URL `https://drift-robust-tinyml.vercel.app` could not be independently retrieved, so deployed website/repository agreement remains unverified.

## Executive finding

Genuine baseline, drift, adaptation, and Stage 09 explanation-generation artifacts exist. Stage 10–12 validation results, quantized exports, firmware measurements, and PPK2 traces do not. Stage 09 already had four rows in the legacy experiment registry; stale README/reviewer prose caused the reported inconsistency. The deeper defect was duplicated state across prose, YAML, CSV, and portal JSON.

## Findings

| Area | Finding | Severity | Disposition |
|---|---|---:|---|
| Scientific consistency | README called XAI unexecuted while Stage 09 artifacts and registry rows exist. | High | Corrected; Stage 09 stays `EXECUTED`; Stages 10–12 do not inherit that status. |
| Duplicated data | Pipeline YAML, legacy registry, config, prose, and exported JSON overlap. | High | Normalized generated registries now drive a typed portal export; legacy evidence is preserved as input. |
| Status vocabulary | `COMPLETED`, `NOT_EXECUTED`, and evidence types were conflated. | High | Normalized public outputs use `MEASURED`, `DERIVED`, `EXECUTED`, `PLANNED`, `BLOCKED`, `FAILED`, `NOT_APPLICABLE`. |
| Claims | Claim paths existed without normalized artifact identities. | High | Added SHA-256 artifact registry and supported-claim validation. |
| Pipeline dependencies | Full Pareto analysis requires missing physical latency and energy. | High | Hardware-dependent Stages 15–20 marked `BLOCKED`. |
| Website agreement | Source portal loads generated evidence, but lacked a concise state/next/blocker view. | Medium | Added evidence-driven Cockpit and Failure Analysis pages; deployed instance still needs verification. |
| Unsupported novelty | Combination-novelty prose is not backed by an exhaustive current literature review. | High | Literature matrix begins `REVIEW_REQUIRED`; “first” is not authorized. |
| Uncertainty | Probabilities exist, but chronological calibration/risk-coverage has not run. | High | RQ8 remains `PLANNED`; no reliability claim was created. |
| Statistics | Seed 42 is the frozen baseline; multi-seed/bootstrap evidence is absent. | High | Added resampling methodology; RQ1–RQ3 remain only partly answered. |
| Model development | Quantization had no frozen embedded candidate protocol. | High | Added protocol separating serialized size, parameter bytes, Flash, and SRAM. |
| Hardware | No board record, firmware hash, map file, device latency log, or PPK2 trace. | Critical | Physical claims remain blocked; host proxies are forbidden. |
| Licensing | Code is MIT; external dataset licensing needs source verification. | Medium | External registry makes license confirmation a selection gate. |
| Visualizations | Source CSVs exist, but N/unit/protocol/experiment/hash are not uniform in all captions. | Medium | Open; figures were not relabeled without evidence. |
| Feature semantics | “128 features” concealed 16 sensors × 8 response characteristics. | High | Added canonical feature metadata with sensor, family, phase, EMA alpha, interpretation, and source column. |
| Provenance | Not every metric had a long-format unit and artifact ID. | High | Generated measurement/artifact registries add these; unknown N/CI remain blank. |

## Source-of-truth architecture

Existing artifacts are immutable inputs. `scripts/build_research_intelligence.py` deterministically builds normalized experiments, measurements, artifacts, claims, and the 128-row feature ontology. `scripts/validate_research_evidence.py` checks states, units, orphan links, paths, hashes, and supported claims. `scripts/portal/export_evidence.py` produces portal JSON; pages consume only typed accessors in `lib/evidence.ts`.

## Evidence created in this phase

No predictive, fidelity, stability, uncertainty, quantization, latency, memory, or energy result was created. New executed outputs are data-governance evidence: normalized rows, a deterministic feature ontology, computed hashes, and validation results. They are not physical measurements.

## Next scientific experiment

Execute `EXP-XAI-FIDELITY-001` against frozen Stage 09 artifacts. Pre-register method-specific retention/deletion and probability-degradation metrics for local representations and prediction/permutation-score effects for global representations. Preserve per-sample outputs and bootstrap intervals. Do not proceed to explanation-stability claims until method applicability and fidelity are resolved.
