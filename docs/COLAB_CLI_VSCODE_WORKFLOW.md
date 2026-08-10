# VS Code + WSL2 + Google Colab CLI workflow

This is the control-plane workflow for running real Google Colab research sessions from this
VS Code workspace with repeatable commands and full scientific provenance. It complements, and
does not replace, [`docs/COLAB_GUIDE.md`](COLAB_GUIDE.md) (interactive kernel usage) and
[`docs/REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

**Absolute rule:** every run carries an explicit environment label — one of
`LOCAL_WINDOWS_CPU`, `LOCAL_WINDOWS_GPU`, `WSL_LOCAL`, `COLAB_CPU`, `COLAB_T4`, `COLAB_L4`,
`COLAB_G4`, `COLAB_A100`, `COLAB_H100`, `PHYSICAL_NRF52840` — inferred by inspecting the actual
runtime, never assumed from a requested allocation. See `src/colab_control/environments.py`.

The **local Windows Git repository remains canonical**. The Colab VM is disposable compute; the
bundle it receives is generated fresh from this repo by `scripts/colab/prepare_workspace.sh`.

## Three modes

### Mode A — Interactive (VS Code Colab kernel)

```
VS Code → open a notebook → Select Kernel → Colab → Auto Connect
```

Best for: interactive notebook development, graph inspection, debugging cell-by-cell.

A run counted this way is genuine only when `in_colab` is `true` in
`results/reproducibility/environment.json` and the notebook's execution metadata/outputs are
retained (see `docs/COLAB_GUIDE.md`). This mode is a development tool — it is not how
Checkpoint reproduction evidence is produced (that's Mode B).

### Mode B — Reproducible session (Colab CLI, evidence-grade)

```
VS Code task → WSL2 → Colab CLI → named CPU/GPU session → controlled execution → artifacts/logs → cleanup
```

Best for: research evidence — dataset gate checks, baseline reproduction, Checkpoint 2.

This is the primary pipeline:

1. `Colab: Verify CLI` — install/update the real `google-colab-cli` via `uv` inside WSL2.
2. `Colab: Authenticate` — explicit OAuth2 auth (interactive, browser).
3. `Colab: Start CPU` (or `Start T4` / `Start G4`) — create/reuse a **named** session
   (`drift-tinyml-cpu` / `drift-tinyml-gpu`). Anonymous sessions are never used.
4. `Colab: Prepare Workspace` → `Colab: Upload Workspace` — bundle and ship a clean copy of
   `src/`, `configs/`, `notebooks/`, `scripts/`, `tests/`, `requirements-colab.txt`,
   `pyproject.toml` to `/content/drift_tinyml_enose/`; verify extraction succeeded.
5. `Colab: Install Requirements` — install `requirements-colab.txt` remotely; verify baseline
   imports (numpy, pandas, scipy, sklearn, matplotlib, yaml, joblib).
6. `Colab: Mount Drive` (optional) — persistent storage under
   `/content/drive/MyDrive/Drift-Robust-TinyML-Research-System/`.
7. `Colab: Run Core Reproduction` — orchestrates Notebook 00 → 01 (hard dataset gate) → 02.
   Stops before 02 if the gate fails (`COLAB_DATASET_GATE = FAILED`).
8. `Colab: Download Results` / `Colab: Export Logs` — recover small artifacts and logs
   **before** stopping the session.
9. `Colab: Stop Session` — stop and verify (`SESSION_STOPPED = YES` only after confirming via
   `colab sessions`).

Every run gets a `RUN_ID` (`<UTC timestamp>_<DESCRIPTOR>`, e.g.
`20260810T153000Z_FIXED_ORIGIN_CPU`) and a `run_manifest.json` recording git SHA, branch,
dataset/config hashes, environment label, CLI version, requested vs. actual accelerator,
package versions, and status. See `src/colab_control/manifest.py`.

### Mode C — Ephemeral job (`colab run`)

```
VS Code task → WSL2 → `colab run <script>` → execute one script → retrieve output → automatic teardown
```

Best for: small independent jobs, smoke tests, one-off batch computations.

`Colab: Smoke Test` runs `scripts/colab/smoke_test.py` this way. It prints runtime identity,
Python version, and a deterministic hash, then exits — it demonstrates the CLI can execute a
one-command remote job end-to-end. **It is not scientific evidence**; evidence must come from
Mode B's reproducible scripts/notebooks and saved artifacts.

## Interactive debugging tools (optional, not evidence sources)

- `colab repl` / `colab console` — interactive remote shells for debugging. Document their use
  but never treat their output as reproducible research evidence.
- `colab ssh --help` — an OPTIONAL advanced proxy workflow (Mission 26). Not required for the
  normal pipeline. Primary flow stays: VS Code local repo → WSL2 Colab CLI → remote runtime.

## Why WSL2 (Mission 3)

The Windows repository stays canonical; the Linux-only Colab CLI runs from **WSL2 Ubuntu**, not
natively in PowerShell. Every `scripts/colab/*.sh` script assumes it runs inside WSL2 and every
VS Code task invokes it via:

```
wsl.exe -d Ubuntu --cd "${workspaceFolder}" -- bash -lc "scripts/colab/<script>.sh"
```

`--cd` accepts the Windows path directly and WSL translates it, so the script executes with the
Windows repo checkout as its working directory (via the `/mnt/c/...` bind) without duplicating
the checkout inside the Linux filesystem.

## Secrets (Mission 34-35)

No token, OAuth credential, or GitHub PAT is ever written to `tasks.json`, `settings.json`,
configs, notebooks, or git history. Colab CLI auth state lives under `~/.config/colab-cli/`
inside WSL2 only. Remote GitHub access from the Colab VM is avoided by default — the workspace
bundle is pushed via `colab upload`, not `git clone`, precisely so the VM never needs
repository credentials.

## Command palette usage (Mission 33)

`Ctrl+Shift+P` → `Tasks: Run Task` → pick any `Colab: ...` task. No shell commands need to be
memorized. Current verified CLI/WSL/session/gate status is always in
[`results/reproducibility/COLAB_STATUS.md`](../results/reproducibility/COLAB_STATUS.md) —
treat anything not recorded there as `NOT_EXECUTED`, never as implied success.
