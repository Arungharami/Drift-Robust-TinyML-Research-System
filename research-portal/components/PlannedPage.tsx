import { EvidenceBadge } from "./EvidenceBadge";
import type { EvidenceStatus } from "@/lib/types";

/** Shared shell for routes whose evidence does not exist yet — an honest, non-broken page
 * rather than a 404 or (worse) fabricated content. */
export function PlannedPage({
  title,
  status = "NOT_EXECUTED",
  summary,
  plan,
}: {
  title: string;
  status?: EvidenceStatus;
  summary: string;
  plan: string[];
}) {
  return (
    <div className="container">
      <div className="section-label">Status</div>
      <div style={{ marginBottom: "0.75rem" }}>
        <EvidenceBadge status={status} />
      </div>
      <h1>{title}</h1>
      <p className="lede">{summary}</p>
      <div className="empty-state">
        <strong>No executed results exist for this page yet.</strong> This is not an error — it
        is an honest reflection of the project&apos;s current evidence state. See{" "}
        <a href="/pipeline">the pipeline page</a> for exactly which stage this depends on.
      </div>
      <h2>Planned work</h2>
      <ul>
        {plan.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
