# Drift-Robust Explainable TinyML for Electronic-Nose Sensing

Publication-oriented research software for studying chronological sensor drift in the [UCI Gas Sensor Array Drift dataset](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset). The system separates verified evidence from planned work and treats time-respecting evaluation as the primary protocol.

## Research questions

1. How does feature distribution drift evolve from chronological batch 1 to batches 2–10?
2. How much does random IID evaluation overestimate future-batch performance?
3. Can compact representations and models retain predictions and explanations under drift?
4. What can be quantized for TinyML without confusing software artifacts with MCU measurements?

## Checkpoint status

Checkpoint 1 implements reproducible environment capture, official dataset acquisition with SHA-256 manifests, validation, chronology-safe splits, an experiment registry, drift metrics, initial figures, notebooks, tests, and CI. Checkpoint 2 adds executed fixed-origin classical baselines, expanding-window adaptation, an explicitly diagnostic IID comparison, class-level errors, drift/performance associations, permutation importance, complexity profiles, and prediction-backed publication artifacts. Deep models, XAI, quantization experiments, and physical hardware measurements are **NOT_EXECUTED**.

## Quick start

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python scripts/download_dataset.py
python scripts/validate_dataset.py
python scripts/run_drift_analysis.py
pytest -q
```

Generated data and results are ignored by Git; manifests and result tables are retained as evidence. The downloader never silently replaces raw files.

## Protocols

- `FIXED_ORIGIN`: fit all preprocessing and models on batch 1; evaluate batches 2–10.
- `EXPANDING_WINDOW`: train only on batches preceding the test batch.
- `IID_DIAGNOSTIC`: random split, explicitly diagnostic rather than a primary result.

See [research protocol](docs/RESEARCH_PROTOCOL.md), [reproducibility guide](docs/REPRODUCIBILITY.md), and [Colab guide](docs/COLAB_GUIDE.md). Notebooks 00 and 01 orchestrate reusable code in `src/`; they do not contain hidden analysis logic.

## Google Colab Development

**Interactive (Mode A):** open a notebook, choose **Select Kernel → Colab → Auto Connect**, then run notebook 00 before other notebooks. Actual Colab execution is reported only when kernel evidence exists. Private clone instructions use a Colab Secret named `GITHUB_TOKEN` without printing or persisting it.

**CLI automation (Mode B, evidence-grade):** `scripts/colab/` drives named Colab sessions (`drift-tinyml-cpu` / `drift-tinyml-gpu`) from **WSL2 Ubuntu** via the real `google-colab-cli`, orchestrated through VS Code tasks (`Ctrl+Shift+P` → `Tasks: Run Task` → `Colab: ...`). Core reproduction — Notebook 00 → 01 (hard dataset gate) → 02 on real Colab — runs via the **`Colab: Run Core Reproduction`** task (or `scripts/colab/run_core_repro.sh` inside WSL2). Every run gets a `RUN_ID` and `run_manifest.json`; results land under `runs/<RUN_ID>/` locally and `results/reproducibility/` (logs, dataset-vs-Colab baseline comparison, environment manifest).

Full workflow (all three modes, WSL2 setup, secrets policy): [`docs/COLAB_CLI_VSCODE_WORKFLOW.md`](docs/COLAB_CLI_VSCODE_WORKFLOW.md). Current verified CLI/WSL2/session/gate state: [`results/reproducibility/COLAB_STATUS.md`](results/reproducibility/COLAB_STATUS.md) — treat anything not recorded there as `NOT_EXECUTED`.

## Scientific integrity

Every number must be produced by executed code and linked to an artifact. Experiment states are `PLANNED`, `RUNNING`, `COMPLETED`, `FAILED`, `INVALID`, `NOT_EXECUTED`, or `SUPERSEDED`. Synthetic data is limited to unit tests. Physical Flash, SRAM, MCU latency, and PPK2 energy remain `NOT_EXECUTED` until measured on hardware.

## Citation and license

Citation metadata will be added with the publication. Licensed under the [MIT License](LICENSE). The UCI dataset retains its own terms and citation requirements.
