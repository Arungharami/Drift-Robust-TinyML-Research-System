# DeepSeek Harness workflow

This repository can be used as a DeepSeek Harness workspace. Harness should assist with bounded research-engineering tasks; it is not an authority that can certify scientific claims.

## Recommended entry point

Use a clean checkout based on `codex/colab-research-system` until the research branch is consolidated into `main`. On Windows PowerShell:

```powershell
git switch codex/colab-research-system
git pull
git switch -c agent/<bounded-task>
npx @deepseek-ai/dsh web
```

Open the URL printed by the command (normally `http://127.0.0.1:3080`), configure a model under **Settings → Models**, and choose this repository as the workspace. Run Harness from the repository root so its workspace context includes `AGENTS.md`.

DeepSeek Harness is a developer preview. Use a task branch, keep approval prompts enabled, and review every diff before committing.

## Session start

Begin every session with a read-only evidence audit:

```text
Read AGENTS.md first. Do not edit files yet.

Audit the requested pipeline stage against configs/pipeline_stages.yaml,
paper/claim_evidence_matrix.csv, the experiment registry, existing artifacts,
tests, and current Git state. Identify satisfied dependencies, missing evidence,
scientific risks, and one bounded next action. Never invent a metric or change
a status without an executed artifact.
```

Approve only one bounded implementation after reviewing the audit. A good execution prompt is:

```text
Implement only the approved bounded task. Preserve the chronological protocol
and evidence rules. Save configuration, seed, environment, logs, metrics, and
failure state. Run focused validation. Regenerate portal evidence only from
authoritative artifacts. Finish with the exact commands run, their outcomes,
artifact paths, unsupported claims, and a concise Git diff summary.
```

## Current evidence boundary

The authoritative status is `configs/pipeline_stages.yaml`. At the branch state where this guide was added:

- stages 00–09 are recorded as `EXECUTED`;
- stages 10–20 are recorded as `NOT_EXECUTED`;
- stage 21 is recorded as `EXECUTED`;
- stage 22 is recorded as `RUNNING`;
- physical nRF52840 and PPK2 results remain unavailable.

These bullets are orientation only. If the registry changes, regenerate derived evidence and update or remove this summary.

## Good first task

The next evidence-producing work should be chosen only after verifying dependencies and the actual branch state. Under the current registry, Stage 10 (explanation fidelity) is the first unexecuted stage whose declared dependency, Stage 09, is satisfied. The agent should first inspect `results/xai/stage09_fidelity_prep.csv`, the Stage 09 configuration and documentation, model artifacts, and tests; it must not assume the preparation artifact is correct merely because it exists.

## Completion checklist

A task is complete only when:

- the scientific or infrastructure objective is bounded and documented;
- required dependencies were available;
- source artifacts and hashes are preserved;
- relevant tests/checks ran, or the missing check is labeled `NOT_RUN`;
- pipeline status matches actual evidence;
- portal JSON was regenerated rather than hand-edited when applicable;
- manuscript and public text contain no unsupported claim;
- the final change is isolated in a draft pull request.
