---
license: other
tags:
  - reproducibility
  - electronic-nose
  - concept-drift
  - tinyml
pretty_name: Drift-Robust TinyML Research Evidence
---

# Drift-Robust TinyML Research Evidence (dataset card)

**Repository status:** DRAFT — not yet pushed to the Hub. Push explicitly with
`scripts/bridge/push_hf_dataset.sh` once `hf auth login` has been completed. PRIVATE by default
(see `configs/research_bridge.yaml: huggingface.private_by_default`).

## What this is

Derived **reproducibility evidence** for the Drift-Robust Explainable TinyML research project —
manifests, hashes, environment captures, validation reports, and small result tables produced
by executing the code in
[Arungharami/Drift-Robust-TinyML-Research-System](https://github.com/Arungharami/Drift-Robust-TinyML-Research-System).

**This repository does NOT redistribute the raw UCI dataset archive.** Only derived, small
evidence files are included (see `configs/research_bridge.yaml: release_bundle` for the exact
include/exclude rules — `data/raw/*` is explicitly excluded from every release bundle).

## Original data provenance

- **Source:** [UCI Gas Sensor Array Drift Dataset](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset)
  (Vergara et al.). This project does not claim any ownership of the original UCI data —
  attribution and redistribution terms are governed by UCI's own license for that dataset.
  Anyone reproducing this work should download the archive directly from UCI, not from this
  repository.
- **Expected dimensions:** 13,910 observations × 128 features, 10 chronological batches, 6 gas
  classes.
- **Official archive SHA-256:**
  `91e8f466f202e7a093d657673ce47311c3e90416f7df3057966058961c351fe4`

## Chronology

Batches are chronologically ordered (Batch 1 earliest, Batch 10 latest). The project's primary
evaluation protocol (`FIXED_ORIGIN`) trains only on Batch 1 and evaluates on Batches 2–10,
respecting time order; `EXPANDING_WINDOW` and `IID_DIAGNOSTIC` are secondary/diagnostic
protocols. See `docs/RESEARCH_PROTOCOL.md` in the source repository.

## Derived-file descriptions

| File | Description |
|---|---|
| `dataset_validation.json` / `.md` | Verified dataset dimensions, chronology, and archive SHA-256 against the values above. |
| `environment.json` | Captured local/CI execution environment (package versions, Python, OS). |
| `bridge/platform_manifest.json` | Cross-platform provenance manifest: Git SHA, dataset SHA, experiment/config SHAs, per-platform status. |
| `bridge/github_status.json` | GitHub CLI auth/repo state at time of evidence generation. |
| `bridge/artifact_index.csv` | SHA-256 index of every artifact exported to Hugging Face/Kaggle, with local-vs-remote verification status. |

## License / attribution

- This derived evidence: see the source repository's [LICENSE](https://github.com/Arungharami/Drift-Robust-TinyML-Research-System/blob/main/LICENSE) (MIT).
- Original UCI dataset: retains its own UCI citation/attribution terms — see the UCI dataset
  page linked above. Redistribution of the raw archive itself has not been verified against
  those terms, which is exactly why it is excluded from this repository.

## Limitations

- This is reproducibility evidence, not a standalone ML-ready dataset release — some fields
  will read `NOT_EXECUTED` / `NOT_CREATED` until the corresponding pipeline stage has actually
  run (see `results/reproducibility/COLAB_STATUS.md` and `bridge/platform_manifest.json` in the
  source repo for current state).
- No physical-hardware measurements (Flash/SRAM/MCU latency/PPK2 energy) are included; those
  remain `NOT_EXECUTED` at this checkpoint.

## Reproduction instructions

1. Clone [the GitHub repository](https://github.com/Arungharami/Drift-Robust-TinyML-Research-System) (canonical source of truth — this Hub repo is a mirror of evidence, not the source).
2. Download the official UCI archive yourself and verify its SHA-256 against the value above.
3. Follow `docs/REPRODUCIBILITY.md` and `docs/RESEARCH_PLATFORM_BRIDGE.md` in that repository.
