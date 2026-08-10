# scripts/colab/ — Colab CLI control plane

Small, composable, fail-fast wrappers around the real `google-colab-cli`. Every script runs
inside **WSL2 Ubuntu** (never natively in PowerShell) and sources [`lib.sh`](lib.sh) for shared
config access (`configs/colab.yaml`, single source of truth — Mission 39) and logging.

Full workflow documentation: [`docs/COLAB_CLI_VSCODE_WORKFLOW.md`](../../docs/COLAB_CLI_VSCODE_WORKFLOW.md).
Current verified status: [`results/reproducibility/COLAB_STATUS.md`](../../results/reproducibility/COLAB_STATUS.md).

| Script | Purpose |
|---|---|
| `bootstrap_wsl.sh` | Install/verify `uv`, `python3`, `git` inside WSL2. |
| `verify_cli.sh` | Install/update the real `colab` CLI via `uv tool`; print its version. |
| `auth.sh` | Explicit OAuth2 authentication against the Colab backend. |
| `start_cpu.sh` | Create/reuse the canonical CPU session `drift-tinyml-cpu`. |
| `start_gpu.sh [T4\|L4\|G4\|A100]` | Create/reuse the optional GPU session. |
| `status.sh` | List all sessions and the canonical CPU/GPU session status. |
| `prepare_workspace.sh` | Build `dist/colab_workspace.tar.gz` from the local repo. |
| `upload_workspace.sh` | Upload + extract the workspace bundle; verify required paths. |
| `install_environment.sh` | Install `requirements-colab.txt` remotely; verify imports. |
| `mount_drive.sh` | Mount Drive; create the canonical persistent folder tree. |
| `run_notebook.sh <nb> <RUN_ID>` | Execute one notebook remotely as an execution copy. |
| `run_core_repro.sh` | Orchestrate Notebook 00 → 01 (hard dataset gate) → 02. |
| `run_checkpoint2.sh` | Orchestrate the full Checkpoint-2 pipeline (no deep learning). |
| `download_results.sh <RUN_ID>` | Download only small validated artifacts for a run. |
| `export_logs.sh <RUN_ID>` | Export session logs locally and (best-effort) to Drive. |
| `stop.sh [SESSION]` | Stop a session and verify it actually stopped. |
| `smoke_test.py` | Ephemeral `colab run` payload — NOT scientific evidence. |

Every script uses `set -euo pipefail` and is safe to re-run (idempotent where the underlying
CLI supports it — e.g. `start_cpu.sh` reuses an existing session instead of creating a
duplicate). Config values (session names, remote paths, dataset gate) are read from
`configs/colab.yaml` through `read_config.py`; nothing is hardcoded twice.

**Prerequisite:** WSL2 Ubuntu must be installed and these scripts run from inside it
(`wsl -d Ubuntu -- bash -lc "scripts/colab/<script>.sh"`). See
`results/reproducibility/COLAB_STATUS.md` for the currently observed WSL2/CLI/auth state.
