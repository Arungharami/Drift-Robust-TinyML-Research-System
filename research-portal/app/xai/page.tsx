import type { Metadata } from "next";
import { ArtifactLink } from "@/components/ArtifactLink";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { formatPercent, getXai } from "@/lib/evidence";
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
            retraining. Stage 10 has now evaluated behavioral fidelity from these saved
            explanations; stability and latency remain <code>NOT EXECUTED</code>.
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

          <h2>Stage 10 behavioral fidelity</h2>
          <div style={{ marginBottom: "0.75rem" }}>
            <EvidenceBadge status={xai.fidelity_status} />
          </div>
          {xai.fidelity_status === "EXECUTED" && (
            <>
              <p style={{ fontSize: "0.88rem", color: "var(--text-muted)" }}>
                Experiment <code>{xai.fidelity_experiment_id}</code> evaluated{" "}
                {xai.n_fidelity_rows.toLocaleString()} model/sample/top-k cases. No pass/fail
                threshold was preregistered. MODEL-C2-C4 use the ablation ranking as both
                candidate and reference, so their perfect overlap is identity rather than
                independent validation.
              </p>
              <div className="table-scroll">
                <table>
                  <thead><tr><th>Model</th><th>Candidate</th><th>k</th><th>Overlap</th><th>Preserved</th><th>Closeness</th><th>Abs. sufficiency gap</th><th>Comprehensiveness</th></tr></thead>
                  <tbody>
                    {xai.fidelity_summary.map((row, i) => (
                      <tr key={i}>
                        <td>{row.model_id}</td>
                        <td><code style={{ fontSize: "0.72rem" }}>{row.candidate_method}</code></td>
                        <td>{row.top_k}</td>
                        <td>{formatPercent(row.mean_rank_overlap_at_k)}</td>
                        <td>{formatPercent(row.candidate_prediction_preservation_rate)}</td>
                        <td>{formatPercent(row.mean_candidate_probability_closeness)}</td>
                        <td>{formatPercent(row.mean_candidate_absolute_sufficiency_gap)}</td>
                        <td>{formatPercent(row.mean_candidate_comprehensiveness_drop)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p style={{ fontSize: "0.85rem" }}>
                Protocol, selected results, hashes, and limitations:{" "}
                <ArtifactLink path="docs/experiments/STAGE10_EXPLANATION_FIDELITY.md" />.
              </p>
              <h3>Stage 10 artifacts</h3>
              <ul style={{ fontSize: "0.9rem" }}>
                {xai.fidelity_artifact_paths.map((path) => (
                  <li key={path}><ArtifactLink path={path} /></li>
                ))}
              </ul>
            </>
          )}

          <h2>Stage 11 chronological stability</h2>
          <div style={{ marginBottom: "0.75rem" }}>
            <EvidenceBadge status={xai.stability_status} />
          </div>
          {xai.stability_status === "EXECUTED" && (
            <>
              <p style={{ fontSize: "0.88rem", color: "var(--text-muted)" }}>
                Experiment <code>{xai.stability_experiment_id}</code> contains{" "}
                {xai.n_stability_pairwise_rows} chronological comparisons. No stability
                threshold was preregistered; the table reports distribution-specific
                observations only.
              </p>
              <div className="table-scroll">
                <table>
                  <thead><tr><th>Model</th><th>Mean Spearman vs B2</th><th>Minimum vs B2</th><th>Mean adjacent</th><th>Cosine vs B2</th><th>Top-10 Jaccard</th><th>Top-1 Jaccard</th></tr></thead>
                  <tbody>
                    {xai.stability_summary.map((row) => (
                      <tr key={row.model_id}>
                        <td>{row.model_id}</td>
                        <td>{Number(row.mean_reference_spearman).toFixed(3)}</td>
                        <td>{Number(row.minimum_reference_spearman).toFixed(3)}</td>
                        <td>{Number(row.mean_adjacent_spearman).toFixed(3)}</td>
                        <td>{Number(row.mean_reference_cosine).toFixed(3)}</td>
                        <td>{formatPercent(row.mean_reference_top_10_jaccard)}</td>
                        <td>{formatPercent(row.mean_reference_top_1_jaccard)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p style={{ fontSize: "0.85rem" }}>
                Protocol, exact aggregates, and limitations:{" "}
                <ArtifactLink path="docs/experiments/STAGE11_EXPLANATION_STABILITY.md" />.
              </p>
              <h3>Stage 11 artifacts</h3>
              <ul style={{ fontSize: "0.9rem" }}>
                {xai.stability_artifact_paths.map((path) => (
                  <li key={path}><ArtifactLink path={path} /></li>
                ))}
              </ul>
            </>
          )}

          <h2>Stage 12 host-side latency</h2>
          <EvidenceBadge status={xai.latency_status} />
          {xai.latency_status === "EXECUTED" && (
            <>
              <p style={{ fontSize: "0.88rem", color: "var(--text-muted)" }}>
                Experiment <code>{xai.latency_experiment_id}</code> contains {xai.n_latency_raw_rows}
                {" "}timings from one shared GitHub runner. These are not on-device measurements.
              </p>
              <div className="table-scroll"><table>
                <thead><tr><th>Model</th><th>Method</th><th>n</th><th>Median ms</th><th>p95 ms</th></tr></thead>
                <tbody>{xai.latency_summary.map((row) => <tr key={row.model_id + row.method}>
                  <td>{row.model_id}</td><td><code>{row.method}</code></td><td>{row.n_measurements}</td>
                  <td>{Number(row.median_latency_ms).toFixed(3)}</td><td>{Number(row.p95_latency_ms).toFixed(3)}</td>
                </tr>)}</tbody>
              </table></div>
              <p><ArtifactLink path="docs/experiments/STAGE12_HOST_EXPLANATION_LATENCY.md" /></p>
            </>
          )}

          <h2>Stage 09 artifacts</h2>
          <ul style={{ fontSize: "0.9rem" }}>
            {xai.artifact_paths.map((path) => (
              <li key={path}><ArtifactLink path={path} /></li>
            ))}
          </ul>
        </>
      )}

      <h2>Downstream measurement status</h2>
      <p style={{ fontSize: "0.88rem", color: "var(--text-muted)" }}>
        Stages 10-12 are complete on host; physical/on-device timing remains unexecuted.
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
