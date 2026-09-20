# Process View (`/process`)

## What this is

An interactive, evidence-driven "how does this system work" page. It groups the pipeline
registry (`configs/pipeline_stages.yaml`, exported through
`research-portal/data/evidence/pipeline.json`) into six human-scale phases — Data Foundation,
Classical Chronological ML, Explainability (XAI), Embedded Export, Hardware Deployment, and
Publication — and renders them as an interactive 3D scene (falling back to an accessible list)
so a new visitor can understand the shape of the project in under a minute, then drill into
`/pipeline` for full per-stage detail.

## What it is not

It introduces no new evidence, measurement, or claim. It is a navigational and explanatory layer
over data that already exists and is already displayed, stage-by-stage, on `/pipeline`. Every
value a visitor sees on `/process` — status, dependency, artifact link — is the same value shown
on `/pipeline`, only grouped and visualized differently. It does not depict physical hardware;
device imagery is tracked separately (see "Deliberately out of scope" below).

## Source of truth

- `research-portal/lib/process-phases.ts` defines the six-phase grouping (`PHASE_DEFINITIONS`, a
  hand-authored list of stage IDs per phase) and `buildProcessPhases()`, the only function that
  turns `PipelineStage[]` (from `lib/evidence.ts` → `getPipeline()`) into phase view-models.
- Phase status counts and cross-phase dependency edges are *computed* from real per-stage
  `status` and `depends_on` fields — never hand-declared. If `configs/pipeline_stages.yaml` adds,
  removes, or renames a stage without a matching update to `PHASE_DEFINITIONS`,
  `buildProcessPhases()` throws at build time (`npm run build`) rather than silently
  misrepresenting the pipeline. This is intentionally a hard build failure, not a lint warning.

## Rendering strategy

- `app/process/page.tsx` is a server component: it calls `getPipeline()` / `buildProcessPhases()`
  server-side and passes plain, serializable phase data to the client.
- `components/process/ProcessExplorer.tsx` (`"use client"`) owns view-mode state (3D vs. list),
  detects WebGL support and `prefers-reduced-motion` on mount, and renders the shared detail
  panel. It defaults to the accessible list view for SSR/first paint and upgrades to 3D only
  after confirming WebGL support client-side, avoiding a hydration flash.
- `components/process/ProcessScene.tsx` is a plain `three.js` scene (WebGLRenderer, OrbitControls,
  a Raycaster for clicks, plain-DOM label overlays projected from 3D each frame), loaded only via
  `next/dynamic(..., { ssr: false })` so its ~180kB chunk is isolated to this one route and never
  touches other pages' first-load JS. **`@react-three/fiber`/`@react-three/drei` were tried first
  and dropped**: fiber v8's pinned `react-reconciler@0.27.0` throws
  `Cannot read properties of undefined (reading 'ReactCurrentBatchConfig')` against this repo's
  `react@18.3.1` (confirmed with a single, deduped React copy in the tree — not a duplicate-React
  issue, a real upstream incompatibility). Downgrading React to work around a nice-to-have visual
  was out of scope, so the scene is driven imperatively instead — no reconciler involved, fewer
  dependencies, and a smaller shipped bundle. It uses only procedural geometry — no remote
  textures, fonts, or models are fetched at runtime, so the scene has no external network
  dependency and nothing to fail silently if a CDN is slow or blocked.
- `components/process/ProcessSceneBoundary.tsx` is a minimal error boundary: if the 3D scene
  throws for any reason (driver quirk, context loss), it falls back to the list view rather than
  breaking the page.
- `components/process/ProcessListView.tsx` is the fallback — and manually selectable — accessible
  view: real `<button>` elements, fully keyboard-operable, identical `onSelect` contract to the
  3D scene, so switching modes never loses selection state.
- Node/edge colors reuse the same `--status-*` design tokens as the rest of the site
  (`app/globals.css`), resolved per-theme via a `MutationObserver` on `<html data-theme>` so the
  scene follows the existing light/dark toggle without any change to `ThemeToggle.tsx`.

## Cross-navigation added elsewhere

- `/pipeline` now derives its heading count from `stages.length` instead of a hardcoded number
  (it had drifted to say "23-stage" against an actual 27-stage registry) and links to `/process`.
- `components/PipelineStage.tsx` cards now carry a stable `id="stage-{id}"` anchor so `/process`
  can deep-link a specific stage.
- `/` (home) gains a link to `/process` as the suggested first stop for a new visitor.
- `lib/nav.ts` adds a "How It Works" entry.

## Deliberately out of scope here

- Device imagery for the physical sensor array (no physical unit exists yet — see `/hardware`
  and `docs/NEXT_LEVEL_RESEARCH_AUDIT.md`).
- A written "how to build this for ML" methodology guide.
- Any change to `/pipeline`'s per-stage content beyond the anchor IDs and the corrected count.

Both are natural follow-ups once this view is reviewed.
