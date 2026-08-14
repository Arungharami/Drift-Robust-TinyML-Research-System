# Colab CLI Control Plane — Status

This file is the single source of truth for "what has actually been verified/executed" on the
real Google Colab CLI control plane. It is updated only after a real check/run, never from
assumption. Stale completed state must never masquerade as current — if a step below has not
been re-verified since the WSL2/CLI environment last changed, treat it as unknown, not passing.

**Last updated:** 2026-08-10 (third verification pass — WSL2 engine now present, blocked on the "Virtual Machine Platform" optional component)

## WSL2 verification log

| Attempt | Result |
|---|---|
| 2026-08-10, pass 1 (infrastructure build) | `wsl --status` / `wsl -l -v`: "The Windows Subsystem for Linux is not installed." |
| 2026-08-10, pass 2 (post user-reported `wsl --install -d Ubuntu`) | Same "not installed" stub message on all three checks. Diagnosed as install not yet completed as Administrator, or restart pending. |
| 2026-08-10, pass 3 (post user follow-up) | `wsl --version` now succeeds: **WSL version 2.7.11.0**, kernel 6.18.33.2-2 — the WSL engine itself is installed. However `wsl --status` reports: *"WSL2 is unable to start since virtualization is not enabled on this machine... enable the 'Virtual Machine Platform' optional component... Enable by running: wsl.exe --install --no-distribution"*. `wsl -l -v` reports: *"Windows Subsystem for Linux has no installed distributions."* Cross-checked with `systeminfo`: all four Hyper-V hardware prerequisites pass — VM Monitor Mode Extensions: Yes, **Virtualization Enabled In Firmware: Yes**, Second Level Address Translation: Yes, Data Execution Prevention Available: Yes. **Conclusion: this is a real hardware-capable machine; the sole remaining blocker is the "Virtual Machine Platform" Windows optional component, a software toggle — no BIOS/firmware trip is required.** No Ubuntu distribution is registered yet either way. |

## Control plane

| Component | Status | Detail |
|---|---|---|
| CLI installed | **NO** | `google-colab-cli` has not been installed anywhere — a working WSL2 distribution is a prerequisite and none is registered yet. |
| CLI version | N/A | Not installed. |
| WSL2 engine | **INSTALLED** (2.7.11.0) | `wsl --version` succeeds. Not yet usable — see "Virtual Machine Platform" blocker below. |
| WSL2 usable | **NO — BLOCKED** | `wsl --status`: "WSL2 is unable to start since virtualization is not enabled on this machine" → really means the "Virtual Machine Platform" Windows optional component is off. Firmware/hardware virtualization itself is confirmed enabled (see verification log). Gate 1 of the reproduction-continuation task forbids proceeding past this point until Ubuntu can execute bash successfully. |
| WSL2 distribution | N/A | No distributions registered (`wsl -l -v`: "has no installed distributions"). |
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

**USER ACTION REQUIRED (third request — progress made, one component left).**

The WSL2 engine is installed and the hardware/firmware fully supports virtualization. Only the
"Virtual Machine Platform" Windows optional component remains off. No BIOS/UEFI trip is needed.

1. Open PowerShell **as Administrator** (right-click → "Run as administrator"; confirm the UAC
   prompt actually appears — if it doesn't, the shell is not elevated and this will silently
   no-op).
2. Run: `wsl.exe --install --no-distribution` — this enables "Virtual Machine Platform" (and
   the WSL optional component if somehow still off) without also trying to fetch a distro.
3. **Fully restart Windows** — enabling an optional Windows component genuinely requires a
   reboot to take effect, unlike the previous pass.
4. After restart, open a *new* PowerShell window (elevation not required for this check) and
   run `wsl --status` — it should report no virtualization error. Then run
   `wsl --install -d Ubuntu` to actually fetch and register the Ubuntu distribution, which pass
   3 confirmed is still missing.
5. Confirm directly with `wsl -l -v` — Ubuntu should be listed at **VERSION 2** — before
   re-invoking any Colab task.

Once that's confirmed, resume with `Colab: Bootstrap WSL` → `Colab: Verify CLI` →
`Colab: Authenticate` → `Colab: Start CPU` → `Colab: Smoke Test` from the VS Code command
palette (`Ctrl+Shift+P` → `Tasks: Run Task`).
