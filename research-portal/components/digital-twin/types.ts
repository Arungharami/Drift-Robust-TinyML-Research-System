// Shared types for the digital-twin scene. Every TwinComponent's `status` is
// sourced from research-portal/lib/evidence.ts — never hand-typed here — so
// the 3D view can never drift out of sync with the evidence-driven pages.

import type { EvidenceStatus } from "@/lib/types";

export type TwinGroup = "sensor" | "edge" | "gateway" | "cloud";

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
}
