import { EvidenceBadge } from "@/components/EvidenceBadge";
import type { EvidenceStatus } from "@/lib/types";

const DIMENSIONS = [
  { id: "accuracy", label: "Accuracy", question: "Is the prediction correct?" },
  { id: "explanation", label: "Explanation", question: "Can we understand why the model predicted it?" },
  { id: "deployability", label: "Deployability", question: "Can the model realistically operate on constrained hardware?" },
] as const;

/**
 * Section 9 — a conceptual research framework, not a claim that all three dimensions have been
 * jointly proven. Each dimension's badge is this project's own real, current evidence status.
 */
export function TrustFramework({
  accuracyStatus,
  explanationStatus,
  deployabilityStatus,
}: {
  accuracyStatus: EvidenceStatus;
  explanationStatus: EvidenceStatus;
  deployabilityStatus: EvidenceStatus;
}) {
  const statusById: Record<(typeof DIMENSIONS)[number]["id"], EvidenceStatus> = {
    accuracy: accuracyStatus,
    explanation: explanationStatus,
    deployability: deployabilityStatus,
  };

  return (
    <section className="threemt-trust" aria-labelledby="threemt-trust-title">
      <h2 id="threemt-trust-title">Accuracy Is Not Enough.</h2>
      <div className="card-grid">
        {DIMENSIONS.map((d) => (
          <div className="card" key={d.id}>
            <div className="section-label">{d.label}</div>
            <p style={{ marginBottom: "0.6rem" }}>{d.question}</p>
            <EvidenceBadge status={statusById[d.id]} />
          </div>
        ))}
      </div>
      <div className="threemt-trust-intersection">
        <span className="threemt-trust-intersection-label">Trust</span>
        <p className="threemt-trust-intersection-note">
          the intersection of all three — a research framework this project measures toward, not
          a claim that all three are already jointly demonstrated on physical hardware.
        </p>
      </div>
    </section>
  );
}
