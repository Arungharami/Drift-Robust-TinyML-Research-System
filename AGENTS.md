# AGENTS.md

## Mission

Advance the drift-robust explainable TinyML study while preserving a strict chain from source data and configuration to executed artifacts, reported claims, and the public portal.

## Non-negotiable evidence rules

- Never fabricate, estimate, interpolate, or "fill in" a scientific result.
- A numerical claim is supported only when an executed experiment produced a saved artifact that identifies its dataset/configuration and source commit.
- Missing evidence remains `NOT_EXECUTED`, `BLOCKED`, `FAILED`, or `INVALID`; do not convert those states to success.
- Host or Colab measurements are not physical nRF52840 measurements.
- Flash, SRAM, on-device latency, and PPK2 energy require real hardware/tool output. Keep their values null and their state non-executed or blocked until such evidence exists.
- Synthetic data is permitted only in tests and must never be presented as a research result.
- Do not strengthen manuscript, README, portal, model-card, or dataset-card claims beyond the saved evidence.

## Sources of truth

- `configs/pipeline_stages.yaml` is the authoritative pipeline-status registry.
- `paper/claim_evidence_matrix.csv` is the authoritative mapping from manuscript claims to evidence.
- `results/registry/experiment_registry.csv` records experiment identity and lifecycle.
- `results/` and `artifacts/` contain execution evidence; raw logs and manifests take precedence over prose summaries.
- `research-portal/data/evidence/*.json` is generated output. Regenerate it with `python scripts/portal/export_evidence.py`; never hand-edit reported values or statuses there.
- If two documents disagree, report the inconsistency and reconcile derived prose to the authoritative artifact. Do not silently choose the more favorable value.

## Required workflow

1. Begin with a read-only audit of the relevant configuration, code, tests, existing artifacts, and current Git diff.
2. State the bounded objective, required inputs, success criteria, and expected artifact paths before editing.
3. Change one scientific stage or one infrastructure concern at a time.
4. Preserve frozen chronological protocols and leakage controls unless the task explicitly creates a new versioned protocol.
5. Run the narrowest relevant validation and record exactly which commands ran and their outcomes.
6. Regenerate derived portal evidence only after its source artifacts or status registry change.
7. Inspect the final diff for unrelated changes, secrets, generated noise, and unsupported prose.
8. Use a branch and draft pull request. Do not write directly to the default branch.

## Validation

For Python/research changes, run the relevant subset of:

```bash
python -m compileall -q src
pytest -q
python scripts/portal/export_evidence.py
```

Validate edited YAML, JSON, CSV schemas, and notebooks. For portal changes, run:

```bash
cd research-portal
npm ci
npm run typecheck
npm run lint
npm run build
```

A command that was unavailable or not run must be reported as `NOT_RUN`; do not describe it as passed.

## Data, credentials, and publishing

- Do not replace or modify canonical raw data silently.
- Preserve dataset URLs, licenses, checksums, split manifests, preprocessing contracts, seeds, package versions, and source commit identifiers.
- Never commit API keys, tokens, private URLs, credentials, or local secret files.
- Do not upload to Hugging Face, Kaggle, Vercel, or another external service without an explicit user request.
- External research assets remain private by default until the user approves publication.

## Manuscript and portal language

Distinguish clearly among `EXECUTED`, `RUNNING`, `PLANNED`, `NOT_EXECUTED`, `BLOCKED`, `FAILED`, `INVALID`, and `SUPERSEDED`. Use "worker-reported" or "pipeline-recorded" where independent verification has not occurred. Describe limitations and negative results with the same prominence as favorable findings.

## Starting rule for a new agent session

Read this file, `configs/pipeline_stages.yaml`, `paper/claim_evidence_matrix.csv`, and the relevant experiment documentation before proposing work. Prefer the highest-value software stage whose dependencies are satisfied. Never bypass a failed or blocked gate.
