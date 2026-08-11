# research-portal

Evidence-driven research portal for **Drift-Robust Explainable TinyML for Electronic-Nose
Sensing**, built with Next.js (App Router, TypeScript).

## Architecture

This app never hand-types a research metric. The only bridge from real repository artifacts
(`results/`, `artifacts/`, `configs/`, `paper/`) to the UI is:

```
scripts/portal/export_evidence.py   (run from the repo root)
        |
        v
research-portal/data/evidence/*.json
        |
        v
research-portal/lib/evidence.ts     (typed accessors — the ONLY module that imports this JSON)
        |
        v
app/**/page.tsx, app/api/**/route.ts
```

If an artifact does not exist upstream, the corresponding evidence field is `null` and every
page renders `NOT EXECUTED` via `<EvidenceBadge>` — never a placeholder or estimated number.

## Local development

```bash
# from the repository root, regenerate evidence first:
python scripts/portal/export_evidence.py

cd research-portal
npm install
npm run dev        # http://localhost:3000
```

Other scripts: `npm run build`, `npm run start`, `npm run typecheck`, `npm run lint`.

## Deploying to Vercel

This app lives in a subdirectory, not the repository root:

1. In the Vercel project settings, set **Root Directory** to `research-portal`.
2. Framework preset: **Next.js** (auto-detected).
3. Build command / output: defaults (`next build`) are correct — do not override.
4. Environment variables: copy from `.env.example` into the Vercel project's environment
   variables. None of them are secret; all are `NEXT_PUBLIC_*` values used only for outbound
   links and metadata.
5. Confirm the Python-only parts of the parent repository (`src/`, `scripts/`, `notebooks/`)
   are **not** picked up as the deploy target — Root Directory scoping handles this
   automatically as long as it is set correctly.

## Regenerating evidence before a deploy

`research-portal/data/evidence/*.json` is committed (not `.gitignore`d) so that Vercel's build
does not need Python or access to the rest of the monorepo at build time. Whenever the
underlying research artifacts change, regenerate and commit:

```bash
python scripts/portal/export_evidence.py
git add research-portal/data/evidence
git commit -m "Refresh research portal evidence"
```

## Design notes

- No Tailwind/CSS framework — a small hand-written design-token system in `app/globals.css`,
  chosen deliberately to avoid a generic SaaS/marketing look for an academic research portal.
- Light/dark mode via CSS variables (`prefers-color-scheme` + a `data-theme` override toggled by
  `components/ThemeToggle.tsx`, persisted to `localStorage`).
- Charts: `recharts`, used only on `/results` where real CSV-derived series exist.
- Figures embed directly from `raw.githubusercontent.com` at the exact commit evidence was
  exported from, rather than duplicating binary figure files into this app.
