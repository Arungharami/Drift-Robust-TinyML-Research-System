import type { EvidenceStatus } from "@/lib/types";

const LABELS: Record<EvidenceStatus, string> = {
  EXECUTED: "Executed",
  VALIDATED: "Validated",
  PLANNED: "Planned",
  RUNNING: "Running",
  FAILED: "Failed",
  BLOCKED: "Blocked",
  BLOCKED_HARDWARE: "Hardware blocked",
  PROTOCOL_FROZEN: "Protocol frozen",
  NOT_EXECUTED: "Not executed",
  NOT_MEASURED: "Not measured",
};

export function EvidenceBadge({ status }: { status: EvidenceStatus | string }) {
  const known = (status in LABELS ? status : "NOT_EXECUTED") as EvidenceStatus;
  return <span className={`badge badge-${known}`}>{LABELS[known]}</span>;
}
