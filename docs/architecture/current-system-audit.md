# Current System Audit

Date: 2026-09-17
Scope: Full-repository audit ahead of the proposed "DriftTwin AI Lab" digital-twin
redesign. This document is descriptive only — it records what exists today so that
later phases do not destroy, duplicate, or misrepresent working research
infrastructure. No code was changed to produce this document.

---

## 1. What this project actually is

This is a **publication-track research codebase**, not a product prototype. It
studies chronological sensor drift on the UCI Gas Sensor Array Drift dataset,
with a target (not yet realized) edge deployment on a Nordic nRF52840. The
central research question — whether resource-aware, drift-robust ML +
explainability can survive TinyML constraints on real hardware — is explicitly
**unanswered** in the repo's own words.

The project enforces a strict, actively-tested **evidence-honesty discipline**:
no number is shown anywhere (Python results, tests, or the web portal) unless an
executed artifact produced it. This is not a style preference; it's load-bearing
for the thesis and is enforced by tests (`tests/test_hardware_portal.py`,
`tests/test_stage15_hardware_gate.py`) that fail the build if a page ever shows a
fabricated hardware number or silently drops a `NOT_MEASURED` state.

**Any redesign must preserve this discipline exactly.** The master prompt's
requirements in this area (Sections 2, 40) are not new asks — they describe a
system that already exists and is already tested.

---

## 2. Current architecture

### 2.1 Research pipeline (Python, `src/`, `scripts/`, `configs/`, `results/`)

A 23-stage pipeline (Stage 00–22), authoritatively tracked in
`configs/pipeline_stages.yaml`. Status per stage:

| Stages | Area | Status |
|---|---|---|
| 00–08 | Env capture, dataset download/validation, chronological split, classical baselines (4 models: LR/RF/SVM-RBF/MLP), drift analysis (Wasserstein + standardized mean shift), evidence-based model selection | **EXECUTED**, real result CSVs in `results/` |
| 09 | Resource-aware XAI (permutation importance, intrinsic coefficients/impurity, custom single-feature ablation — deliberately **not** SHAP/LIME) | **EXECUTED** |
| 10 | Explanation fidelity | **EXECUTED**, outcome mixed/unsupported |
| 11 | Explanation stability | **EXECUTED**, outcome mixed |
| 12 | Host-side XAI computational cost | **EXECUTED** (explicitly not an MCU latency claim) |
| 13 | Embedded export/equivalence protocol freeze | `PROTOCOL_FROZEN` (gate, not an experiment) |
| 14 | Standalone FP32 C export equivalence (host-compiled via Zig cc, x86-64) | **FAILED** (real negative result) |
| 14R | C1 preprocessing repair attempt | **FAILED** |
| 14F-GATE/EXEC/XAI | "Fused" preprocessing architecture (host-only) | **PASSED** (host-only) |
| 15 | nRF52840 deployment | **BLOCKED_HARDWARE** — no board/debug probe ever detected |
| 16–20 | Flash/SRAM, physical latency, PPK2 energy, Pareto | **BLOCKED**, no script exists yet |
| 21 | Figures/tables | **EXECUTED** (131 figure files, 18 table files) |
| 22 | Manuscript evidence export | **RUNNING** (deliberately no Results/Discussion prose yet) |

Real, tested, non-stub code exists for: dataset loading/validation/chronology
(`src/data/`), drift metrics (`src/drift/`, only Wasserstein + standardized mean
shift — no PSI/KS/ADWIN/DDM), classical models (`src/models/classical.py` — no
teacher/student, no distillation, no quantization code anywhere), XAI
(`src/xai/`, extensive, well-tested), and host-side C export/equivalence
(`src/embedded/`, real generated C + host-compiled `.exe` binaries via Zig cc —
**never cross-compiled or run on an MCU**).

197 pytest tests collect cleanly across 24 files. `results/` contains 302 real,
populated evidence files, not scaffolding.

### 2.2 Evidence ledger (already exists — do not rebuild from scratch)

The single most important finding for the redesign: **Section 20 of the master
prompt ("Research Evidence Ledger") already exists and is mature.**

- `paper/claim_evidence_matrix.csv` — every manuscript claim → experiment ID →
  dataset/split/config hashes → git commit → result artifact → figure → status
  (`SUPPORTED`/`UNSUPPORTED`/`UNRESOLVED`).
- `research/hypotheses.yaml`, `research/questions.yaml`,
  `research/acceptance_criteria.yaml` — H1–H10 / RQ1–RQ10 / AC1–AC10, each with
  explicit status and links.
- `results/registry/{experiments,artifacts,claims,measurements}.csv` —
  normalized evidence tables.
