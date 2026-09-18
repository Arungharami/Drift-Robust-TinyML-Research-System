// Builds the digital-twin component list from real evidence. This is the ONLY
// place that maps evidence into 3D-scene data — it reads exclusively through
// lib/evidence.ts, same rule as every other page in the portal, so the twin
// can never show a status the rest of the site doesn't already show.

import { getDataset, getEmbedded, getProjectStatus, getXai } from "@/lib/evidence";
import type { TwinComponent } from "./types";

export function buildTwinComponents(): TwinComponent[] {
  const project = getProjectStatus();
  const embedded = getEmbedded();
  const xai = getXai();
  const dataset = getDataset();
  const gate = embedded.stage15_hardware_gate;
  const hardwareStatus = String(gate?.scientific_execution_status ?? project.hardware_state);

  const components: TwinComponent[] = [
    {
      id: "sensor-chamber",
      name: "Sample Chamber",
      group: "sensor",
      position: [-9, 0, 0],
      role: "Holds the gas sample and exposes it to the sensor array during acquisition.",
      input: "Odor / gas sample",
      output: "Raw analog sensor response",
      status: dataset.evidence_status,
      statusNote: "Modeled from the UCI Gas Sensor Array Drift dataset's acquisition protocol — this is not a live chamber.",
      evidenceLinks: [{ label: "Data dictionary", path: "docs/DATA_DICTIONARY.md" }],
      portalHref: "/dataset",
    },
    {
      id: "sensor-array",
      name: "16-Channel Sensor Array",
      group: "sensor",
      position: [-6.3, 0, 0],
      role: "16 metal-oxide gas sensors, 8 response-characteristic features each (128 features total).",
      input: "Analog conductance response",
      output: "128-dimensional feature vector",
      status: dataset.evidence_status,
      evidenceLinks: [{ label: "Feature ontology (128 features)", path: "research/feature_metadata.csv" }],
      portalHref: "/dataset",
    },
    {
      id: "drift-detector",
      name: "Drift Detector",
      group: "edge",
      position: [-3.6, 0, 0],
      role: "Computes per-feature Wasserstein distance and standardized mean shift against the Batch-1 reference distribution.",
      input: "Feature vector (current batch)",
      output: "Per-feature and global drift score",
      status: "EXECUTED",
      evidenceLinks: [
        { label: "Drift metrics implementation", path: "src/drift/metrics.py" },
        { label: "Global drift by batch", path: "results/drift/global_drift_by_batch.csv" },
      ],
      portalHref: "/results",
    },
    {
      id: "ml-model",
      name: "Classical ML Model",
      group: "edge",
      position: [-0.9, 0, 0],
      role: "One of four chronologically-evaluated classical models (Logistic Regression, Random Forest, RBF-SVM, MLP).",
      input: "Feature vector",
      output: "Predicted gas class",
      status: "EXECUTED",
      evidenceLinks: [{ label: "Model definitions", path: "src/models/classical.py" }],
      portalHref: "/methodology",
    },
    {
      id: "xai",
      name: "Resource-Aware Explanation",
      group: "cloud",
      position: [1.8, 2.1, 0],
      role: "Permutation importance, intrinsic coefficients/impurity, and single-feature ablation — deliberately not SHAP or LIME.",
      input: "Model + feature vector",
      output: "Feature attribution",
      status: xai.evidence_status,
      statusNote: "Executed, but fidelity and stability evidence is predominantly unsupported or mixed — see the XAI page.",
      evidenceLinks: [{ label: "Resource-aware XAI protocol", path: "docs/experiments/STAGE09_RESOURCE_AWARE_XAI.md" }],
      portalHref: "/xai",
    },
    {
      id: "mcu",
      name: "nRF52840 MCU (conceptual)",
      group: "edge",
      position: [4.5, 0, 0],
      role: "Target Cortex-M4F edge device for quantized inference. This model is a conceptual placeholder, not a reconstruction of the physical board.",
      input: "Quantized model + preprocessed features",
      output: "On-device prediction (not yet produced)",
      status: hardwareStatus,
      statusNote: "No physical nRF52840 board or debug probe has ever been detected on the development machine.",
      evidenceLinks: [{ label: "Hardware detection evidence", path: "results/embedded/stage15_hardware_detection.json" }],
      portalHref: "/hardware",
    },
    {
      id: "gateway",
      name: "Gateway / Laptop",
      group: "gateway",
      position: [7.2, 0, 0],
      role: "Planned USB / Serial / BLE bridge between the MCU and the research portal. Architecture only — no device is connected.",
      input: "Device telemetry (planned)",
      output: "Forwarded telemetry stream (planned)",
      status: "PLANNED",
      evidenceLinks: [],
    },
    {
      id: "cloud",
      name: "Research & Evidence Registry",
      group: "cloud",
      position: [9.9, 0, 0],
      role: "Experiment registry, claim-evidence ledger, and the generated evidence this entire portal reads from.",
      input: "Experiment artifacts",
      output: "Evidence-backed claims and status badges",
      status: "EXECUTED",
      evidenceLinks: [{ label: "Claim-evidence matrix", path: "paper/claim_evidence_matrix.csv" }],
      portalHref: "/experiments",
    },
  ];

  return components;
}
