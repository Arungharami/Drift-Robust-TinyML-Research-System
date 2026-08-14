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

      <h2>Validation stage status</h2>
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
      {xai.fidelity_status === "EXECUTED" && <>
        <h2>Stage 10 fidelity</h2>
        <p className="lede">Experiment <code>{xai.fidelity_experiment_id}</code> tested whether ranked inputs actually influence frozen model behavior under controlled Batch-1-reference perturbations.</p>
        <h3>What does fidelity mean here?</h3>
        <p>Fidelity means that features identified as important change the frozen model&apos;s behavior when experimentally perturbed. It is not human interpretability, causal truth, chemical causality, or model accuracy.</p>
        <div className="card-grid">
          <div className="card"><div className="section-label">Method/scope summaries</div><span className="metric-value">{xai.fidelity_summary.length}</span></div>
          <div className="card"><div className="section-label">Bootstrap intervals</div><span className="metric-value">{xai.fidelity_ci_count}</span></div>
        </div>
        <div className="table-scroll"><table><thead><tr><th>Scope</th><th>Model</th><th>Method</th><th>Mean selected − random</th><th>N</th><th>Unit</th></tr></thead><tbody>{xai.fidelity_summary.map((row, i) => <tr key={i}><td>{row.scope}</td><td>{row.model_id}</td><td><code>{row.method}</code></td><td>{Number(row.mean).toFixed(4)}</td><td>{row.n}</td><td>{row.unit}</td></tr>)}</tbody></table></div>
        <p>Results are heterogeneous; no universal explanation-fidelity claim is made. Local ablation is cumulative ablation consistency because its evaluation is partly circular.</p>
        <ul>{xai.fidelity_artifact_paths.map(path => <li key={path}><ArtifactLink path={path} /></li>)}</ul>
      </>}
      {xai.stability_status === "EXECUTED" && <>
        <h2>Stage 11 stability under chronological drift</h2>
        <p className="lede">Experiment <code>{xai.stability_experiment_id}</code> separates explanation change from input change and frozen-model output change.</p>
        <h3>What does stability mean here?</h3>
        <p>Stability asks whether similar model situations produce similar explanations, and whether explanation changes are proportionate to actual changes in sensor inputs or model behavior.</p>
        <h3>Stability does not mean</h3><ul><li>The explanation is faithful or causal.</li><li>The model is accurate.</li><li>Sensors are physically unchanged.</li><li>The same explanation should persist under real drift.</li></ul>
        <div className="card-grid"><div className="card"><div className="section-label">Method/scope summaries</div><span className="metric-value">{xai.stability_summary.length}</span></div><div className="card"><div className="section-label">Bootstrap intervals</div><span className="metric-value">{xai.stability_ci_count}</span></div></div>
        <div className="table-scroll"><table><thead><tr><th>Scope</th><th>Model</th><th>Method</th><th>Metric</th><th>Mean</th><th>N</th></tr></thead><tbody>{xai.stability_summary.map((row, i) => <tr key={i}><td>{row.scope}</td><td>{row.model_id}</td><td><code>{row.method}</code></td><td>{row.metric_name}</td><td>{Number(row.mean).toFixed(4)}</td><td>{row.n}</td></tr>)}</tbody></table></div>
        <p>Evidence is method- and context-dependent. Intrinsic global vectors marked <code>ALL</code> were not fabricated into chronological series, and matched cross-batch samples are cross-sectional rather than longitudinal.</p>
        <ul>{xai.stability_artifact_paths.map(path => <li key={path}><ArtifactLink path={path} /></li>)}</ul>
      </>}
      {xai.latency_status === "EXECUTED" && <>
        <h2>Computational cost</h2>
        <p className="lede">Experiment <code>{xai.latency_experiment_id}</code> measured warm, steady-state host computation with raw nanosecond timing and verified single-thread controls.</p>
        <div className="card-grid">
          <div className="card"><div className="section-label">Host measured</div><EvidenceBadge status="EXECUTED" /><p>Median, p95, N, model, method, scope, environment, and artifact are retained below.</p></div>
          <div className="card"><div className="section-label">MCU not measured</div><EvidenceBadge status="NOT_EXECUTED" /><p>Physical nRF52840 latency, energy, Flash, and SRAM remain unmeasured.</p></div>
        </div>
        <p><strong>Host latency is not an estimate of nRF52840 latency or energy.</strong></p>
        <div className="table-scroll"><table><thead><tr><th>Scope</th><th>Model</th><th>Method / phase</th><th>Median (µs)</th><th>p95 (µs)</th><th>N</th><th>Environment</th><th>Experiment</th></tr></thead><tbody>
          {xai.latency_summary.filter(row => ["EXPLANATION_COMPUTE", "ONE_TIME_GLOBAL_EXTRACTION_COST", "GLOBAL_EXPLANATION_TOTAL"].includes(row.phase ?? "")).map((row, i) => <tr key={i}><td>{row.scope}</td><td>{row.model_id}</td><td><code>{row.method}</code><br /><small>{row.phase}</small></td><td>{Number(row.median_us).toLocaleString(undefined, { maximumFractionDigits: 3 })}</td><td>{Number(row.p95_us).toLocaleString(undefined, { maximumFractionDigits: 3 })}</td><td>{row.n}</td><td>{row.environment_id}</td><td><code>{row.experiment_id}</code></td></tr>)}
        </tbody></table></div>
        <p>Global dataset procedures and local per-sample methods are intentionally separate; this is not a universal method leaderboard. Top-k reduction and serialization are separate phases.</p>
        <h3>Claim evaluation</h3>
        <div className="table-scroll"><table><thead><tr><th>Claim</th><th>Status</th><th>Evidence</th></tr></thead><tbody>{xai.latency_claims.map(row => <tr key={row.claim_id}><td><code>{row.claim_id}</code></td><td>{row.status}</td><td>{row.evidence_summary}</td></tr>)}</tbody></table></div>
        <p>Primary artifact: <ArtifactLink path="results/xai/stage12_raw_timings.csv" />. Full report: <ArtifactLink path="docs/experiments/STAGE12_XAI_LATENCY.md" />.</p>
      </>}
    </div>
  );
}