- `scripts/portal/export_evidence.py` — the **only** bridge from Python results
  to the web portal; "never estimates, interpolates, or invents a number."
- `scripts/validate_research_evidence.py` — CI-enforced integrity checker
  (orphan links, hash mismatches, invalid states).
- Standardized status vocabulary used consistently everywhere: `MEASURED,
  DERIVED, EXECUTED, PLANNED, BLOCKED, FAILED, NOT_APPLICABLE` (public) plus
  internal `NOT_EXECUTED, RUNNING, INVALID, SUPERSEDED, BLOCKED_HARDWARE,
  BLOCKED_CREDENTIALS, BLOCKED_CONFIGURATION`.

This is exactly the "status engine" the master prompt asks for in Section 50 —
already implemented, one level lower (Python + generated JSON) than the master
prompt assumed (it does not exist as a TypeScript runtime engine; see 2.3).

### 2.3 Web portal (`research-portal/`, Next.js 15 App Router, deployed to Vercel)

- Stack: Next.js 15, React 18, TypeScript (strict), Recharts for charts, one
  hand-written CSS stylesheet (light/dark via `data-theme`). **No Tailwind, no
  UI kit, no 3D library (no three.js/R3F) anywhere.**
- 24 real routes, all either fully populated from evidence or an honest
  `PLANNED`/`BLOCKED` state — no Lorem-ipsum stubs. Notable existing pages that
  overlap heavily with master-prompt asks: `/pipeline` (→ Section 8 system map),
  `/experiments` (→ Section 19 registry), `/xai` (→ Section 16
  explainability), `/hardware` + `/tinyml` (→ Sections 7/12/27 hardware/edge),
  `/professor-review` (→ Section 32), `/paper` (→ Section 33), `/reproducibility`
  (→ Section 25).
- `lib/evidence.ts` is documented as **the only module allowed to read
  `data/evidence/*.json`** — a strong, already-enforced architecture boundary.
  `lib/types.ts` defines the `EvidenceStatus` union type used everywhere.
  **Preserve this pattern** rather than introducing a parallel data path.
  There is no client-side "enforcement engine" — enforcement is upstream in
  Python; the frontend just renders the status string it's given.
  `/embedded` is a one-line re-export alias of `/tinyml` (legacy, needs a
  decision: keep/redirect/remove).
- Professor-review collaboration (Supabase): schema fully designed
  (`supabase/migrations/20260814_professor_review_collaboration.sql`, RLS
  policies, invite/moderation tables) and a detailed enablement doc
  (`docs/PROFESSOR_REVIEW_COLLABORATION_SETUP.md`) exist, but it is **not wired
  up** — no Supabase SDK dependency, `COLLABORATION_FEATURE_STATE=disabled` by
  default, `/api/professor-review` POST always returns 503/501,
  `/professor-review/admin` deliberately 404s pending an auth guard. This is
  designed-but-unbuilt groundwork, not broken code.
- No frontend test runner exists (no Jest/Vitest/Playwright). Frontend
  correctness is currently asserted from Python (`tests/test_hardware_portal.py`,
  `tests/test_portal_registry_consistency.py`) by grepping generated
  page/component source for required strings — unusual but deliberate and
  effective for the evidence-honesty invariant.
- Two `.env.example` files (repo root vs. `research-portal/`) are out of sync;
  the portal-local one is missing the four collaboration vars that
  `lib/collaboration.ts` actually reads.

### 2.4 What does NOT exist yet (confirmed, not assumed)

- No 3D of any kind (no three.js/R3F/WebGL) — Sections 5–7 of the master prompt
  are 100% net-new frontend work.
- No teacher/student model architecture, no knowledge distillation, no
  quantization code (Section 15) — models are 4 classical scikit-learn
  pipelines only.
- No PSI/KS-test/ADWIN/DDM drift detectors (Section 14 partially net-new) —
  only Wasserstein distance and standardized mean shift, both univariate.
- No SHAP (Section 16 mentions it) — deliberately excluded by design
  (`docs/experiments/STAGE09_RESOURCE_AWARE_XAI.md` states the SHAP/LIME
  policy). Any redesign copy must not imply SHAP is used.
- No real nRF52840 firmware, no Zephyr project, no flashed binary, no physical
  measurement of any kind (Flash/SRAM/latency/energy) — Sections 26–27 hardware
  work is entirely blocked pending a physical board. `configs/
  nrf52840_resource_budget.yaml` values are all `TBD_BEFORE_COMPILE`, not
  measurements.
- No device telemetry adapters (Web Serial/BLE), no live-lab dashboard, no
  recorded-replay mode — Sections 9–12, 46–49 are net-new.
