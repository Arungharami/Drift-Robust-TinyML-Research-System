# System Map (`/system-map`)

Status: implemented, Phase C. Companion to `/pipeline` (the existing 23-stage
raw registry view) — the system map is a grouped, dependency-aware visual
layer over the same evidence, not a second pipeline registry.

## What this page is

A plain HTML/CSS node-and-edge view of the complete research architecture,
from the physical sample to the evidence ledger, deliberately **not** a 3D
scene (see Part 12 of the Phase-C brief this was built against). This keeps
it fully server-rendered, fast, and usable with no JavaScript beyond the
click-to-select interactivity.

## Data source

`research-portal/lib/digital-twin/system-components.ts` (`buildSystemComponents()`)
is the single registry. It reads exclusively through
`research-portal/lib/evidence.ts` — `getPipeline()`, `getDataset()`,
`getXai()`, `getEmbedded()`, `getProjectStatus()`, `getExperiments()` — the
same accessors every other evidence-driven page uses. It never invents a
status: where a conceptual stage below has a real pipeline stage behind it,
`pipelineIds` names the exact stage id(s) from `configs/pipeline_stages.yaml`
and `researchStatus` is derived from them (see `stageStatus()` /
`worstStatus()` helpers in that file). Where no pipeline stage, protocol, or
experiment exists at all — live monitoring, production retraining, the
gateway/telemetry bridge — `researchStatus` is explicitly `PLANNED` and
`pipelineIds` is empty. That emptiness is itself meaningful: it means "this
node documents an architectural placeholder," not "this was overlooked."

## Pipeline order and grouping

18 conceptual stages, grouped into five domains (`SystemMapGroup`):

| Group | Stages |
|---|---|
| Physical Layer | Sample, Sensor System, Signal Acquisition |
| Data / ML Layer | Preprocessing, Feature Extraction, Drift Analysis, Machine Learning, Calibration, Explainability |
| Edge Layer | Compression/Quantization, TinyML Artifact, nRF52840 Deployment, Edge Prediction |
| Operations Layer | Gateway/Telemetry, Monitoring, Adaptation/Retraining |
| Research Layer | Experiment Registry, Evidence Ledger |

Note: "Adaptation / Retraining" here means a *live production* retraining
loop — it does not exist. This is explicitly distinguished in its
`statusNote` from the `EXPANDING_WINDOW` protocol (an already-*executed*
**offline research evaluation** of periodic retraining, see `/methodology`)
so the two "adaptation" concepts in this codebase are never conflated.

## Research status vs. UI/software status (mandatory distinction)

The field is named `researchStatus`, not `status`, specifically so it cannot
be misread as "this UI feature is implemented." A node's presence on this map
means the stage is *documented* — it does not mean the stage's underlying
function is implemented or executed. The page carries a standing banner
saying this explicitly, rather than adding a second per-node `uiStatus` field
to the evidence model (the evidence model itself — `lib/evidence.ts`,
`lib/types.ts` — is left untouched by this page).

## Dependency graph

Every node's `dependencies: string[]` lists other node ids it requires. The
build function throws at build time if any dependency id doesn't match a real
node id in the same registry — a dangling dependency cannot silently ship.
The inspector (`SystemMapInspector.tsx`) renders both directions: "Depends on"
(what this node needs) and "Required by" (what would be blocked if this node
isn't ready) — this is how the map explains, for example, why "Edge
Prediction" is `BLOCKED`: it depends on "nRF52840 Deployment," which is
`BLOCKED_HARDWARE`.

## Interaction and evidence integration

- Clicking a node (in the grouped graph or the always-rendered text list)
  opens `SystemMapInspector`, showing stage number, group, research status,
  description, role, inputs, outputs, algorithms, dependencies/dependents,
  evidence links (via the existing `ArtifactLink` component), related
  models/experiments, and limitations.
- Status badges reuse `EvidenceBadge` unchanged — the exact same status
  vocabulary and colors as every other page.
- Evidence links use `ArtifactLink`, so they resolve to the exact GitHub blob
  at the commit evidence was exported from, identical to every other page.

## Deep linking

`?stage=<id>` (e.g. `/system-map?stage=drift-analysis`) pre-selects a node.
Unlike the digital-twin pages, this value is read **server-side** from the
page's `searchParams` prop rather than via the `useSearchParams()` hook — a
deliberate choice: `useSearchParams()` forces Next.js to bail the whole
subtree out to client-side-only rendering unless wrapped carefully, which
would have made this plain-HTML page depend on JavaScript for its initial
content for no real benefit (there is no WebGL dependency here to justify
that cost, unlike `/digital-twin`). Reading `searchParams` server-side instead
makes `/system-map` a dynamically-rendered (not statically prerendered) route,
which is the correct and minimal trade for genuine deep-linking.

## What this page intentionally does not do

- It does not fabricate line-routed SVG edges between arbitrarily positioned
  nodes. Cross-column relationships are carried by the dependency chips in the
  inspector, which stay legible at any viewport width without custom
  line-layout code.
- It does not duplicate `/pipeline`'s raw 23-stage table — that page remains
  the authoritative one-row-per-pipeline-stage view; this page is the
  higher-level, grouped, dependency-aware companion.
