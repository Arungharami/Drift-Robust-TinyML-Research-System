# Vercel Deployment

## Production

- Domain: `https://drift-robust-tinyml-research.vercel.app`
- Vercel project: `drift-robust-tinyml-research` (team `Arun's projects` / `aruns-projects-ba93fc58`)
- Production branch: `main`
- Framework: Next.js (App Router)
- App location: `research-portal/` — this is a monorepo; the Next.js app is **not** at the repo root.

## Dashboard configuration status (as of 2026-09-20, re-verified)

The Vercel project's dashboard settings, confirmed via `vercel project
inspect drift-robust-tinyml-research`:

- Framework Preset: **`Next.js`** — fixed manually since this doc was first written.
- Root Directory: **`.`** (repo root) — **still wrong, still needs to be `research-portal`.**

Fixing only the Framework Preset was not sufficient: a git-triggered deploy
still builds from the repo root, where there is no Next.js app (the real one
is at `research-portal/`), so **automatic git-push deploys still do not
work** — confirmed by checking `vercel ls` immediately after merging a PR to
`main`: no new deployment was triggered.

**The Vercel CLI cannot change Root Directory** — `vercel project` only
supports `add`/`inspect`/`list`/`remove`/`token`; it is a dashboard/API-only
field.

### The one remaining manual step

Someone with dashboard access must, once, go to:

**Vercel Dashboard → `drift-robust-tinyml-research` → Settings → General**

- **Root Directory** → Edit → `research-portal` → Save

(Framework Preset is already correctly set to `Next.js` — nothing to do there.)

After this one-time fix, every future `git push`/merge to `main` will deploy
correctly on its own — no more manual CLI workaround needed.

## Manual deploy workaround (used until the setting above is fixed)

From `research-portal/`, with the Vercel CLI authenticated and linked
(`vercel link --project drift-robust-tinyml-research`):

```bash
# Preview
vercel pull --yes --environment preview
vercel build
vercel deploy --prebuilt

# Production (only after the preview above has been checked)
vercel pull --yes --environment production
vercel build --prod
vercel deploy --prebuilt --prod
```

This works because running the CLI directly from `research-portal/` sidesteps
the dashboard's incorrect Root Directory — the build starts from the correct
directory regardless of what the dashboard says.

## Rollback

```bash
vercel rollback --yes
# or promote a specific known-good deployment:
vercel promote <deployment-url-or-id>
```

Vercel keeps every previous production deployment; rolling back does not
require a new build.

## Common failures and their real cause

| Symptom | Real cause |
|---|---|
| `No Output Directory named 'public' found` | Root Directory misconfigured (repo root instead of `research-portal`) — see above. |
| Live site shows stale/old content despite recent merges to `main` | Same root cause: normal git-triggered deploys have been silently failing, so the last *successful* deploy (however it was actually produced) is what's still live. |
| `next build` succeeds locally but a PR's browser test still shows a crash | Build/typecheck only check static shape; a runtime mounting crash (e.g. a react-reconciler/React-version mismatch) only shows up when the page is actually loaded in a browser. Always verify with a real (even headless) browser before trusting a green build — see `research-portal/components/process/ProcessScene.tsx`'s doc comment for a specific example of this exact failure mode. |

## Three.js runtime verification

`/digital-twin`, `/digital-twin/device`, and `/process` each render a WebGL
scene client-side only (`next/dynamic(..., { ssr: false })`), using plain
imperative `three.js` (`WebGLRenderer`, `OrbitControls`, `Raycaster`,
`requestAnimationFrame`) — **not** `@react-three/fiber`/`@react-three/drei`,
which are deliberately absent from `research-portal/package.json`
(`react-reconciler@0.27.0` crashes on mount against this project's
`react@18.3.1`). Before merging any change under
`research-portal/components/digital-twin/` or
`research-portal/components/process/`, verify in a real browser — build and
typecheck passing is not sufficient:

```bash
cd research-portal && npm run build && npm run start -- -p 4180
# separately, with Playwright (headless Chromium):
# npx playwright install chromium   (once)
# launch with: --use-gl=angle --use-angle=swiftshader --ignore-gpu-blocklist
# check: canvas count > 0, zero console errors, zero page errors,
#        no "ReactCurrentBatchConfig" in any error
```

## Site URL (metadata, robots, sitemap)

`NEXT_PUBLIC_SITE_URL` is now set as a real Vercel production environment
variable (`https://drift-robust-tinyml-research.vercel.app`). Its in-code
fallback in `app/layout.tsx`, `app/robots.ts`, and `app/sitemap.ts` was also
corrected — all three previously fell back to a stale, incorrect hostname
(`drift-robust-tinyml.vercel.app`, missing `-research`) whenever the env var
wasn't set, which it never was. This silently pointed `metadataBase` (so
every page's Open Graph/canonical URLs), `robots.txt`'s sitemap reference,
and every `sitemap.xml` entry at the wrong domain. Confirmed live before the
fix: `curl https://drift-robust-tinyml-research.vercel.app/sitemap.xml`
returned `<loc>` entries under the wrong hostname.

## Asset locations

- 3D concept-art images (AI-generated, explicitly not physical evidence):
  `research-portal/public/3d/`, shown on `/digital-twin/gallery`.
- Scientific evidence JSON (generated, never hand-edited): `research-portal/data/evidence/*.json`.

## Scientific evidence rules (unchanged by any deployment work)

Deployment and infrastructure changes must never alter what the portal
reports as measured, executed, blocked, or planned. See the repository's
`AGENTS.md` for the full evidence policy. In particular:

- Hardware statuses (`BLOCKED_HARDWARE`, `NOT_MEASURED`, `NOT_EXECUTED`) are
  read from `research-portal/lib/evidence.ts` and must never be edited to
  "make the site look better."
- Concept-art images must keep their `CONCEPT VISUALS — NOT EXPERIMENTAL
  EVIDENCE` disclaimer.
