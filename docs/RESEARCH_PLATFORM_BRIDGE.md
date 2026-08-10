# Research Platform Bridge — GitHub / Colab / Hugging Face / Kaggle / Drive

This document explains the multi-platform bridge connecting GitHub, VS Code/Codex, Google
Colab, Hugging Face Hub, and Kaggle, and the policy that keeps scientific provenance intact
across all of them. It complements
[`docs/COLAB_CLI_VSCODE_WORKFLOW.md`](COLAB_CLI_VSCODE_WORKFLOW.md) (Colab-specific) and
[`docs/PLATFORM_PROVENANCE.md`](PLATFORM_PROVENANCE.md) (the provenance graph).

Current verified state of every platform: `results/reproducibility/bridge/*_status.json` and
`results/reproducibility/bridge/platform_manifest.json` — regenerate with
`scripts/bridge/verify_all.sh` + `scripts/bridge/generate_bridge_manifest.py` before trusting
anything here as current.

## Why each platform exists

| Platform | Role | Never used for |
|---|---|---|
| **GitHub** | Canonical source of truth: code, configs, tests, CI, small evidence artifacts, manifests, experiment registry, paper source, Git history. | Large compute, large binary storage. |
| **Colab** | Primary cloud compute: real notebook execution, CPU reproduction, future GPU deep learning, XAI, remote logs. | Canonical code storage or canonical results storage. |
| **Hugging Face Hub** | Research artifact hub: validated model artifacts, model/dataset cards, derived datasets, quantized models. | Canonical source of truth; raw UCI data redistribution. |
| **Kaggle** | Independent reproduction platform: portable evidence packaging, independent notebooks, alternative GPU. | Canonical source of truth; primary compute. |
| **Google Drive** | Large, temporary Colab-session persistence: executed notebooks, large predictions, checkpoints, logs. | Canonical code or canonical results storage. |

## Absolute rule: canonical source policy

**No platform is allowed to silently become the scientific source of truth except GitHub.**
Every released result links back to: Git SHA, dataset SHA, config SHA, experiment ID, execution
environment, and timestamp — see `src/research_bridge/manifest.py`'s schema and
`configs/research_bridge.yaml`, where `github.canonical: true` is enforced by
`src/research_bridge/config.py` (the loader raises if it's ever set to anything else).

Colab, Hugging Face, and Kaggle results are *evidence*, checked against GitHub, never the
reverse. `results/reproducibility/colab_vs_local_baselines.csv` and (once run)
`results/reproducibility/kaggle_vs_local.csv` compare remote-platform outputs against local/CI
evidence and record `MATCH`/`MISMATCH` — local values are never copied into the remote column.

## Authentication

| Platform | CLI | Verify | Login |
|---|---|---|---|
| GitHub | `gh` (native Windows, no WSL needed) | `gh auth status` | `gh auth login` |
| Hugging Face | `hf` (current CLI — **not** the deprecated `huggingface-cli`) | `hf auth whoami` | `hf auth login` (browser) or `hf auth login --token $HF_TOKEN` for automation |
| Kaggle | `kaggle` (official package) | harmless authenticated probe, e.g. `kaggle config view` | `kaggle auth login` (browser) or `KAGGLE_API_TOKEN` env var |
| Colab | `colab` (WSL2-gated — see `docs/COLAB_CLI_VSCODE_WORKFLOW.md`) | `colab --auth=oauth2 sessions` | same |

`gh`, `hf`, and `kaggle` all run **natively on Windows** — `scripts/bridge/*.sh` do not go
through `wsl.exe`, unlike `scripts/colab/*.sh`. One-command status summary:
`python scripts/bridge/bridge_status.py` (READY / BLOCKED / NOT_CONFIGURED / NOT_EXECUTED /
FAILED per platform, never a credential).

## Private/public rules

`configs/research_bridge.yaml` enforces `private_by_default: true` for both `huggingface` and
`kaggle` — the config loader raises `BridgeConfigError` if either is ever flipped to `false`.
Every repo/dataset/kernel this bridge creates is private:

- `hf repos create ... --private` (never `--public`) — `push_hf_dataset.sh`, `push_hf_model.sh`.
- `kaggle datasets create -p ...` (no `-u`/`--public` flag) — `prepare_kaggle_dataset.py` stages
  files but does not upload; a human runs `kaggle datasets create` explicitly.
- `kernel-metadata.json` always has `"is_private": true`.

Nothing here uploads automatically as a side effect of any other script. Every push is one
explicit command, run by a human, one platform at a time.

### Before any public release (not automated — a human checklist)

License audit → secret scan (`src/research_bridge/secrets.py`, run via
`build_release_bundle.sh`) → PII scan → claim/evidence audit → README/card review → artifact
hash verification (`verify_cross_platform_hashes.py`). None of this is currently satisfied for
any asset — nothing has been made public.

## Artifact flow

```
LOCAL/VS Code → Git commit → GitHub CI → Colab execution → evidence artifacts
    → GitHub provenance commit → selected release bundle (scripts/bridge/build_release_bundle.sh)
    → Hugging Face / Kaggle (explicit push) → download verification
    → cross-platform hash MATCH (verify_cross_platform_hashes.py)
```

This hierarchy is never reversed silently (Mission 20). Every artifact exported to another
platform gets a SHA-256 computed locally *before* upload
(`src/research_bridge/hashing.py::sha256_file`) and recomputed on the downloaded copy *after*
(`verify_cross_platform_hashes.py`) — a successful upload alone is never trusted. Results land
in `results/reproducibility/bridge/artifact_index.csv`.

## Reproduction flow (independent verification)

Kaggle exists specifically as an **independent** replication environment — not a live mirror of
Colab's ephemeral state. Only a versioned reproducibility bundle tied to a specific Git SHA is
ever synchronized to Kaggle (Mission 24); Colab's temporary VM state is never pushed there
directly. `platforms/kaggle/kernel/drift_tinyml_reproduction.ipynb` independently re-verifies
dataset integrity and the Checkpoint-1 drift diagnostic against the same Git SHA / dataset hash
/ config the GitHub evidence was produced from.

## Failure recovery

- **Secret found in a release bundle:** `build_release_bundle.sh` exits non-zero before the
  bundle is used anywhere; fix the source file and re-run. Nothing partially-scanned is ever
  uploaded.
- **Hash mismatch after download:** `verify_cross_platform_hashes.py` exits 1 and records
  `MISMATCH` in `artifact_index.csv` — treat the remote copy as untrusted, re-upload, re-verify.
- **CLI not authenticated:** every push script (`push_hf_dataset.sh`, `push_hf_model.sh`) checks
  `hf auth whoami` first and dies with an explicit instruction rather than attempting an upload
  that would fail with a less clear error.
- **Colab CLI blocked (WSL2 gate):** the bridge scripts here never depend on Colab being usable;
  `bridge_status.py` reports `Colab: BLOCKED` independently and the rest of the bridge still
  works. See `results/reproducibility/COLAB_STATUS.md` for the current WSL2/Colab blocker.

## Hash verification example

```bash
python scripts/bridge/verify_cross_platform_hashes.py \
  results/reproducibility/dataset_validation.json \
  <path to the copy just downloaded from HF/Kaggle> \
  --platform huggingface --remote-identifier <namespace>/drift-robust-tinyml-research-data \
  --remote-revision main
```
