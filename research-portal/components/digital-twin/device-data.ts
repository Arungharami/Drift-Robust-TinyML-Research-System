// Builds the exploded device-layer list for /digital-twin/device from real evidence — same
// rule as twin-data.ts: reads exclusively through lib/evidence.ts. Where a layer overlaps a
// /digital-twin component conceptually (sample chamber, sensor array, MCU), it reuses the same
// id so the two pages can deep-link to "the same thing," not a re-derived duplicate.

import { getDataset, getEmbedded, getProjectStatus } from "@/lib/evidence";
import type { TwinComponent } from "./types";

/** Vertical layer index, top (0) to bottom (9) — used for both assembled and exploded Y placement. */
export function buildDeviceLayers(): TwinComponent[] {
  const project = getProjectStatus();
  const embedded = getEmbedded();
  const dataset = getDataset();
  const gate = embedded.stage15_hardware_gate;
  const hardwareStatus = String(gate?.scientific_execution_status ?? project.hardware_state);
  const fp32Status = embedded.fp32_summary?.scientific_execution_status ?? "NOT_EXECUTED";

  const layers: TwinComponent[] = [
    {
      id: "top-enclosure",
      name: "Top Enclosure",
      group: "sensor",
      position: [0, 0, 0],
      category: "physical",
      role: "Weatherproof/handling shell over the sample chamber.",
      researchPurpose: "Protects the sensor array and allows controlled sample exposure.",
      input: "Ambient environment",
      output: "Sealed internal volume",
      status: "PLANNED",
      statusNote: "No enclosure design exists in this repository — architecture placeholder only.",
      evidenceLinks: [],
    },
    {
      id: "sensor-chamber",
      name: "Sample Chamber",
      group: "sensor",
      position: [0, 0, 0],
      category: "physical",
      role: "Holds the gas sample and exposes it to the sensor array.",
      input: "Odor / gas sample",
      output: "Raw analog sensor response",
      status: dataset.evidence_status,
      statusNote: "Modeled from the UCI Gas Sensor Array Drift dataset's acquisition protocol.",
      evidenceLinks: [{ label: "Data dictionary", path: "docs/DATA_DICTIONARY.md" }],
      portalHref: "/dataset",
    },
    {
      id: "sensor-array",
      name: "16-Channel Sensor Array",
      group: "sensor",
      position: [0, 0, 0],
      category: "sensor",
      role: "16 metal-oxide gas sensors, 8 response-characteristic features each.",
      input: "Analog conductance response",
      output: "128-dimensional feature vector",
      status: dataset.evidence_status,
      evidenceLinks: [{ label: "Feature ontology (128 features)", path: "research/feature_metadata.csv" }],
      portalHref: "/dataset",
    },
    {
      id: "signal-acquisition",
      name: "Signal Acquisition Module",
      group: "sensor",
      position: [0, 0, 0],
      category: "signal",
      role: "Generic functional placeholder for analog-to-digital signal conditioning.",
      researchPurpose: "Would convert raw sensor conductance into the digitized values the pipeline consumes.",
      input: "Analog sensor response",
      output: "Digitized feature stream",
      status: "PLANNED",
      statusNote: "No acquisition circuit has been selected or designed — named generically rather than claiming a specific ADC.",
      evidenceLinks: [],
    },
    {
      id: "main-pcb",
      name: "Main PCB",
      group: "edge",
      position: [0, 0, 0],
      category: "physical",
      role: "Carrier board for the MCU and supporting circuitry.",
      input: "Digitized feature stream, power",
      output: "Routed signals to MCU",
      status: "PLANNED",
      statusNote: "No PCB layout exists in this repository.",
      evidenceLinks: [],
    },
    {
      id: "mcu",
      name: "nRF52840 MCU",
      group: "edge",
      position: [0, 0, 0],
      category: "deployment",
      role: "Target Cortex-M4F edge device for quantized inference.",
      researchPurpose: "The physical validation target for every TinyML claim in this project.",
      input: "Quantized model + preprocessed features",
      output: "On-device prediction (not yet produced)",
      status: String(gate?.flash ?? "NOT_EXECUTED"),
      hardwareStatus: hardwareStatus,
      statusNote: "No physical nRF52840 board or debug probe has ever been detected on the development machine.",
      evidenceLinks: [{ label: "Hardware detection evidence", path: "results/embedded/stage15_hardware_detection.json" }],
      relatedExperiments: ["EXP-MCU-C1-FP32-PORT-001"],
      limitations: ["Board identity unresolved: no supported device detected.", "Zephyr board target not selected."],
      portalHref: "/hardware",
    },
    {
      id: "inference-layer",
      name: "Model / Inference Layer",
      group: "edge",
      position: [0, 0, 0],
      category: "tinyml",
      role: "Stores the exported model and runs the inference computation.",
      researchPurpose: "Numerical-equivalence-checked C export of the frozen classical models.",
      input: "Feature vector",
      output: "Predicted class + score",
      status: String(fp32Status),
      statusNote: "Host-compiled (x86-64, Zig cc) numerical-equivalence build only — never cross-compiled or run on an MCU.",
      relatedModels: ["MODEL-C1", "MODEL-C4"],
      evidenceLinks: [{ label: "Embedded export source", path: "src/embedded/export_fp32_common.py" }],
      portalHref: "/tinyml",
    },
    {
      id: "comm-layer",
      name: "Communication Layer",
      group: "gateway",
      position: [0, 0, 0],
      category: "gateway",
      role: "Generic placeholder for the planned USB / Serial / BLE bridge to a host gateway.",
      input: "On-device prediction (planned)",
      output: "Forwarded telemetry (planned)",
      status: "PLANNED",
      evidenceLinks: [],
    },
    {
      id: "power-layer",
      name: "Power Layer",
      group: "edge",
      position: [0, 0, 0],
      category: "physical",
      role: "Planned Power Profiler Kit II (PPK2) measurement point for inference/explanation energy.",
      input: "Supply voltage",
      output: "Regulated MCU power / current trace (planned)",
      status: "NOT_EXECUTED",
      statusNote: "No physical PPK2 trace exists.",
      evidenceLinks: [],
      portalHref: "/hardware",
    },
    {
      id: "bottom-enclosure",
      name: "Bottom Enclosure",
      group: "sensor",
      position: [0, 0, 0],
      category: "physical",
      role: "Base shell carrying the PCB and power connections.",
      input: "N/A",
      output: "Mechanical support",
      status: "PLANNED",
      statusNote: "No enclosure design exists in this repository — architecture placeholder only.",
      evidenceLinks: [],
    },
  ];

  return layers;
}
