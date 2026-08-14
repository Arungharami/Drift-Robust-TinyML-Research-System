---
license: other
tags:
  - reproducibility
  - electronic-nose
  - concept-drift
  - tinyml
pretty_name: Drift-Robust TinyML Model Release Template
---

# Drift-Robust TinyML Model Card (template)

**Status: NOT_EXECUTED.** No experiment has produced a `COMPLETED`, validated model bundle at
this checkpoint — there is nothing to publish yet. `scripts/bridge/push_hf_model.sh` refuses to
run against anything whose `manifest.json.status` is not exactly `COMPLETED` (Mission 21). This
file is the template that a real release will fill in; every field below stays `NOT_EXECUTED`
until that happens.

Copy this file into the model bundle directory alongside `manifest.json` before running
`scripts/bridge/push_hf_model.sh <bundle_dir>`, then fill in every field marked `NOT_EXECUTED`.

## Model details

| Field | Value |
|---|---|
| Model name | NOT_EXECUTED |
| Experiment ID | NOT_EXECUTED |
| Architecture | NOT_EXECUTED |
| Git SHA (training code) | NOT_EXECUTED |
| Dataset archive SHA-256 | `91e8f466f202e7a093d657673ce47311c3e90416f7df3057966058961c351fe4` (fixed — the official UCI archive hash, independent of which model trained on it) |
| Config SHA | NOT_EXECUTED |

## Training protocol

| Field | Value |
|---|---|
| Chronological train batch(es) | NOT_EXECUTED |
| Chronological test batch(es) | NOT_EXECUTED |
| Protocol (`FIXED_ORIGIN` / `EXPANDING_WINDOW` / `IID_DIAGNOSTIC`) | NOT_EXECUTED |
| Execution environment | NOT_EXECUTED (must be one of `LOCAL_WINDOWS_CPU`, `LOCAL_WINDOWS_GPU`, `WSL_LOCAL`, `COLAB_CPU`, `COLAB_T4`, `COLAB_L4`, `COLAB_G4`, `COLAB_A100`, `COLAB_H100` — never inferred, always the actually-observed runtime) |

## Metrics

| Metric | Value |
|---|---|
| Accuracy (per future batch) | NOT_EXECUTED |
| Macro F1 (per future batch) | NOT_EXECUTED |
| Balanced accuracy (per future batch) | NOT_EXECUTED |

## Intended use

NOT_EXECUTED — to be filled in once a real model exists. In general: research reproducibility
artifact for chronological-drift evaluation of electronic-nose sensing, not a production
classifier.

## Out-of-scope use

Not validated for deployment on physical hardware, safety-critical applications, or any gas
sensor array other than the UCI Gas Sensor Array Drift Dataset's original 16-sensor array.

## TinyML status

NOT_EXECUTED — quantization/on-device conversion has not occurred at this checkpoint.

## Hardware status

Flash = NOT_EXECUTED
SRAM = NOT_EXECUTED
MCU inference latency = NOT_EXECUTED
MCU explanation latency = NOT_EXECUTED
PPK2 inference energy = NOT_EXECUTED
PPK2 explanation energy = NOT_EXECUTED

Colab (real or planned) is cloud compute, not embedded hardware — no Colab run satisfies any
line above.
