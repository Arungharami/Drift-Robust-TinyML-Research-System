# scripts/bridge/ — GitHub / Hugging Face / Kaggle research bridge

Small, composable, fail-fast wrappers connecting this repo to Hugging Face Hub and Kaggle,
with GitHub kept canonical throughout. `gh`, `hf`, and `kaggle` all run **natively on Windows**
(no WSL2 needed) — unlike `scripts/colab/`, which is WSL2-gated. See
[`docs/RESEARCH_PLATFORM_BRIDGE.md`](../../docs/RESEARCH_PLATFORM_BRIDGE.md) for the full policy
and [`results/reproducibility/bridge/`](../../results/reproducibility/bridge/) for current status.

| Script | Purpose |
|---|---|
| `verify_github.sh` / `verify_huggingface.sh` / `verify_kaggle.sh` | Verify one platform's CLI + auth; write `<platform>_status.json`. |
| `verify_all.sh` (`verify_all.ps1` on native PowerShell) | Run all three verifications in one pass. |
| `bridge_status.py` | One-command READY/BLOCKED/NOT_CONFIGURED/NOT_EXECUTED summary across GitHub, Hugging Face, Kaggle, Colab, Drive. |
| `build_release_bundle.sh` | Build `dist/research_bridge/` from small validated evidence; secret-scans the result. |
| `generate_bridge_manifest.py` | Write `results/reproducibility/bridge/platform_manifest.json` from real, current state. |
| `push_hf_dataset.sh` | Create/confirm the **private** HF dataset repo and upload the release bundle + dataset card. |
| `push_hf_model.sh <bundle>` | Publish a model bundle to the **private** HF model repo — refuses unless `manifest.json.status == COMPLETED`. |
| `prepare_kaggle_dataset.py` | Stage `platforms/kaggle/dataset/` (evidence copy + `dataset-metadata.json`, private). Does not upload. |
| `prepare_kaggle_kernel.py` | Write `platforms/kaggle/kernel/kernel-metadata.json` (private, no GPU/internet by default). Does not upload. |
| `pull_kaggle_outputs.sh <kernel_id>` | Download a Kaggle kernel's outputs locally. |
| `verify_cross_platform_hashes.py` | Compare a local artifact's SHA-256 against a freshly-downloaded remote copy; appends to `artifact_index.csv`. |

Every script uses `set -euo pipefail`, is safe to re-run, and never prints or writes a token.
Config values (repo names, dataset/kernel slugs, release-bundle rules) come from
`configs/research_bridge.yaml` via `read_config.py` — nothing is hardcoded twice.

**Nothing here uploads anything automatically.** `push_hf_dataset.sh`, `push_hf_model.sh`,
`kaggle datasets create`, and `kaggle kernels push` are only ever invoked explicitly, one
command/task at a time, and every new Hub/Kaggle asset is created private.
