import { EvidenceBadge } from "./EvidenceBadge";
import { ArtifactLink } from "./ArtifactLink";
import type { ExperimentRecord } from "@/lib/types";

export function ExperimentCard({ experiment }: { experiment: ExperimentRecord }) {
  const status = experiment.status === "COMPLETED" ? "EXECUTED" : experiment.status;
  return (
    <div className="card card-stack">
      <div className="card-heading-row">
        <div>
          <div className="section-label">{experiment.protocol}</div>
          <h3 style={{ margin: "0.1rem 0 0.3rem" }}>{experiment.experiment_id}</h3>
        </div>
        <EvidenceBadge status={status as never} />
      </div>
      <p style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>{experiment.research_question}</p>
      <div className="kv-grid">
        <div className="kv-item">
          <div className="k">Model</div>
          <div className="v">{experiment.model}</div>
        </div>
        <div className="kv-item">
          <div className="k">Train batches</div>
          <div className="v">{experiment.train_batches || "—"}</div>
        </div>
        <div className="kv-item">
          <div className="k">Test batches</div>
          <div className="v">{experiment.test_batches || "—"}</div>
        </div>
        <div className="kv-item">
          <div className="k">Seed</div>
          <div className="v">{experiment.seed}</div>
        </div>
        <div className="kv-item">
          <div className="k">Git commit</div>
          <div className="v">{experiment.git_commit?.slice(0, 7) || "—"}</div>
        </div>
        <div className="kv-item">
          <div className="k">Timestamp</div>
          <div className="v">{experiment.timestamp}</div>
        </div>
      </div>
      {experiment.metrics_artifact ? (
        <p style={{ fontSize: "0.85rem", marginTop: "0.5rem", marginBottom: 0 }}>
          Metrics: <ArtifactLink path={experiment.metrics_artifact.replace(/\\/g, "/")} commit={experiment.git_commit} />
        </p>
      ) : null}
      {experiment.notes ? (
        <p style={{ fontSize: "0.8rem", color: "var(--text-faint)", marginTop: "0.4rem", marginBottom: 0 }}>
          {experiment.notes}
        </p>
      ) : null}
    </div>
  );
}
