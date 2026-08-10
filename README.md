# Drift-Robust Explainable TinyML for Electronic-Nose Sensing

**Chronological Evaluation, Resource-Aware Explanations, and Reproducible Edge Deployment**

Researcher: **Arun Kumar Gharami**  
Status: **active research — results must be evidence-backed**  
Target edge platform: **nRF52840 / Cortex-M4F**  
Physical energy instrumentation: **Nordic PPK2**

## Research objective

This project studies whether compact machine-learning models can remain useful and explainable under long-term electronic-nose sensor drift while satisfying realistic microcontroller constraints.

The work deliberately combines four requirements that are often evaluated separately:

1. **chronological drift evaluation** rather than relying only on pooled random splits;
2. **resource-aware explainability** with fidelity and stability analysis;
3. **reproducible model/export lineage** from experiment configuration to firmware artifact;
4. **physical edge measurements** for memory, latency, and energy before deployment claims are made.

## Evidence rule

> No numerical result may be presented as an experimental finding unless it comes from an executed experiment and a saved, traceable artifact.

If physical hardware is unavailable, an export fails, or a measurement has not been run, the project records `NOT EXECUTED` or `FAILED` rather than estimating a favorable value.

## Benchmark

The primary benchmark is the **UCI Gas Sensor Array Drift Dataset at Different Concentrations** (DOI: `10.24432/C5MK6M`). UCI reports 13,910 measurements from 16 chemical sensors, six gas classes, 128 features per measurement, and ten time-ordered batches spanning approximately 36 months.

Canonical source:

- https://archive.ics.uci.edu/dataset/270/gas+sensor+array+drift+dataset+at+different+concentrations

## End-to-end research pipeline

```text
01  Dataset acquisition + integrity manifest
02  Frozen chronological evaluation protocol
03  Reproducible lightweight baselines
04  Per-batch drift robustness analysis
05  Resource-aware explanation implementation
06  Explanation fidelity + stability under drift
07  Quantization / embedded export
08  nRF52840 deployment + Flash/SRAM + latency
09  Nordic PPK2 inference/explanation energy
10  Accuracy–trust–resource Pareto analysis
11  Evidence-backed figures, tables, discussion, and final paper
```

Only evidence-supported model configurations advance into the expensive XAI and hardware stages.

## System architecture

```text
UCI benchmark
   ↓
Google Colab experiment pipeline
   ↓
configs + metrics + models + explanation artifacts + manifests
   ↓
GitHub evidence record ───────────────→ Vercel research portal
   ↓                                      ↑
Hugging Face model / dataset cards ───────┘
   ↓
embedded export
   ↓
nRF52840 firmware
   ↓
map files + raw latency logs + PPK2 traces
   ↓
verified hardware tables / figures
```

The project separates the **public ML artifact/demo layer** from the **physical deployment evidence layer**. A Hugging Face demo does not count as proof of nRF52840 feasibility.

## Public research portal

A professional Next.js portal is maintained in:

```text
research-portal/
```

It is designed for Vercel deployment and exposes:

- research question and evidence policy;
- benchmark facts and chronological workflow;
- experiment-stage status (`EXECUTED`, `IN_PROGRESS`, `PLANNED`, `NOT_EXECUTED`);
- equations tied to intended measurements;
- Hugging Face integration plan;
- real-world nRF52840 telemetry contract;
- literature/novelty map;
- professor/advisor review workflow;
- final-paper pathway;
- machine-readable `/api/project-status` endpoint.

For Vercel, set the project **Root Directory** to `research-portal`.

## Colab role

Google Colab is the experiment engine, not the final record. A professional run should export at least:

- environment/package manifest;
- random seeds and configuration;
- dataset/source hashes and split manifest;
- per-batch predictions and metrics;
- trained model artifact;
- explanation artifact;
- quantized/exported artifact when applicable;
- figures/tables generated from saved results.

The GitHub repository should preserve the metadata required to reproduce and audit those outputs.

## Hugging Face role

After a candidate model passes the evidence gate, create a dedicated project model repository containing:

- model card and intended use;
- preprocessing contract;
- chronological evaluation summary;
- exact source Git commit;
- model/export hashes;
- limitations and failure modes;
- links to the paper and this repository.

For the UCI data, prefer a canonical-source dataset card/pointer plus split/preprocessing manifests until the exact republishing decision is reviewed.

An optional Hugging Face Space can host a validated interactive demo, while the MCU remains the authoritative deployment target.

## Real-world deployment path

```text
Gas sensor array
   ↓
nRF52840 / Cortex-M4F
   ├── gas prediction
   └── lightweight explanation
   ↓
USB serial or BLE gateway
   ↓
structured telemetry
   ↓
research/demo dashboard
```

The telemetry schema keeps latency and energy fields null until the relevant physical measurements exist.

## Repository organization

```text
├── data/               # benchmark source/manifest structure; raw data policy applies
├── docs/               # protocol, literature, reproducibility, deployment notes
├── models/             # generated model outputs (normally ignored unless intentionally published)
├── notebooks/          # Colab/Jupyter experiments
├── paper/              # notes, figures/tables, drafts, validated final manuscript
├── research-portal/    # Next.js/Vercel public research portal
├── scripts/            # reproducible command-line experiment helpers
├── src/                # data, model, XAI, export, hardware-support code
├── tests/              # automated validation
└── requirements.txt
```

## Literature anchors

The protocol is being developed against both foundational and recent work, including:

- Vergara et al. (2012), *Chemical gas sensor drift compensation using classifier ensembles*, DOI `10.1016/j.snb.2012.01.074`.
- Rodríguez-Luján et al. (2014), *On the calibration of sensor arrays for pattern recognition using the minimal number of experiments*, DOI `10.1016/j.chemolab.2013.10.012`.
- Disabato & Roveri (2024), *Tiny Machine Learning for Concept Drift*, DOI `10.1109/TNNLS.2022.3229897`.
- Zhang et al. (2025), *Unsupervised Attention-Based Multisource Domain Adaptation Framework for Drift Compensation in Electronic Nose Systems*, DOI `10.1109/TIM.2025.3604131`.
- Lin & Zhan (2026), *Sensor-Drift Compensation in Electronic-Nose-Based Gas Recognition Using Knowledge Distillation*, DOI `10.3390/informatics13010015`.
- Dehghani et al. (2026), *Human-Centered Explainable AI for TinyML Edge Devices: A Pareto-Based Selection Framework with LLM-Guided Design*, arXiv `2608.07091`.

These papers raise the novelty bar. The working contribution therefore focuses on the combined evidence chain of **chronological electronic-nose drift + lightweight explanation fidelity/stability + physically measured MCU resource cost**, rather than making a broad “TinyML + XAI” novelty claim.

## Professor/advisor review workflow

The Vercel preview should be used as a research-meeting artifact:

1. review the problem statement and novelty boundary;
2. review/freeze chronological splits, leakage controls, baselines, and ablations;
3. record methodology decisions before expensive runs;
4. execute experiments and attach traceable artifacts;
5. review failures and physical measurement protocol;
6. validate figures/tables before strengthening manuscript claims;
7. agree contribution/authorship expectations explicitly before final submission.

## Installation

Python research environment:

```bash
pip install -r requirements.txt
```

Portal environment:

```bash
cd research-portal
npm install
npm run dev
```

## Citation

A final BibTeX entry will be added only when the manuscript title, author list, venue/status, and persistent identifier are finalized. Until then, please cite the underlying UCI dataset and the relevant referenced methods directly.
