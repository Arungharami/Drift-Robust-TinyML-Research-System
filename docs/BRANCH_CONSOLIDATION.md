# Branch consolidation record

## Scope

This record documents the manual resolution used to consolidate
`codex/colab-research-system` with `main` after GitHub reported the direct integration pull
request as unmergeable.

Common ancestor: `e94856bfd73acfb413e6b379351e99d5d4523fdc`.

At the audit point, the research branch was 25 commits ahead and 15 commits behind `main`.
Only 14 paths had been changed independently on `main`; the large PR size came primarily from
research code, tests, configurations, and saved artifacts absent from the default branch.

## Resolution policy

The research branch is the content base because it contains the executable system and the
coherent multi-page evidence portal. Main-branch content is retained where it adds a compatible
capability. Earlier static portal files are superseded rather than mixed into the evidence
pipeline.

| Path | Resolution |
|---|---|
| `.github/workflows/research-portal-ci.yml` | Merged: locked install, typecheck, lint, build, read-only permissions, timeout, and main/PR triggers. |
| `.gitignore` | Merged union: research artifacts, secrets, Python, portal, LaTeX, and final-paper exception. |
| `README.md` | Research version retained; it contains the executable-system overview and agent guardrails. |
| `paper/README.md` | Main-only manuscript workflow retained. |
| `research-portal/README.md` | Reconciled around the artifact-driven multi-page portal; deployment and advisor workflow retained. |
| `research-portal/app/api/project-status/route.ts` | Research version retained because it reads exported evidence instead of static constants. |
| `research-portal/app/globals.css` | Research version retained because it styles the active multi-page component system. |
| `research-portal/app/layout.tsx` | Research version retained, including shared header/footer and metadata. |
| `research-portal/app/page.tsx` | Research evidence-driven home page retained; earlier single-page portal superseded. |
| `research-portal/lib/research.ts` | Main-only static data module intentionally omitted; `lib/evidence.ts` is authoritative. |
| `research-portal/next-env.d.ts` | Main-only Next.js type declaration retained. |
| `research-portal/next.config.ts` | Intentionally omitted because the research portal already owns `next.config.mjs`; keeping both is ambiguous. |
| `research-portal/package.json` | Research version retained for typecheck, lint, Recharts, and the current application dependency set. |
| `research-portal/tsconfig.json` | Research strict configuration retained (`noUncheckedIndexedAccess` and casing checks included). |

## Scientific invariants

- `configs/pipeline_stages.yaml` remains the authoritative stage registry.
- No model, metric, artifact, claim-evidence verdict, or stage status was changed by consolidation.
- No physical nRF52840 or PPK2 state was promoted.
- Portal values continue to come only from generated evidence JSON.
- Superseded files remain recoverable from Git history.

## Required validation

The integration PR must run both repository CI and Research Portal CI. Merge is permitted only
if GitHub reports the integration branch mergeable and both workflows pass.
