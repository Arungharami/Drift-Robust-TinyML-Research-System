export type EvidenceStatus = "EXECUTED" | "IN_PROGRESS" | "NOT_EXECUTED" | "PLANNED";

export const project = {
  title: "Drift-Robust Explainable TinyML for Electronic-Nose Sensing",
  subtitle:
    "Chronological evaluation, resource-aware explanations, and reproducible edge deployment on constrained hardware.",
  author: "Arun Kumar Gharami",
  year: 2026,
  repository: "https://github.com/Arungharami/Drift-Robust-TinyML-Research-System",
  huggingFaceProfile: "https://huggingface.co/arun-gharami",
  uciDataset:
    "https://archive.ics.uci.edu/dataset/270/gas+sensor+array+drift+dataset+at+different+concentrations",
};

export const evidenceRules = [
  "Every reported number must come from an executed experiment and saved artifact.",
  "Chronological batches are never randomly mixed for the primary drift evaluation.",
  "Hardware latency, Flash, SRAM, and energy stay NOT EXECUTED until physically measured.",
  "The public portal distinguishes executed evidence from planned methodology.",
  "Model, explanation, export, and hardware artifacts must be traceable to a configuration and commit.",
];

export const datasetFacts = [
  { label: "Measurements", value: "13,910" },
  { label: "Sensors", value: "16 chemical sensors" },
  { label: "Features", value: "128 per measurement" },
  { label: "Classes", value: "6 gases" },
  { label: "Chronology", value: "10 batches / 36 months" },
  { label: "Missing values", value: "None reported by UCI" },
];

export const pipeline = [
  {
    id: "01",
    title: "Dataset acquisition & integrity",
    status: "IN_PROGRESS" as EvidenceStatus,
    detail:
      "Load the UCI gas-sensor drift data, retain original batch identity, record source DOI, file hashes, row counts, labels, concentrations, and schema checks.",
  },
  {
    id: "02",
    title: "Chronological protocol",
    status: "PLANNED" as EvidenceStatus,
    detail:
      "Freeze train/validation/test rules that respect time ordering. Report per-batch performance and degradation instead of only a pooled random split.",
  },
  {
    id: "03",
    title: "Frozen lightweight baselines",
    status: "PLANNED" as EvidenceStatus,
    detail:
      "Run reproducible classical and compact models with fixed seeds, preprocessing, and hyperparameter records. Select only evidence-supported candidates for edge deployment.",
  },
  {
    id: "04",
    title: "Drift robustness analysis",
    status: "NOT_EXECUTED" as EvidenceStatus,
    detail:
      "Measure accuracy, macro-F1, confusion structure, per-batch degradation, and model stability as the sensor distribution evolves.",
  },
  {
    id: "05",
    title: "Resource-aware explanations",
    status: "NOT_EXECUTED" as EvidenceStatus,
    detail:
      "Compare explanation methods that can be simplified or approximated for edge use. Heavy desktop SHAP/LIME results are not treated as proof of MCU feasibility.",
  },
  {
    id: "06",
    title: "Fidelity & stability",
    status: "NOT_EXECUTED" as EvidenceStatus,
    detail:
      "Evaluate whether lightweight explanations preserve important attribution behavior and whether explanation rankings remain stable under chronological drift.",
  },
  {
    id: "07",
    title: "Quantization & embedded export",
    status: "NOT_EXECUTED" as EvidenceStatus,
    detail:
      "Export only selected models, verify prediction parity, generate embedded artifacts, and preserve conversion logs and checksums.",
  },
  {
    id: "08",
    title: "nRF52840 deployment",
    status: "NOT_EXECUTED" as EvidenceStatus,
    detail:
      "Compile for Cortex-M4F, capture map files, and measure physical inference/explanation latency on the target board.",
  },
  {
    id: "09",
    title: "PPK2 energy measurement",
    status: "NOT_EXECUTED" as EvidenceStatus,
    detail:
      "Use Nordic PPK2 traces for physical inference and explanation energy. No proxy energy values are presented as measured results.",
  },
  {
    id: "10",
    title: "Accuracy–trust–resource Pareto analysis",
    status: "NOT_EXECUTED" as EvidenceStatus,
    detail:
      "Build a final trade-off view only from measured accuracy, explanation quality, Flash/SRAM, latency, and energy evidence.",
  },
];

export const equations = [
  {
    name: "Macro-F1",
    equation: "F1_macro = (1/C) Σ_c 2·P_c·R_c / (P_c + R_c)",
    note: "Primary class-balanced performance measure across gases.",
  },
  {
    name: "Chronological degradation",
    equation: "ΔM_t = M_reference − M_t",
    note: "Tracks performance loss in each future batch relative to the frozen reference condition.",
  },
  {
    name: "Top-k explanation stability",
    equation: "S_J(A,B) = |Top_k(A) ∩ Top_k(B)| / |Top_k(A) ∪ Top_k(B)|",
    note: "A simple, auditable stability view for important-feature overlap across batches or perturbations.",
  },
  {
    name: "Physical energy",
    equation: "E = ∫ V(t) · I(t) dt",
    note: "Computed from the measured PPK2 trace, not estimated from runtime alone.",
  },
  {
    name: "Pareto dominance",
    equation: "a ≺ b if a is no worse on every objective and strictly better on at least one",
    note: "Used to identify defensible accuracy–trust–resource trade-offs without inventing a single arbitrary score.",
  },
];

