// Shared evidence types. Every value on screen traces back to one of these, which in turn
// traces back to research-portal/data/evidence/*.json, generated only by
// scripts/portal/export_evidence.py from real repository artifacts. Nothing here is fabricated.

export type EvidenceStatus =
  | "EXECUTED"
  | "VALIDATED"
  | "PLANNED"
  | "RUNNING"
  | "FAILED"
  | "BLOCKED"
  | "NOT_EXECUTED";

export interface PipelineStage {
  id: string;
  name: string;
  status: EvidenceStatus;
  notebook: string | null;
  script: string | null;
  artifact_paths: string[];
  git_commit: string | null;
  depends_on: string[];
  notes: string;
}

export interface ExperimentRecord {
  experiment_id: string;
  timestamp: string;
  research_question: string;
  protocol: string;
  model: string;
  representation: string;
  train_batches: string;
  validation_batches: string;
  test_batches: string;
  seed: string;
  dataset_hash: string;
  split_hash: string;
  config_hash: string;
  git_commit: string;
  environment: string;
  status: string;
  metrics_artifact: string;
  model_artifact: string;
  notes: string;
}

export interface DatasetEvidence {
  evidence_status: EvidenceStatus;
  source: string;
  source_url: string;
  artifact_path: string;
  validation: {
    status: string;
    samples: number;
    features: number;
    batches: number;
    classes: number;
    batch_rows: Record<string, number>;
    labels: Record<string, number>;
    missing_values: number;
    malformed_rows: unknown[];
    batch_hashes: Record<string, string>;
    dataset_hash: string;
    expectations: Record<string, { expected: number; actual: number; matches: boolean }>;
  } | null;
}

export interface BaselinesEvidence {
  evidence_status: EvidenceStatus;
  protocol_note: string;
  fixed_origin_summary: Record<string, string>[];
  fixed_origin_by_batch: Record<string, string>[];
  expanding_window_by_batch: Record<string, string>[];
  iid_diagnostic: Record<string, string>[];
  iid_generalization_gap: Record<string, string>[];
  expanding_vs_fixed: Record<string, string>[];
  model_complexity: Record<string, string>[];
  drift_performance_correlations: Record<string, string>[];
  artifact_paths: string[];
}

export interface DriftEvidence {
  evidence_status: EvidenceStatus;
  global_drift_by_batch: Record<string, string>[];
  artifact_paths: string[];
}

export interface ClaimRecord {
  claim_id: string;
  candidate_claim: string;
  experiment_id: string;
  dataset_hash: string;
  split_hash: string;
  config_hash: string;
  metric: string;
  result_artifact: string;
  figure: string;
  git_commit: string;
  status: string;
}

export interface FigureRecord {
  id: string;
  svg_path: string;
  png_path: string;
  source_csv: string | null;
}

export interface TableRecord {
  id: string;
  markdown_path: string;
  csv_path: string;
}

export interface PlatformStatus {
  authenticated: boolean;
  account?: string | null;
  username?: string | null;
  repository?: string;
  branch?: string;
  commit?: string;
  remote?: string;
  cli_version: string;
  timestamp: string;
}

export interface PlatformEvidence {
  github: PlatformStatus | null;
  huggingface: PlatformStatus | null;
  kaggle: PlatformStatus | null;
  platform_manifest: Record<string, unknown> | null;
}

export interface EnvironmentEvidence {
  timestamp_utc: string;
  in_colab: boolean;
  python: string;
  platform: string;
  cpu: string;
  logical_cpu_count: number;
  ram_bytes: number;
  gpu: string | null;
  cuda: string | null;
  git_commit: string;
  seed: number;
  packages: Record<string, string>;
}

export interface XaiApplicabilityRow {
  experiment_id: string;
  model_id: string;
  method: string;
  scope: string;
  status: string;
  reason: string;
}

export interface XaiTop3Row {
  model_id: string;
  method: string;
  batch: string;
  features: string[];
}

export interface XaiEvidence {
  evidence_status: EvidenceStatus;
  experiment_id: string | null;
  status: string;
  created_at: string | null;
  per_model_status: Record<string, { status: string; n_local_samples?: number; n_global_rows?: number; reason?: string }>;
  applicability_matrix: XaiApplicabilityRow[];
  n_global_rows: number;
  n_local_samples: number;
  n_reduced_rows: number;
  n_fidelity_prep_rows: number;
  local_sample_categories: Record<string, number>;
  top3_by_model_method_batch: XaiTop3Row[];
  artifact_paths: string[];
  fidelity_status: EvidenceStatus;
  stability_status: EvidenceStatus;
  latency_status: EvidenceStatus;
}

export interface ProjectStatus {
  project: string;
  repository: string;
  branch: string;
  git_commit: string;
  last_updated: string;
  pipeline_stage_counts: Record<string, number>;
  pipeline_total_stages: number;
  hardware_state: EvidenceStatus;
  paper_state: string;
}

export interface ResearchIntelligence {
  evidence_status: EvidenceStatus;
  registries: { experiments: Record<string, string>[]; measurements: Record<string, string>[]; artifacts: Record<string, string>[]; claims: Record<string, string>[]; decisions: Record<string, string>[] };
  feature_structure: { physical_sensors: number; features_per_sensor: number | null; feature_count: number; metadata_artifact: string };
  failure_rows: Record<string, string>[];
  class_failure_rows: Record<string, string>[];
  hardware_blocker: string;
  next_experiment: string;
}
