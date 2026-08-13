import type { Metadata } from "next";
import { ArtifactLink } from "@/components/ArtifactLink";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { getXai } from "@/lib/evidence";
import type { EvidenceStatus } from "@/lib/types";

export const metadata: Metadata = { title: "XAI" };

export default function XaiPage() {
  const xai = getXai();

  return (
    <div className="container">
      <div className="section-label">Stage 09</div>
      <div style={{ marginBottom: "0.75rem" }}>
        <EvidenceBadge status={xai.evidence_status} />
      </div>
      <h1>Resource-aware explainability</h1>
      <p className="lede">
        {xai.evidence_status === "EXECUTED" ? (
          <>
            Experiment <code>{xai.experiment_id}</code> — explanations generated for the four
            evidence-selected FIXED_ORIGIN models, loaded from their frozen artifacts with no
            retraining. This stage prepares evidence for Stages 10-12; it does not itself report
            fidelity, stability, or latency conclusions (see below — all three remain{" "}
            <code>NOT EXECUTED</code>).
          </>
        ) : (
          "Explanation strategies suitable for constrained inference — evaluated for cost and fidelity, not assumed reliable."
        )}
      </p>

      {xai.evidence_status === "EXECUTED" && (
        <>
          <h2>What actually ran</h2>
          <div className="card-grid">
            <div className="card">
              <div className="section-label">Global importance rows</div>
              <span className="metric-value">{xai.n_global_rows.toLocaleString()}</span>
            </div>
            <div className="card">
              <div className="section-label">Local samples</div>
              <span className="metric-value">{xai.n_local_samples.toLocaleString()}</span>
            </div>
            <div className="card">
              <div className="section-label">Reduced top-k rows</div>
              <span className="metric-value">{xai.n_reduced_rows.toLocaleString()}</span>
            </div>
            <div className="card">
              <div className="section-label">Stage-10 fidelity-prep rows</div>
              <span className="metric-value">{xai.n_fidelity_prep_rows.toLocaleString()}</span>
            </div>
          </div>

          <h2>Method applicability — every model × method × scope</h2>
          <p style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
            No model was forced through a method it does not scientifically support — every{" "}
            <code>NOT_APPLICABLE</code> below carries the actual capability-detection reason.
          </p>
          <div className="table-scroll">
            <table>
              <thead><tr><th>Model</th><th>Method</th><th>Scope</th><th>Status</th><th>Reason</th></tr></thead>
              <tbody>
                {xai.applicability_matrix.map((row, i) => (
                  <tr key={i}>
                    <td>{row.model_id}</td>
                    <td><code>{row.method}</code></td>
                    <td>{row.scope}</td>
                    <td><EvidenceBadge status={(row.status === "EXECUTED" ? "EXECUTED" : row.status === "NOT_APPLICABLE" ? "BLOCKED" : "NOT_EXECUTED") as EvidenceStatus} /></td>
                    <td style={{ fontSize: "0.82rem", color: "var(--text-faint)" }}>{row.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h2>Top-3 features (Batch 2 / model-level)</h2>
          <div className="table-scroll">
            <table>
              <thead><tr><th>Model</th><th>Method</th><th>Batch</th><th>#1</th><th>#2</th><th>#3</th></tr></thead>
              <tbody>
                {xai.top3_by_model_method_batch.map((row, i) => (
                  <tr key={i}>
                    <td>{row.model_id}</td>
                    <td><code style={{ fontSize: "0.78rem" }}>{row.method}</code></td>
                    <td>{row.batch}</td>
                    {row.features.map((f, j) => <td key={j}>{f}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p style={{ fontSize: "0.85rem" }}>
            Rankings differ by model and method — an empirical observation, not a claim about
            which ranking is more correct (that is Stage 10&apos;s question). Full research note:{" "}
            <ArtifactLink path="docs/experiments/STAGE09_RESOURCE_AWARE_XAI.md" />.
          </p>

          <h2>Local sample categories</h2>
          <div className="card-grid">
            {Object.entries(xai.local_sample_categories).map(([category, count]) => (
              <div className="card" key={category}>
                <div className="section-label">{category.replace(/_/g, " ")}</div>
                <span className="metric-value">{count}</span>
              </div>
            ))}
          </div>

          <h2>Artifacts</h2>
          <ul style={{ fontSize: "0.9rem" }}>
            {xai.artifact_paths.map((path) => (
              <li key={path}><ArtifactLink path={path} /></li>
            ))}
          </ul>
        </>
      )}

      <h2>Not yet executed</h2>
      <p style={{ fontSize: "0.88rem", color: "var(--text-muted)" }}>
        Stage 09 prepares evidence; it does not itself compute these.
      </p>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Measurement</th><th>Status</th></tr></thead>
          <tbody>
            <tr><td>Explanation fidelity (Stage 10)</td><td><EvidenceBadge status={xai.fidelity_status} /></td></tr>
            <tr><td>Explanation stability across drift (Stage 11)</td><td><EvidenceBadge status={xai.stability_status} /></td></tr>
            <tr><td>Explanation latency (Stage 12)</td><td><EvidenceBadge status={xai.latency_status} /></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