export const architecture = [
  {
    title: "Research path",
    flow: "UCI data → Colab experiments → immutable metrics/artifacts → GitHub evidence record → Hugging Face model card → Vercel portal",
  },
  {
    title: "Physical edge path",
    flow: "Gas sensor array → nRF52840 inference + lightweight explanation → USB/BLE gateway → telemetry → Vercel dashboard",
  },
  {
    title: "Artifact lineage",
    flow: "config + seed + data manifest + commit → model → explanation → quantized export → firmware build → map/log/PPK2 trace",
  },
];

export const huggingFacePlan = [
  {
    title: "Model repository",
    status: "PLANNED" as EvidenceStatus,
    detail:
      "Publish the selected deployable model, model card, preprocessing contract, limitations, evaluation tables, and artifact hashes after the evidence gate passes.",
  },
  {
    title: "Dataset card / pointer",
    status: "PLANNED" as EvidenceStatus,
    detail:
      "Reference the canonical UCI source and publish reproducible split manifests and preprocessing metadata rather than silently changing the raw benchmark.",
  },
  {
    title: "Interactive Space",
    status: "PLANNED" as EvidenceStatus,
    detail:
      "Optional Gradio/Space demo for a validated model. The Vercel portal can embed or call the demo while the MCU remains the authoritative deployment target.",
  },
];

export const noveltyMap = [
  {
    prior: "Vergara et al. (2012)",
    contribution: "Foundational classifier-ensemble drift compensation benchmark.",
    gapForThisProject: "No modern resource-aware XAI or measured TinyML deployment.",
  },
  {
    prior: "Disabato & Roveri (2024)",
    contribution: "TinyML adaptation under concept drift on microcontrollers.",
    gapForThisProject: "Not focused on electronic-nose gas drift or explanation quality/energy.",
  },
  {
    prior: "Zhang et al. (2025)",
    contribution: "Multi-source attention/domain adaptation for E-nose drift.",
    gapForThisProject: "Strong drift modeling, but a different objective from measured explainable TinyML deployment.",
  },
  {
    prior: "Lin & Zhan (2026)",
    contribution: "Knowledge-distillation drift compensation with future-batch style evaluation.",
    gapForThisProject: "Raises the bar for chronological evaluation; does not by itself establish physical resource-aware XAI on the target MCU.",
  },
  {
    prior: "Dehghani et al. (2026 preprint)",
    contribution: "Human-centered Pareto selection of XAI methods for TinyML.",
    gapForThisProject: "Physical MCU deployment and empirical hardware validation are explicitly outside that proof-of-concept scope.",
  },
];

export const references = [
  {
    label: "UCI Gas Sensor Array Drift at Different Concentrations",
    year: "2013",
    url: "https://doi.org/10.24432/C5MK6M",
  },
  {
    label: "Vergara et al. — Chemical gas sensor drift compensation using classifier ensembles",
    year: "2012",
    url: "https://doi.org/10.1016/j.snb.2012.01.074",
  },
  {
    label: "Rodríguez-Luján et al. — Calibration of sensor arrays with minimal experiments",
    year: "2014",
    url: "https://doi.org/10.1016/j.chemolab.2013.10.012",
  },
  {
    label: "Disabato & Roveri — Tiny Machine Learning for Concept Drift",
    year: "2024",
    url: "https://doi.org/10.1109/TNNLS.2022.3229897",
  },
  {
    label: "Zhang et al. — Unsupervised Attention-Based Multisource Domain Adaptation",
    year: "2025",
    url: "https://doi.org/10.1109/TIM.2025.3604131",
  },
  {
    label: "Sun et al. — Prototype-Optimized Unsupervised Domain Adaptation",
    year: "2025",
    url: "https://doi.org/10.1016/j.eswa.2024.125444",
  },
  {
    label: "Lin & Zhan — Sensor-Drift Compensation Using Knowledge Distillation",
    year: "2026",
    url: "https://doi.org/10.3390/informatics13010015",
  },
  {
    label: "Li et al. — Robust domain adversarial network with joint adaptation",
    year: "2026",
    url: "https://doi.org/10.1016/j.microc.2026.116906",
  },
  {
    label: "Dehghani et al. — Human-Centered Explainable AI for TinyML Edge Devices",
    year: "2026",
    url: "https://arxiv.org/abs/2608.07091",
  },
];

export const professorWorkflow = [
  "Share the Vercel preview as a compact project brief before a meeting.",
  "Ask the professor to challenge the research question, chronological protocol, baselines, and novelty map before final experiments are frozen.",
  "Record advisor decisions as dated methodology notes or GitHub issues so changes are auditable.",
  "After results exist, invite review of the evidence tables, failure cases, and hardware measurement protocol before drafting strong claims.",
  "Add co-authorship or formal project roles only after contribution and authorship expectations are explicitly agreed.",
];

export const telemetryExample = `{
  "device_id": "nrf52840-enose-01",
  "timestamp": "ISO-8601",
  "batch_context": "real-world-demo",
  "prediction": null,
  "confidence": null,
  "top_features": [],
  "inference_latency_ms": null,
  "explanation_latency_ms": null,
  "energy_uJ": null,
  "evidence_status": "NOT_EXECUTED"
}`;
