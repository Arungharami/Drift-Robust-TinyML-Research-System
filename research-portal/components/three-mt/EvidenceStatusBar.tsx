import Link from "next/link";
import type { ProjectStatus } from "@/lib/types";

/**
 * Section 13 — research status made prominent, not hidden at the bottom. Every count is read
 * directly from project-status.json (itself derived from configs/pipeline_stages.yaml), so this
 * bar can never drift out of sync with the registry it summarizes.
 */
export function EvidenceStatusBar({ project }: { project: ProjectStatus }) {
  const counts = Object.entries(project.pipeline_stage_counts).sort((a, b) => b[1] - a[1]);
  return (
    <section id="evidence-status" className="threemt-status-bar" aria-labelledby="threemt-status-title">
      <h2 id="threemt-status-title">Research Status</h2>
      <p style={{ maxWidth: "62ch" }}>
        This research tells you what was measured — and what was not. Every number below is the
        current <code>configs/pipeline_stages.yaml</code> registry, not a separate or more
        favorable accounting.
      </p>
      <div className="threemt-status-counts">
        {counts.map(([status, count]) => (
          <div key={status} className="threemt-status-count">
            <span className="threemt-status-count-value mono">
              {count} / {project.pipeline_total_stages}
            </span>
            <span className="threemt-status-count-label">{status.replace(/_/g, " ")}</span>
          </div>
        ))}
      </div>
      <p className="btn-row">
        <Link className="btn" href="/pipeline">
          Full Pipeline Registry
        </Link>
      </p>
    </section>
  );
}
