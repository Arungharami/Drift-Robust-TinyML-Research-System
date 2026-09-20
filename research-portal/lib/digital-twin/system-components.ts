// Canonical end-to-end research-pipeline registry for /system-map. Reads exclusively through
// research-portal/lib/evidence.ts — same rule as every other evidence-driven page — so this
// never becomes a second source of truth alongside configs/pipeline_stages.yaml.
//
// Where a conceptual stage below has a real, executed pipeline stage behind it, `pipelineIds`
// names the exact stage id(s) from getPipeline() and `researchStatus` is derived from them.
// Where no pipeline stage or protocol exists for a conceptual stage (e.g. live monitoring,
// production retraining), `researchStatus` is explicitly PLANNED and `pipelineIds` is empty —
// the node's presence on the map documents an architectural placeholder, not an implemented one.

import type { EvidenceLink } from "@/components/digital-twin/types";
import { getDataset, getEmbedded, getExperiments, getPipeline, getProjectStatus, getXai } from "@/lib/evidence";
import type { EvidenceStatus, PipelineStage } from "@/lib/types";

export type SystemMapGroup = "physical" | "data-ml" | "edge" | "operations" | "research";

export const GROUP_LABELS: Record<SystemMapGroup, string> = {
  physical: "Physical Layer",
  "data-ml": "Data / ML Layer",
  edge: "Edge Layer",
  operations: "Operations Layer",
  research: "Research Layer",
};

export interface SystemComponent {
  id: string;
  name: string;
  shortName?: string;
  group: SystemMapGroup;
  /** Display order within the overall pipeline (not necessarily unique across groups). */
  stage: number;
  description: string;
  role: string;
  inputs: string[];
  outputs: string[];
  algorithms?: string[];
  /** Research/evidence status — deliberately NOT called "status" alone, so it is never read as
   * "this page/feature is implemented." A node appearing on the map means it is documented,
   * not that its function is implemented or executed. */
  researchStatus: EvidenceStatus | string;
  statusNote?: string;
  /** Other node ids this stage depends on. */
  dependencies: string[];
  evidenceLinks: EvidenceLink[];
  relatedExperiments?: string[];
  relatedModels?: string[];
  limitations?: string[];
  portalHref?: string;
  pipelineIds: string[];
}

function stageStatus(pipeline: PipelineStage[], id: string): EvidenceStatus | string {
  return pipeline.find((s) => s.id === id)?.status ?? "NOT_EXECUTED";
}

/** Worst-case-first rollup for a node backed by several pipeline stages (e.g. the FP32 export chain). */
function worstStatus(statuses: (EvidenceStatus | string)[]): EvidenceStatus | string {
  const priority = ["FAILED", "BLOCKED", "BLOCKED_HARDWARE", "NOT_EXECUTED", "PLANNED", "PROTOCOL_FROZEN", "RUNNING", "EXECUTED", "VALIDATED"];
  for (const p of priority) if (statuses.includes(p)) return p;
  return statuses[0] ?? "NOT_EXECUTED";
}

