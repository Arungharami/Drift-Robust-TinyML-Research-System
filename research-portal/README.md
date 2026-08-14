# Drift-Robust TinyML research portal

Evidence-driven Next.js portal for **Drift-Robust Explainable TinyML for Electronic-Nose
Sensing**.

The portal may describe planned methodology, but it must never display an experimental number as
a result unless executed code produced it and a traceable repository artifact preserves it.

## Evidence architecture

The application does not hand-type research metrics:

```text
results/ + artifacts/ + configs/ + paper/
                    |
                    v
scripts/portal/export_evidence.py
                    |
                    v
research-portal/data/evidence/*.json
                    |
                    v
research-portal/lib/evidence.ts
                    |
                    v
app/**/page.tsx + app/api/**/route.ts
```

`research-portal/lib/evidence.ts` is the only module that imports generated evidence JSON. If
source evidence is missing, exported values remain null and the UI renders an explicit
non-executed or blocked state.

## Evidence states

- `EXECUTED` — the stage ran and the declared artifacts exist.
- `RUNNING` — active work, not a completed result.
- `PLANNED` — protocol or design work not yet executed.
- `NOT_EXECUTED` — required evidence does not exist.
- `BLOCKED` — execution cannot proceed because a named dependency or resource is unavailable.
- `FAILED` / `INVALID` — execution occurred but did not produce admissible evidence.

Do not promote a status using estimates, manually typed values, literature measurements, or
simulation substituted for physical hardware.

## Local development

Regenerate evidence first from the repository root:

```bash
python scripts/portal/export_evidence.py
cd research-portal
npm ci
npm run typecheck
npm run lint
npm run dev
```

Production validation:

```bash
npm run build
npm start
```

The project uses Next.js App Router, TypeScript, Recharts for evidence-backed plots, and a small
hand-written design system. It supports light/dark presentation without a CSS framework.

## Vercel deployment

Import the GitHub repository and configure:

- Framework Preset: **Next.js**
- Root Directory: **research-portal**
- Build Command: default (`next build`)
- Output Directory: default
- Environment variables: copy the non-secret `NEXT_PUBLIC_*` values from `.env.example`

Generated evidence JSON is committed so Vercel does not need Python or access to the parent
research environment during the build.

Whenever authoritative research artifacts change:

```bash
python scripts/portal/export_evidence.py
git add research-portal/data/evidence
git commit -m "Refresh research portal evidence"
```

## Machine-readable status

The portal exposes `/api/project-status` plus experiment, result, and hardware APIs. These
routes return exported evidence and must not maintain a second hand-written status source.

## Hardware boundary

Hugging Face, Kaggle, Colab, host timing, or a browser demo cannot prove nRF52840 deployment.
Flash, SRAM, on-device latency, and PPK2 energy remain null or non-executed until real device,
toolchain, and measurement artifacts exist.

The real-world telemetry contract therefore permits null measurements:

```json
{
  "device_id": "nrf52840-enose-01",
  "prediction": null,
  "confidence": null,
  "top_features": [],
  "inference_latency_ms": null,
  "explanation_latency_ms": null,
  "energy_uJ": null,
  "evidence_status": "NOT_EXECUTED"
}
```

## Professor/advisor review

Use Vercel previews as review checkpoints:

1. confirm the research question and novelty boundary;
2. freeze chronological splits, leakage controls, baselines, and ablations;
3. review executed evidence and failed gates;
4. validate hardware measurement protocols before device claims;
5. trace every table and figure to a saved artifact;
6. strengthen manuscript claims only after the claim-evidence matrix supports them.

## Consolidation note

The default branch previously contained an earlier single-page portal. The consolidated portal
keeps the research branch's multi-page, artifact-driven implementation because it is wired to
`scripts/portal/export_evidence.py` and the saved evidence directory. The earlier static
`lib/research.ts`, duplicate `next.config.ts`, and single-page application are intentionally
superseded; their history remains available in Git.
