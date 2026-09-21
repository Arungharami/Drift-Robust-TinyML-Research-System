// Groups the real pipeline_stages registry (lib/evidence.ts -> getPipeline()) into a small
// number of human-scale "phases" for the /process visual explainer. This module invents no
// evidence: every field on a ProcessPhase is either (a) a hand-authored UI label/grouping of
// real stage IDs, verified below to cover the registry exactly once, or (b) computed directly
// from PipelineStage fields (status counts, dependency edges). If the upstream registry adds,
// removes, or renames a stage without a matching update here, buildProcessPhases() throws
// instead of silently drifting out of sync with configs/pipeline_stages.yaml.

import type { EvidenceStatus, PipelineStage } from "./types";

export interface ProcessPhaseDefinition {
  id: string;
  title: string;
  shortLabel: string;
  description: string;
  stageIds: string[];
}

// Hand-authored grouping of the pipeline registry into six human-scale phases, in pipeline
// order. Membership only — status, notes, artifacts, and dependencies below are all derived
// from real stage data, never asserted here.
const PHASE_DEFINITIONS: ProcessPhaseDefinition[] = [
  {
    id: "data",
    title: "Data Foundation",
    shortLabel: "Data",
    description: "Acquire, verify, and chronologically split the raw gas-sensor dataset.",
    stageIds: ["00", "01", "02", "03", "04"],
  },
  {
    id: "classical-ml",
    title: "Classical Chronological ML",
    shortLabel: "Baseline ML",
    description:
      "Train and evaluate baseline classifiers strictly forward in time, and quantify sensor drift.",
    stageIds: ["05", "06", "07", "08"],
  },
  {
    id: "xai",
    title: "Explainability (XAI)",
    shortLabel: "XAI",
    description:
      "Generate model explanations, then test their fidelity, stability, and host compute cost.",
    stageIds: ["09", "10", "11", "12"],
  },
  {
    id: "embedded-export",
    title: "Embedded Export",
    shortLabel: "Embed",
    description:
      "Freeze a numerical-equivalence protocol and attempt host-side FP32 export toward the MCU target.",
    stageIds: ["13", "14", "14R", "14F-GATE", "14F-EXEC", "14F-XAI", "14Q-GATE"],
  },
  {
    id: "hardware",
    title: "Hardware Deployment",
    shortLabel: "Hardware",
    description: "Flash, measure latency, and profile energy on the physical nRF52840 board.",
    stageIds: ["15", "16", "17", "18", "19", "20"],
  },
  {
    id: "publication",
    title: "Publication",
    shortLabel: "Publish",
    description: "Generate figures/tables and export claim-linked evidence into the manuscript.",
    stageIds: ["21", "22"],
  },
];

export interface ProcessPhase extends ProcessPhaseDefinition {
  order: number;
  stages: PipelineStage[];
  statusCounts: Partial<Record<EvidenceStatus, number>>;
  dominantStatus: EvidenceStatus;
  isFullyExecuted: boolean;
  hasFailure: boolean;
  hasBlocker: boolean;
  dependsOnPhaseIds: string[];
}

// Priority order used only to pick one representative badge color for a phase that mixes
// statuses. The underlying per-stage statuses (shown in the detail panel) are never collapsed.
const STATUS_PRIORITY: EvidenceStatus[] = [
  "FAILED",
  "BLOCKED",
  "BLOCKED_HARDWARE",
  "RUNNING",
  "NOT_MEASURED",
  "NOT_EXECUTED",
  "PLANNED",
  "PROTOCOL_FROZEN",
  "VALIDATED",
  "EXECUTED",
];

function dominantStatusOf(counts: Partial<Record<EvidenceStatus, number>>): EvidenceStatus {
  for (const status of STATUS_PRIORITY) {
    if ((counts[status] ?? 0) > 0) return status;
  }
  return "NOT_EXECUTED";
}

/** Builds the phase view model from the real pipeline registry. Throws if the registry and the
 * hand-authored grouping have drifted apart, so a future stage addition/rename/removal cannot
 * silently fall out of the visualization or double-count a stage. */
export function buildProcessPhases(stages: PipelineStage[]): ProcessPhase[] {
  const byId = new Map(stages.map((s) => [s.id, s]));
  const seen = new Set<string>();

  const phases: ProcessPhase[] = PHASE_DEFINITIONS.map((def, index) => {
    const memberStages: PipelineStage[] = def.stageIds.map((id) => {
      const stage = byId.get(id);
      if (!stage) {
        throw new Error(
          `process-phases: stage "${id}" listed in phase "${def.id}" does not exist in the ` +
            `pipeline registry. Update PHASE_DEFINITIONS in lib/process-phases.ts to match ` +
            `configs/pipeline_stages.yaml.`
        );
      }
      if (seen.has(id)) {
        throw new Error(`process-phases: stage "${id}" is assigned to more than one phase.`);
      }
      seen.add(id);
      return stage;
    });

    const statusCounts: Partial<Record<EvidenceStatus, number>> = {};
    for (const stage of memberStages) {
      statusCounts[stage.status] = (statusCounts[stage.status] ?? 0) + 1;
    }

    const dependsOnPhaseIds = new Set<string>();
    for (const stage of memberStages) {
      for (const depId of stage.depends_on) {
        if (def.stageIds.includes(depId)) continue; // internal dependency, not cross-phase
        const owningPhase = PHASE_DEFINITIONS.find((p) => p.stageIds.includes(depId));
        if (owningPhase && owningPhase.id !== def.id) dependsOnPhaseIds.add(owningPhase.id);
      }
    }

    return {
      ...def,
      order: index,
      stages: memberStages,
      statusCounts,
      dominantStatus: dominantStatusOf(statusCounts),
      isFullyExecuted: memberStages.every((s) => s.status === "EXECUTED" || s.status === "VALIDATED"),
      hasFailure: memberStages.some((s) => s.status === "FAILED"),
      hasBlocker: memberStages.some((s) => s.status === "BLOCKED" || s.status === "BLOCKED_HARDWARE"),
      dependsOnPhaseIds: Array.from(dependsOnPhaseIds),
    };
  });

  if (seen.size !== stages.length) {
    const missing = stages.map((s) => s.id).filter((id) => !seen.has(id));
    throw new Error(
      `process-phases: ${missing.length} pipeline stage(s) are not covered by any phase: ` +
        `${missing.join(", ")}. Update PHASE_DEFINITIONS in lib/process-phases.ts.`
    );
  }

  return phases;
}
