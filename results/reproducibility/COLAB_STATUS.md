# Colab CLI Control Plane — Status

This file is the single source of truth for "what has actually been verified/executed" on the
real Google Colab CLI control plane. It is updated only after a real check/run, never from
assumption. Stale completed state must never masquerade as current — if a step below has not
been re-verified since the WSL2/CLI environment last changed, treat it as unknown, not passing.

**Last updated:** 2026-08-10 (infrastructure build pass — no real Colab execution has occurred yet)

## Control plane

| Component | Status | Detail |
|---|---|---|
| CLI installed | **NO** | `google-colab-cli` has not been installed anywhere — WSL2 is a prerequisite and is missing. |
| CLI version | N/A | Not installed. |
| WSL2 | **NOT INSTALLED** | `wsl --status` reports: "The Windows Subsystem for Linux is not installed. You can install by running 'wsl.exe --install'." (checked 2026-08-10) |
| WSL2 distribution | N/A | No distributions registered (`wsl -l -v` fails — WSL2 itself is absent, not just Ubuntu). |
| OAuth status | **NOT AUTHENTICATED** | Cannot authenticate without the CLI. |
| VS Code Colab extension | Configured (recommended) | `google.colab` listed in `.vscode/extensions.json`; installation in the editor itself not verified from this session. |
| VS Code tasks.json | **CREATED** | `.vscode/tasks.json` has the full lifecycle task set; all Colab tasks will fail until WSL2 exists. |
| Session status (`drift-tinyml-cpu`) | NOT_EXECUTED | No session has ever been created. |
| Session status (`drift-tinyml-gpu`) | NOT_EXECUTED | No session has ever been created. |
| Drive mounted | NOT_EXECUTED | — |
| Drive persistent root | Not yet created | Target: `/content/drive/MyDrive/Drift-Robust-TinyML-Research-System/` |

## CLI smoke test (Mission 42)

**NOT_EXECUTED.** Requires WSL2 → CLI install → auth → CPU session, in that order. None of
those preconditions are met.

## Notebook execution on REAL Colab

| Notebook | Status |
|---|---|
| `00_environment_and_reproducibility.ipynb` | NOT_EXECUTED on real Colab (this checkpoint's local/CI execution is a separate, already-verified artifact — see `docs/EXPERIMENT_STATUS.md`) |
| `01_dataset_audit_and_drift_characterization.ipynb` | NOT_EXECUTED on real Colab |
| `02_classical_chronological_baselines.ipynb` | NOT_EXECUTED on real Colab |

## Gates

| Gate | Status |
|---|---|
| `COLAB_DATASET_GATE` | NOT_EVALUATED (requires Notebook 01 on real Colab) |
| `COLAB_CORE_REPRO_GATE` | **FAILED** (by definition — Notebook 00/01/02 real-Colab execution has not occurred) |

## Baseline comparison

`results/reproducibility/colab_vs_local_baselines.csv` has not been generated — there is no
Colab-side baseline run to compare against the existing local/CI baseline results yet.

## Artifacts

- Run manifest: none exist yet (`runs/` directory does not exist).
- Execution logs: none exported.
- Downloaded results: none.
- Executed notebooks: none.

## GPU

- Requested: NO (default policy — CPU is canonical; GPU is opt-in per Mission 8/38).
- Profile configuration: **YES** — `configs/colab.yaml` defines `gpu_profiles: [T4, L4, G4, A100]`
  and `scripts/colab/start_gpu.sh` accepts any of them, but none has been allocated.

## Deep learning

NOT_EXECUTED. Not authorized/scoped for this pass (Mission 23).

## Physical hardware

| Item | Status |
|---|---|
| Flash | NOT_EXECUTED |
| SRAM | NOT_EXECUTED |
| MCU inference latency | NOT_EXECUTED |
| MCU explanation latency | NOT_EXECUTED |
| PPK2 inference energy | NOT_EXECUTED |
| PPK2 explanation energy | NOT_EXECUTED |

Colab is not embedded hardware — no line above is satisfied by any Colab run, real or planned.

## Last real run ID

None. `runs/` has not been created by any real execution.

## Next action

**USER ACTION REQUIRED.** Open an Administrator PowerShell window and run:

```
wsl --install -d Ubuntu
```

Restart Windows if prompted, then re-run `Colab: Bootstrap WSL` → `Colab: Verify CLI` →
`Colab: Authenticate` → `Colab: Start CPU` → `Colab: Smoke Test` from the VS Code command
palette (`Ctrl+Shift+P` → `Tasks: Run Task`) to populate the rows above with real, verified
state.
