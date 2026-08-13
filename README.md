# Drift-Robust Explainable TinyML for Electronic-Nose Sensing

**Chronological Evaluation, Resource-Aware Explanations, and Reproducible Edge Deployment**

Publication-oriented research software for studying chronological sensor drift in the [UCI Gas Sensor Array Drift dataset](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset). The system separates verified evidence from planned work throughout — a missing result is recorded as `NOT_EXECUTED`; it is never estimated, simulated, or filled in.

## Research question

> Can lightweight machine-learning models combined with resource-aware explanation strategies maintain useful predictive performance and interpretable behavior under chronological electronic-nose sensor drift, while satisfying the memory, latency, and energy constraints of TinyML-class microcontrollers?

This question is not yet fully answered — see the [research portal](#research-portal-web-application) for exactly what is currently evidenced versus planned.

## Architecture

```
UCI Gas Sensor Array Drift Dataset
  -> validation -> chronological split -> frozen preprocessing
  -> baseline models -> chronological drift evaluation
  -> evidence-selected models -> resource-aware XAI
  -> fidelity + stability -> quantization/export
  -> nRF52840 / Cortex-M4F -> Flash + SRAM -> physical latency
  -> Nordic PPK2 energy -> Pareto analysis
  -> saved experiment artifacts -> GitHub + Hugging Face + Kaggle
  -> Vercel research portal -> manuscript
```

Everything left of "evidence-selected models" is executed (Checkpoint 1–2). Everything from
resource-aware XAI onward is `NOT_EXECUTED` — see `configs/pipeline_stages.yaml` for the
authoritative, version-controlled status of all 23 pipeline stages.

## Repository structure

| Path | Contents |
|---|---|
| `src/` | Data loading, drift metrics, model training/evaluation, Colab control plane, research-platform bridge |
| `notebooks/` | 00–03: environment, dataset/drift audit, classical baselines, temporal adaptation |
| `configs/` | Frozen protocol/model/pipeline-stage definitions (version-controlled, never silently changed) |
| `results/` | Figures, tables, baseline metrics, drift metrics, experiment registry, reproducibility artifacts |
| `artifacts/` | Trained model files (`.joblib`), embeddings, explanations, quantized exports |
| `paper/` | Claim-evidence matrix, figure/table indices, result/discussion drafts (evidence-controlled) |
| `platforms/` | Staged Hugging Face and Kaggle publishing assets (private by default) |
| `scripts/colab/`, `scripts/bridge/`, `scripts/portal/` | Colab CLI control plane, GitHub/HF/Kaggle bridge, evidence-export pipeline |
| `research-portal/` | Next.js evidence-driven research portal (see below) |
| `docs/` | Protocol, reproducibility, Colab workflow, and platform-bridge documentation |

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

## Experimental protocol

- `FIXED_ORIGIN` (primary): fit all preprocessing and models on batch 1; evaluate batches 2–10 without retraining.
- `EXPANDING_WINDOW`: retrain using all batches strictly before the test batch.
- `IID_DIAGNOSTIC`: stratified random split, explicitly diagnostic — never a primary result.

Frozen in `configs/chronological_protocol.yaml`. See [research protocol](docs/RESEARCH_PROTOCOL.md), [reproducibility guide](docs/REPRODUCIBILITY.md), and [Colab guide](docs/COLAB_GUIDE.md).

## Scientific evidence policy

Every number must be produced by executed code and linked to an artifact. Experiment states are `PLANNED`, `RUNNING`, `COMPLETED`, `FAILED`, `INVALID`, `NOT_EXECUTED`, or `SUPERSEDED`. Synthetic data is limited to unit tests. Physical Flash, SRAM, MCU latency, and PPK2 energy remain `NOT_EXECUTED` until measured on real hardware. The research portal's evidence loader (`research-portal/lib/evidence.ts`) enforces this in the UI: a missing artifact renders as `NOT EXECUTED`, never a placeholder number.

## Google Colab Development

**Interactive (Mode A):** open a notebook, choose **Select Kernel → Colab → Auto Connect**, then run notebook 00 before other notebooks.

**CLI automation (Mode B, evidence-grade):** `scripts/colab/` drives named Colab sessions from **WSL2 Ubuntu** via the real `google-colab-cli`, orchestrated through VS Code tasks. Full workflow: [`docs/COLAB_CLI_VSCODE_WORKFLOW.md`](docs/COLAB_CLI_VSCODE_WORKFLOW.md). Current verified status: [`results/reproducibility/COLAB_STATUS.md`](results/reproducibility/COLAB_STATUS.md) — treat anything not recorded there as `NOT_EXECUTED`.

## GitHub / Hugging Face / Kaggle bridge

GitHub is the canonical source of truth; Hugging Face and Kaggle are evidence/reproduction platforms, both private by default and never uploaded to automatically. Full policy: [`docs/RESEARCH_PLATFORM_BRIDGE.md`](docs/RESEARCH_PLATFORM_BRIDGE.md). Provenance graph: [`docs/PLATFORM_PROVENANCE.md`](docs/PLATFORM_PROVENANCE.md).

## Hardware

Target: Nordic nRF52840 (Cortex-M4F), instrumented with a Nordic Power Profiler Kit II. No physical measurement has occurred — Flash, SRAM, inference latency, and inference/explanation energy are all `NOT_EXECUTED`. Colab is cloud compute, never a substitute for a physical-hardware claim.

## Research portal (web application)

`research-portal/` is a Next.js (App Router, TypeScript) evidence-driven research portal. It reads **only** from `research-portal/data/evidence/*.json`, generated exclusively by `scripts/portal/export_evidence.py` from real repository artifacts — no page hand-types a metric.

```bash
python scripts/portal/export_evidence.py   # regenerate research-portal/data/evidence/*.json
cd research-portal
npm install
npm run dev      # local development
npm run build    # production build (also used by Vercel)
```

Routes: `/`, `/research`, `/dataset`, `/methodology`, `/pipeline`, `/experiments`, `/results`, `/xai`, `/tinyml`, `/hardware`, `/huggingface`, `/reproducibility`, `/paper`, `/references`, `/professor-review`, `/about`, plus `/api/project-status`, `/api/experiments`, `/api/results`, `/api/hardware`. See `research-portal/README.md` for deployment details.

## Reproducibility

Every executed artifact records: random seed, Python version, package versions, OS/runtime, Git commit, dataset SHA-256, and configuration hash. See [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) and the portal's [`/reproducibility`](research-portal/app/reproducibility/page.tsx) page.

## Paper

`paper/claim_evidence_matrix.csv` links every candidate manuscript claim to its experiment ID, dataset/config hash, git commit, and result artifact, with a `SUPPORTED`/`UNSUPPORTED` verdict decided by the artifact. Results and Discussion prose are intentionally undrafted until evidence supports them (`paper/RESULTS_DRAFT.md`).

## Citation and license

Citation metadata will be added with the publication. Licensed under the [MIT License](LICENSE). The UCI dataset retains its own terms and citation requirements (Vergara, A. (2012). *Gas Sensor Array Drift Dataset* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5RP6W).
