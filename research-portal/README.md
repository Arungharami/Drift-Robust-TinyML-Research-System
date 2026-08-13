# Drift-Robust TinyML Research Portal

This directory contains the public Next.js research portal for:

**Drift-Robust Explainable TinyML for Electronic-Nose Sensing: Chronological Evaluation, Resource-Aware Explanations, and Reproducible Edge Deployment**

The portal is intentionally evidence-first. It is allowed to describe a planned method, but it must not display an experimental number as a result unless that number was produced by an executed experiment and preserved in a traceable artifact.

## Run locally

Requirements: Node.js 20.9 or newer.

```bash
cd research-portal
npm install
npm run dev
```

Production validation:

```bash
npm run build
npm start
```

## Deploy on Vercel

Import the GitHub repository into Vercel and set:

- Framework Preset: **Next.js**
- Root Directory: **research-portal**
- Build Command: default (`next build`)
- Output Directory: default
- Node.js: 20.9+ / a currently supported Vercel Node runtime

Every connected GitHub branch can then receive a Vercel preview deployment; the production branch should remain `main` unless the project deliberately changes that policy.

## Research-system architecture

```text
UCI benchmark
   ↓
Google Colab experiments
   ↓
metrics + models + explanation artifacts + manifests
   ↓
GitHub evidence record ───────────→ Vercel research portal
   ↓                                  ↑
Hugging Face model/dataset cards ─────┘
   ↓
nRF52840 export + firmware
   ↓
map files + latency logs + PPK2 traces
   ↓
verified hardware tables / figures
```

The physical deployment path is intentionally separate from the cloud demo path:

```text
Gas sensor array
   ↓
nRF52840 / Cortex-M4F inference
   ↓
lightweight explanation
   ↓
USB serial or BLE gateway
   ↓
telemetry / demonstration dashboard
```

Hugging Face is used as an ML artifact and demo layer, not as proof that the MCU deployment succeeded.

## Evidence states

The portal uses four explicit states:

- `EXECUTED` — an experiment ran and its artifact is available.
- `IN_PROGRESS` — active work, not a result.
- `PLANNED` — protocol/design work that is not yet frozen or executed.
- `NOT_EXECUTED` — specifically required evidence that does not exist yet.

Do not change `NOT_EXECUTED` to `EXECUTED` based on estimates, simulated values, literature values, or manually typed numbers.

## Machine-readable project status

The portal exposes:

```text
/api/project-status
```

This endpoint currently reports the research stage status. It can later be extended to expose validated artifact manifests without exposing private tokens or unpublished raw data.

## Hugging Face integration plan

After a model passes the evidence gate, publish a dedicated project model repository containing:

- model card and intended use;
- exact preprocessing contract;
- training/evaluation configuration;
- chronological evaluation summary;
- model/export hashes;
- limitations and failure modes;
- link back to the GitHub commit and paper.

For the UCI benchmark, prefer a dataset card/pointer plus split manifests and preprocessing metadata unless the licensing/republication decision has been explicitly reviewed.

An optional Hugging Face Space can host a validated interactive demo. The Vercel portal can link to or embed that Space while keeping physical nRF52840 measurements as the deployment evidence.

## Real-world telemetry

The initial telemetry contract intentionally allows null measurements:

```json
{
  "device_id": "nrf52840-enose-01",
  "timestamp": "ISO-8601",
  "batch_context": "real-world-demo",
  "prediction": null,
  "confidence": null,
  "top_features": [],
  "inference_latency_ms": null,
  "explanation_latency_ms": null,
  "energy_uJ": null,
  "evidence_status": "NOT_EXECUTED"
}
```

A future gateway may populate these fields only from the actual device/measurement pipeline.

## Professor/advisor workflow

Use Vercel preview deployments as review checkpoints:

1. review research question and novelty map;
2. review and freeze chronological protocol;
3. review baseline fairness and leakage controls;
4. execute experiments and attach evidence;
5. review hardware measurement protocol and failures;
6. validate tables/figures before manuscript claims are strengthened;
7. publish the final paper only after evidence and contribution boundaries are agreed.

## Paper publication

The final validated manuscript should be stored under:

```text
paper/final/
```

The repository `.gitignore` is configured so a final paper PDF can be committed there even though generated PDFs elsewhere remain ignored.
