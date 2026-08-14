// Central evidence loader. This is the ONLY module in the web app that reads
// research-portal/data/evidence/*.json. Every page/component/API route imports typed
// accessors from here — never a raw JSON path, never a hand-typed number.
//
// data/evidence/*.json is generated exclusively by scripts/portal/export_evidence.py from
// real repository artifacts (results/, artifacts/, configs/, paper/). If a value is missing
// upstream, it is missing here too — this module never fills a gap with a guess.

import datasetJson from "@/data/evidence/dataset.json";
import experimentsJson from "@/data/evidence/experiments.json";
import baselinesJson from "@/data/evidence/baselines.json";
import driftJson from "@/data/evidence/drift.json";
import claimsJson from "@/data/evidence/claims.json";
import referencesJson from "@/data/evidence/references.json";
import xaiJson from "@/data/evidence/xai.json";
import pipelineJson from "@/data/evidence/pipeline.json";
import figuresJson from "@/data/evidence/figures.json";
import tablesJson from "@/data/evidence/tables.json";
import platformJson from "@/data/evidence/platform.json";
import environmentJson from "@/data/evidence/environment.json";
import projectStatusJson from "@/data/evidence/project-status.json";

import type {
  BaselinesEvidence,
  ClaimRecord,
  DatasetEvidence,
  DriftEvidence,
  EnvironmentEvidence,
  ExperimentRecord,
  FigureRecord,
  PipelineStage,
  PlatformEvidence,
  ProjectStatus,
  TableRecord,
  XaiEvidence,
} from "./types";

export function getDataset(): DatasetEvidence {
  return datasetJson as DatasetEvidence;
}

export function getExperiments(): ExperimentRecord[] {
  return experimentsJson as unknown as ExperimentRecord[];
}

export function getBaselines(): BaselinesEvidence {
  return baselinesJson as unknown as BaselinesEvidence;
}

export function getDrift(): DriftEvidence {
  return driftJson as unknown as DriftEvidence;
}

export function getClaims(): ClaimRecord[] {
  return claimsJson as unknown as ClaimRecord[];
}

export function getReferences(): import("@/components/ReferenceCard").Reference[] {
  return referencesJson as unknown as import("@/components/ReferenceCard").Reference[];
}

export function getXai(): XaiEvidence {
  return xaiJson as unknown as XaiEvidence;
}

export function getPipeline(): PipelineStage[] {
  return pipelineJson as unknown as PipelineStage[];
}

export function getFigures(): FigureRecord[] {
  return figuresJson as unknown as FigureRecord[];
}

export function getTables(): TableRecord[] {
  return tablesJson as unknown as TableRecord[];
}

export function getPlatform(): PlatformEvidence {
  return platformJson as unknown as PlatformEvidence;
}

export function getEnvironment(): EnvironmentEvidence | null {
  return environmentJson as unknown as EnvironmentEvidence | null;
}

export function getProjectStatus(): ProjectStatus {
  return projectStatusJson as unknown as ProjectStatus;
}

/** GitHub blob URL for a repo-relative artifact path, at the exact commit evidence was generated from. */
export function githubBlobUrl(relativePath: string, commit?: string): string {
  const repo = process.env.NEXT_PUBLIC_GITHUB_REPO ?? "Arungharami/Drift-Robust-TinyML-Research-System";
  const ref = commit ?? getProjectStatus().git_commit;
  return `https://github.com/${repo}/blob/${ref}/${relativePath}`;
}

/** Raw-content GitHub URL (for embedding committed figures) at the exact evidence-export commit. */
export function githubRawUrl(relativePath: string, commit?: string): string {
  const repo = process.env.NEXT_PUBLIC_GITHUB_REPO ?? "Arungharami/Drift-Robust-TinyML-Research-System";
  const ref = commit ?? getProjectStatus().git_commit;
  return `https://raw.githubusercontent.com/${repo}/${ref}/${relativePath}`;
}

export function formatNumber(value: string | number | null | undefined, digits = 3): string {
  if (value === null || value === undefined || value === "") return "NOT EXECUTED";
  const n = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(n)) return String(value);
  return n.toFixed(digits);
}

export function formatPercent(value: string | number | null | undefined, digits = 1): string {
  if (value === null || value === undefined || value === "") return "NOT EXECUTED";
  const n = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(n)) return String(value);
  return `${(n * 100).toFixed(digits)}%`;
}