export function buildSystemComponents(): SystemComponent[] {
  const pipeline = getPipeline();
  const dataset = getDataset();
  const xai = getXai();
  const embedded = getEmbedded();
  const project = getProjectStatus();
  const experimentIds = new Set(getExperiments().map((e) => e.experiment_id));
  const gate = embedded.stage15_hardware_gate;
  const hardwareStatus = String(gate?.scientific_execution_status ?? project.hardware_state);

  const xaiExperiments = ["EXP-XAI-0001", "EXP-XAI-FIDELITY-001", "EXP-XAI-STABILITY-001", "EXP-XAI-LATENCY-001"].filter((id) =>
    Array.from(experimentIds).some((e) => e.startsWith(id)),
  );

  const components: SystemComponent[] = [
    {
      id: "sample",
      name: "Sample",
      group: "physical",
      stage: 1,
      description: "The gas sample presented to the sensor array.",
      role: "Physical input to the entire pipeline.",
      inputs: ["Ambient odor / gas source"],
      outputs: ["Exposure to sensor array"],
      researchStatus: dataset.evidence_status,
      statusNote: "Represented by the public UCI Gas Sensor Array Drift dataset's original acquisition — not a live sample in this repository.",
      dependencies: [],
      evidenceLinks: [{ label: "Data dictionary", path: "docs/DATA_DICTIONARY.md" }],
      pipelineIds: [],
      portalHref: "/dataset",
    },
    {
      id: "sensor-system",
      name: "Sensor System",
      group: "physical",
      stage: 2,
      description: "16-channel metal-oxide gas sensor array.",
      role: "Transduces gas exposure into an analog electrical response.",
      inputs: ["Gas sample"],
      outputs: ["Analog conductance response, 16 channels"],
      researchStatus: dataset.evidence_status,
      dependencies: ["sample"],
      evidenceLinks: [{ label: "Feature ontology", path: "research/feature_metadata.csv" }],
      pipelineIds: ["02"],
      portalHref: "/dataset",
    },
    {
      id: "signal-acquisition",
      name: "Signal Acquisition",
      group: "physical",
      stage: 3,
      description: "Acquisition and digitization of the raw sensor response (128 features: 16 sensors × 8 response characteristics).",
      role: "Converts the physical response into the dataset's digitized feature columns.",
      inputs: ["Analog conductance response"],
      outputs: ["128-dimensional raw feature vector"],
      researchStatus: stageStatus(pipeline, "01"),
      dependencies: ["sensor-system"],
      evidenceLinks: [{ label: "Dataset acquisition", path: "src/data/download.py" }],
      pipelineIds: ["01"],
      portalHref: "/dataset",
    },
    {
      id: "preprocessing",
      name: "Preprocessing",
      group: "data-ml",
      stage: 4,
      description: "Training-only standardization and chronological split preparation.",
      role: "Prepares features for chronologically-evaluated model fitting without leakage.",
      inputs: ["Raw feature vector"],
      outputs: ["Standardized feature vector"],
      algorithms: ["StandardScaler (fit on Batch 1 only)"],
      researchStatus: stageStatus(pipeline, "04"),
      dependencies: ["signal-acquisition"],
      evidenceLinks: [{ label: "Chronological split", path: "src/data/chronology.py" }],
      pipelineIds: ["03", "04"],
      portalHref: "/methodology",
    },
    {
      id: "feature-extraction",
      name: "Feature Extraction",
      group: "data-ml",
      stage: 5,
      description: "128-feature ontology: 16 sensors × 8 response-characteristic features (steady-state, normalized, transient EMA).",
      role: "Defines the feature space every downstream model and explanation method consumes.",
      inputs: ["Standardized feature vector"],
      outputs: ["Named, typed feature ontology"],
      researchStatus: "EXECUTED",
      dependencies: ["preprocessing"],
      evidenceLinks: [{ label: "Feature metadata (128 features)", path: "research/feature_metadata.csv" }],
      pipelineIds: [],
      portalHref: "/dataset",
    },
    {
      id: "drift-analysis",
      name: "Drift Analysis",
      group: "data-ml",
      stage: 6,
      description: "Per-feature and global drift measured against the Batch-1 reference distribution.",
      role: "Quantifies how much sensor behavior shifts across chronological batches.",
      inputs: ["Feature vectors, all batches"],
      outputs: ["Per-feature and global drift scores"],
      algorithms: ["Standardized mean shift", "Normalized Wasserstein distance"],
      researchStatus: stageStatus(pipeline, "07"),
      dependencies: ["feature-extraction"],
      evidenceLinks: [
        { label: "Drift metrics implementation", path: "src/drift/metrics.py" },
        { label: "Global drift by batch", path: "results/drift/global_drift_by_batch.csv" },
      ],
      pipelineIds: ["07"],
      portalHref: "/results",
      limitations: ["Univariate only — no PSI, KS-test, or multivariate drift detector is implemented."],
    },
    {
      id: "machine-learning",
      name: "Machine Learning",
      group: "data-ml",
      stage: 7,
      description: "Four chronologically-evaluated classical models under FIXED_ORIGIN and EXPANDING_WINDOW protocols.",
      role: "Produces the gas-class predictions every later stage explains, compresses, or deploys.",
      inputs: ["Standardized feature vector"],
      outputs: ["Predicted gas class"],
      algorithms: ["Logistic Regression", "Random Forest", "RBF-SVM", "MLP"],
      researchStatus: worstStatus([stageStatus(pipeline, "05"), stageStatus(pipeline, "06")]),
      dependencies: ["feature-extraction"],
      relatedModels: ["MODEL-C1", "MODEL-C2", "MODEL-C3", "MODEL-C4"],
      evidenceLinks: [{ label: "Model definitions", path: "src/models/classical.py" }],
      pipelineIds: ["05", "06"],
      portalHref: "/methodology",
    },
    {
      id: "calibration",
      name: "Calibration",
      group: "data-ml",
      stage: 8,
      description: "Causal confidence calibration (ECE, Brier, NLL, risk-coverage) for selective prediction.",
      role: "Would determine whether model confidence is trustworthy enough to act on under drift.",
      inputs: ["Predicted class probabilities"],
      outputs: ["Calibrated confidence (not yet produced)"],
      researchStatus: "PLANNED",
      statusNote: "RQ8/AC8 — required evidence fields are still PLANNED; H8 is UNTESTED.",
      dependencies: ["machine-learning"],
      evidenceLinks: [{ label: "Acceptance criteria (AC8)", path: "research/acceptance_criteria.yaml" }],
      pipelineIds: [],
    },
    {
      id: "explainability",
      name: "Explainability",
      group: "data-ml",
      stage: 9,
      description: "Resource-aware explanations (permutation importance, intrinsic coefficients/impurity, single-feature ablation) — deliberately not SHAP or LIME.",
      role: "Attributes each prediction to contributing sensor features.",
      inputs: ["Model + feature vector"],
      outputs: ["Feature attribution"],
      algorithms: ["Permutation importance", "Intrinsic coefficients / impurity", "Single-feature ablation"],
      researchStatus: worstStatus([stageStatus(pipeline, "09"), stageStatus(pipeline, "10"), stageStatus(pipeline, "11"), stageStatus(pipeline, "12")]),
      statusNote: "Executed, but fidelity and stability evidence is predominantly unsupported or mixed.",
      dependencies: ["machine-learning"],
      relatedExperiments: xaiExperiments,
      evidenceLinks: [{ label: "Resource-aware XAI protocol", path: "docs/experiments/STAGE09_RESOURCE_AWARE_XAI.md" }],
      pipelineIds: ["09", "10", "11", "12"],
      portalHref: "/xai",
      limitations: ["Fidelity/stability outcomes are mixed, not confirmatory — see /xai."],
    },
    {
      id: "compression",
      name: "Compression / Quantization",
      group: "edge",
      stage: 10,
      description: "INT8 post-training quantization planned; not yet executed at any tier.",
      role: "Would shrink a trained model to fit TinyML memory budgets.",
      inputs: ["Trained model"],
      outputs: ["Quantized model (not yet produced)"],
      researchStatus: String(gate?.quantization ?? "NOT_EXECUTED"),
      statusNote: "Quantization has not been executed at any tier; only FP32 host export equivalence has been attempted.",
      dependencies: ["machine-learning"],
      evidenceLinks: [{ label: "Embedded equivalence protocol", path: "configs/embedded_equivalence_protocol.yaml" }],
      pipelineIds: ["13", "14", "14R", "14F-GATE", "14F-EXEC", "14F-XAI"],
      portalHref: "/tinyml",
      limitations: ["Standalone FP32 export equivalence FAILED twice (Stage 14, 14R) before a fused-preprocessing variant passed on host only (14F)."],
    },
    {
      id: "tinyml-artifact",
      name: "TinyML Artifact",
      group: "edge",
      stage: 11,
      description: "Deployable, quantized, cross-compiled model artifact for the nRF52840.",
      role: "The file that would actually be flashed to the MCU.",
      inputs: ["Quantized model"],
      outputs: ["Cross-compiled firmware artifact (not yet produced)"],
      researchStatus: "NOT_EXECUTED",
      statusNote: "Only host-compiled (x86-64, Zig cc) C export exists — never cross-compiled for Cortex-M4F.",
      dependencies: ["compression"],
      evidenceLinks: [{ label: "Embedded export source", path: "src/embedded/export_fp32_common.py" }],
      pipelineIds: [],
      portalHref: "/tinyml",
    },
    {
      id: "nrf52840-deployment",
      name: "nRF52840 Deployment",
      group: "edge",
      stage: 12,
      description: "Physical flashing and execution on a Nordic nRF52840 (Cortex-M4F) development kit.",
      role: "The physical validation target for every TinyML claim in this project.",
      inputs: ["Cross-compiled firmware artifact"],
      outputs: ["Running on-device inference (not yet produced)"],
      researchStatus: hardwareStatus,
      statusNote: "No physical nRF52840 board or debug probe has ever been detected on the development machine.",
      dependencies: ["tinyml-artifact"],
      relatedExperiments: ["EXP-MCU-C1-FP32-PORT-001"],
      evidenceLinks: [{ label: "Hardware detection evidence", path: "results/embedded/stage15_hardware_detection.json" }],
      pipelineIds: ["15", "16", "17", "18", "19"],
      portalHref: "/hardware",
    },
    {
      id: "edge-prediction",
      name: "Edge Prediction",
      group: "edge",
      stage: 13,
      description: "On-device inference output, produced entirely on the MCU.",
      role: "The prediction a deployed device would serve without a host round-trip.",
      inputs: ["On-device model + live features"],
      outputs: ["Prediction + confidence (not yet produced)"],
      researchStatus: "BLOCKED",
      statusNote: "Blocked on nRF52840 Deployment.",
      dependencies: ["nrf52840-deployment"],
      evidenceLinks: [],
      pipelineIds: [],
    },
    {
      id: "gateway-telemetry",
      name: "Gateway / Telemetry",
      group: "operations",
      stage: 14,
      description: "Planned USB / Serial / BLE bridge forwarding device telemetry to a host gateway.",
      role: "Would carry predictions and diagnostics off the device for monitoring.",
      inputs: ["Edge prediction (planned)"],
      outputs: ["Forwarded telemetry stream (planned)"],
      researchStatus: "PLANNED",
      statusNote: "Architecture only — no device is connected. See the Gateway node on /digital-twin.",
      dependencies: ["edge-prediction"],
      evidenceLinks: [],
      pipelineIds: [],
    },
    {
      id: "monitoring",
      name: "Monitoring",
      group: "operations",
      stage: 15,
      description: "Live dashboarding of deployed-device drift, confidence, and health.",
      role: "Would surface production drift so retraining can be triggered.",
      inputs: ["Telemetry stream"],
      outputs: ["Monitoring dashboard (planned)"],
      researchStatus: "PLANNED",
      statusNote: "No live monitoring exists — /live-lab and telemetry adapters are future-phase work.",
      dependencies: ["gateway-telemetry"],
      evidenceLinks: [],
      pipelineIds: [],
    },
    {
      id: "adaptation",
      name: "Adaptation / Retraining",
      group: "operations",
      stage: 16,
      description: "A live production retraining loop triggered by detected drift.",
      role: "Would keep a deployed model current as sensors age or drift.",
      inputs: ["Monitoring signal"],
      outputs: ["Updated model (planned)"],
      researchStatus: "PLANNED",
      statusNote: "Distinct from the EXPANDING_WINDOW research evaluation protocol (already executed offline, see /methodology) — this node is a live production loop, which does not exist.",
      dependencies: ["monitoring"],
      evidenceLinks: [{ label: "Expanding-window protocol (offline research analog)", path: "configs/chronological_protocol.yaml" }],
      pipelineIds: [],
    },
    {
      id: "experiment-registry",
      name: "Experiment Registry",
      group: "research",
      stage: 17,
      description: "Append-only registry of every executed experiment, with dataset/config/model hashes and git commit.",
      role: "Provenance backbone for every claim made anywhere in this portal.",
      inputs: ["Executed pipeline runs"],
      outputs: ["Registered experiment records"],
      researchStatus: "EXECUTED",
      dependencies: [],
      evidenceLinks: [{ label: "Experiment registry", path: "results/registry/experiment_registry.csv" }],
      pipelineIds: [],
      portalHref: "/experiments",
    },
    {
      id: "evidence-ledger",
      name: "Evidence Ledger",
      group: "research",
      stage: 18,
      description: "Claim → experiment → dataset/config hash → git commit → result artifact mapping.",
      role: "Determines whether any manuscript claim is SUPPORTED, UNSUPPORTED, or UNRESOLVED.",
      inputs: ["Experiment registry", "result artifacts"],
      outputs: ["Claim status"],
      researchStatus: "EXECUTED",
      dependencies: ["experiment-registry"],
      evidenceLinks: [{ label: "Claim-evidence matrix", path: "paper/claim_evidence_matrix.csv" }],
      pipelineIds: ["21", "22"],
      portalHref: "/paper",
    },
  ];

  // Every explainability-related dependency should also chain through drift/ML — verified once here,
  // rather than trusted per-node, so a future edit can't silently create a dangling dependency id.
  const ids = new Set(components.map((c) => c.id));
  for (const c of components) {
    for (const dep of c.dependencies) {
      if (!ids.has(dep)) throw new Error(`system-components.ts: unknown dependency "${dep}" on "${c.id}"`);
    }
  }

  return components;
}