- No Python CLI entry points (`pyproject.toml` defines no `console_scripts`) —
  everything is invoked as `python scripts/<name>.py`. Section 23's `drifttinyml
  train ...`-style CLI does not exist yet.
- No frontend automated tests.

---

## 3. Scientific limitations (stated plainly, per repo's own policy)

- XAI fidelity/stability results (Stage 10/11) are executed but predominantly
  **unsupported or mixed** — this is a real, currently negative/inconclusive
  result central to the professor-review narrative, not a gap to hide.
- Embedded FP32 export equivalence **failed twice** (Stage 14, 14R) before a
  "fused preprocessing" variant passed on host only (14F). No claim of MCU
  readiness exists or should be implied.
- Hardware stage (15+) is 100% blocked — no board has ever been detected.
  Every downstream metric (Flash, SRAM, latency, energy, Pareto) is
  `NOT_MEASURED`/`BLOCKED`, by design, not oversight.
- Small-sample statistics (n=9 batches) are explicitly flagged as
  underpowered for inferential claims (`src/evaluation/statistics.py`,
  `docs/STATISTICAL_ANALYSIS_PLAN.md`) — descriptive only at this stage.
- The root `README.md` architecture-diagram prose is stale (says Stage 09 is
  the last executed stage; Stages 10–12 have since executed). Minor
  single-source-of-truth inconsistency worth fixing.

---

## 4. Hardware blockers

Confirmed via `results/embedded/stage15_hardware_detection.json`
(captured 2026-08-12): no physical nRF52840 board or debug probe has ever been
detected on the development machine. `board_identity:
"UNRESOLVED_NO_SUPPORTED_DEVICE_DETECTED"`. This blocks Stages 15–20 entirely
(physical golden-vector validation, Flash/SRAM measurement, physical latency,
PPK2 energy measurement, Pareto analysis) and therefore blocks any Section
26–27 firmware work from producing real measurements. The architecture for
firmware/export exists conceptually (Stage 13 protocol, Stage 14/14F export
code); what's missing is exclusively **physical access to a board and probe**.

---

## 5. Proposed migration plan (high-level — detailed per-phase plans to follow)

Given the scope of the master prompt (a full product-identity change, a 3D
digital twin, a device-adapter architecture, a Python CLI/package
reorganization, and a database layer), and given that this repository is a live
academic research system with hard-won scientific-integrity guarantees, the
migration should be **additive and layered**, not a rewrite:

1. **Do not touch** `src/`, `scripts/`, `configs/`, `results/`, `paper/`,
   `research/`, the evidence-export pipeline, or the test suite's assertions
   about evidence honesty, except to fix the one stale README paragraph and the
   `.env.example` drift noted above.
2. **Extend, don't replace**, `research-portal/`: keep `lib/evidence.ts` /
   `lib/types.ts` / `data/evidence/*.json` as the single source of truth; add
   new pages/components (3D digital twin, system map, experiment-mode provider,
   device adapters) as new modules that consume the existing evidence loader
   rather than a new data path.
3. Treat the master prompt's "Evidence Ledger" (Section 20), "Model/Experiment
   Registry" (Sections 18–19), and "Status Engine" (Section 50) as **UI/frontend
   views over the already-existing Python-side ledger**, not new systems to
   design from scratch.
4. Any new visual "product identity" (DriftTwin AI Lab branding, 3D twin,
   simulation/recorded/live modes) must not soften or obscure the existing
   BLOCKED_HARDWARE / NOT_MEASURED discipline — new UI surfaces inherit the same
   test-enforced honesty constraints as `/hardware` today.
5. Given the true scope of Sections 3–54, this needs to proceed in the
   explicitly sequential phases the master prompt itself defines (Phase B
   onward), each phase reviewed and reported before starting the next, rather
   than attempted as one pass.

---

## 6. Files referenced in this audit

See the three source audits this document was synthesized from (frontend,
Python/ML, docs/evidence/CI) for exact file paths per subsystem; key anchors:

- `configs/pipeline_stages.yaml` — master stage/status registry
- `paper/claim_evidence_matrix.csv`, `research/{hypotheses,questions,
  acceptance_criteria}.yaml` — evidence ledger
- `scripts/portal/export_evidence.py`, `scripts/validate_research_evidence.py`
- `research-portal/lib/evidence.ts`, `research-portal/lib/types.ts`,
  `research-portal/lib/nav.ts`
- `results/embedded/stage15_hardware_detection.json` — hardware-blocked proof
- `tests/test_hardware_portal.py`, `tests/test_stage15_hardware_gate.py` —
  evidence-honesty enforcement
- `AGENTS.md` — repo's own contributor/agent constitution (read this before any
  future work session in this repo)
