import { EvidenceBadge } from "./EvidenceBadge";
import { ArtifactLink } from "./ArtifactLink";
import type { PipelineStage as PipelineStageT } from "@/lib/types";

export function PipelineStageCard({ stage }: { stage: PipelineStageT }) {
  return (
    <div className="card card-stack">
      <div className="card-heading-row">
        <div>
          <div className="section-label">Stage {stage.id}</div>
          <h3 style={{ margin: "0.1rem 0 0.4rem" }}>{stage.name}</h3>
        </div>
        <EvidenceBadge status={stage.status} />
      </div>
      <p style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>{stage.notes}</p>
      <div className="kv-grid" style={{ marginTop: "0.5rem" }}>
        <div className="kv-item">
          <div className="k">Notebook</div>
          <div className="v">
            {stage.notebook ? <ArtifactLink path={stage.notebook} commit={stage.git_commit ?? undefined} /> : "—"}
          </div>
        </div>
        <div className="kv-item">
          <div className="k">Script</div>
          <div className="v">
            {stage.script ? <ArtifactLink path={stage.script} commit={stage.git_commit ?? undefined} /> : "—"}
          </div>
        </div>
        <div className="kv-item">
          <div className="k">Depends on</div>
          <div className="v">{stage.depends_on.length ? stage.depends_on.join(", ") : "—"}</div>
        </div>
        <div className="kv-item">
          <div className="k">Git commit</div>
          <div className="v">{stage.git_commit ? stage.git_commit.slice(0, 7) : "—"}</div>
        </div>
      </div>
      {stage.artifact_paths.length > 0 && (
        <div style={{ marginTop: "0.5rem" }}>
          <div className="k" style={{ fontSize: "0.72rem", textTransform: "uppercase", color: "var(--text-faint)" }}>
            Artifacts
          </div>
          <ul style={{ margin: "0.3rem 0 0", paddingLeft: "1.1rem", fontSize: "0.85rem" }}>
            {stage.artifact_paths.map((p) => (
              <li key={p}>
                <ArtifactLink path={p} commit={stage.git_commit ?? undefined} />
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
