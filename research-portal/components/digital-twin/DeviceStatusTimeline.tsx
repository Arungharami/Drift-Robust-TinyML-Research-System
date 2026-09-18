import { EvidenceBadge } from "@/components/EvidenceBadge";
import { getDataset, getEmbedded, getPipeline } from "@/lib/evidence";

interface TimelineStep {
  label: string;
  status: string;
  note?: string;
}

function pipelineStatus(id: string): string {
  const stage = getPipeline().find((s) => s.id === id);
  return stage?.status ?? "NOT_EXECUTED";
}

function buildTimeline(): TimelineStep[] {
  const dataset = getDataset();
  const embedded = getEmbedded();
  const gate = embedded.stage15_hardware_gate;

  return [
    { label: "Physical Design", status: "PLANNED", note: "No enclosure/PCB design exists in this repository." },
    { label: "Sensor Integration", status: String(dataset.evidence_status) },
    { label: "Signal Acquisition", status: "PLANNED", note: "No acquisition circuit selected." },
    { label: "Firmware", status: String(gate?.flash ?? "NOT_EXECUTED") },
    { label: "Model Export", status: String(embedded.fp32_summary?.scientific_execution_status ?? "NOT_EXECUTED"), note: "Host-compiled equivalence build only." },
    { label: "Quantization", status: String(gate?.quantization ?? "NOT_EXECUTED") },
    { label: "Flash / SRAM Measurement", status: pipelineStatus("16") },
    { label: "MCU Execution", status: String(gate?.scientific_execution_status ?? pipelineStatus("15")) },
    { label: "Latency Measurement", status: pipelineStatus("17") },
    { label: "Energy Measurement", status: pipelineStatus("18") },
  ];
}

/** Engineering-progress summary for the device view — every value traced to real pipeline/gate evidence. */
export function DeviceStatusTimeline() {
  const steps = buildTimeline();
  return (
    <ol className="twin-timeline">
      {steps.map((step, i) => (
        <li key={step.label}>
          <span className="twin-timeline-index">{String(i + 1).padStart(2, "0")}</span>
          <span className="twin-timeline-label">{step.label}</span>
          <EvidenceBadge status={step.status} />
          {step.note && <span className="twin-timeline-note">{step.note}</span>}
        </li>
      ))}
    </ol>
  );
}
