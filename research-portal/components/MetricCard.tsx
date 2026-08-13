import { EvidenceBadge } from "./EvidenceBadge";
import type { EvidenceStatus } from "@/lib/types";

export function MetricCard({
  label,
  value,
  unit,
  status,
  sublabel,
}: {
  label: string;
  value: string | number | null;
  unit?: string;
  status: EvidenceStatus;
  sublabel?: string;
}) {
  const displayValue = value === null || value === undefined || value === "" ? "—" : value;
  return (
    <div className="card">
      <div className="section-label">{label}</div>
      {status === "EXECUTED" || status === "VALIDATED" ? (
        <div>
          <span className="metric-value">{displayValue}</span>
          {unit ? <span className="metric-unit">{unit}</span> : null}
        </div>
      ) : (
        <EvidenceBadge status={status} />
      )}
      {sublabel ? <p style={{ marginTop: "0.5rem", fontSize: "0.82rem", color: "var(--text-faint)" }}>{sublabel}</p> : null}
    </div>
  );
}
