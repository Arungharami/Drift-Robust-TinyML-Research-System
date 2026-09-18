// Shared types for the digital-twin scene. Every TwinComponent's `status` is
// sourced from research-portal/lib/evidence.ts — never hand-typed here — so
// the 3D view can never drift out of sync with the evidence-driven pages.

import type { EvidenceStatus } from "@/lib/types";

export type TwinGroup = "sensor" | "edge" | "gateway" | "cloud";

/** Broad category used by the device view and system map — not read by the original /digital-twin scene. */
export type SystemCategory =
  | "physical"
  | "sensor"
  | "signal"
  | "ml"
  | "xai"
  | "tinyml"
  | "deployment"
  | "gateway"
  | "evidence";

export interface EvidenceLink {
  label: string;
  path: string;
}

export interface TwinComponent {
  id: string;
  name: string;
  group: TwinGroup;
  /** Base [x, y, z] position along the signal-flow axis, before exploded-view spacing. */
  position: [number, number, number];
  role: string;
  input: string;
  output: string;
  status: EvidenceStatus | string;
  statusNote?: string;
  evidenceLinks: EvidenceLink[];
  /** Portal page with the full evidence for this component, if one exists. */
  portalHref?: string;

  // --- Optional Phase-C metadata below. The original 8 /digital-twin components never set
  // these fields, so ComponentInspector's rendering of them is a strict no-op there — this
  // extension cannot change /digital-twin's existing output. Used by /digital-twin/device.
  /** Broader classification shown as a chip in the inspector. */
  category?: SystemCategory;
  /** Why this stage exists in the research design, distinct from its mechanical `role`. */
  researchPurpose?: string;
  /** Physical-execution status, kept separate from `status` (implementation status) per the
   * project's research-vs-hardware distinction — e.g. status=NOT_EXECUTED (firmware not built)
   * while hardwareStatus=BLOCKED_HARDWARE (no board detected). Omit when the distinction doesn't apply. */
  hardwareStatus?: EvidenceStatus | string;
  relatedModels?: string[];
  relatedExperiments?: string[];
  limitations?: string[];
}
