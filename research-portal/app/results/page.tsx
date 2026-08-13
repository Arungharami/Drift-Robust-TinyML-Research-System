import type { Metadata } from "next";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { ArtifactLink } from "@/components/ArtifactLink";
import { BatchMetricLineChart, ModelBarChart } from "@/components/ResultsCharts";
import { getBaselines, getDrift, githubRawUrl } from "@/lib/evidence";

export const metadata: Metadata = { title: "Results" };

const MODELS = ["MODEL-C1", "MODEL-C2", "MODEL-C3", "MODEL-C4"];

function pivotByBatch(rows: Record<string, string>[], metric: string) {
  const byBatch = new Map<string, Record<string, number | string>>();
  for (const row of rows) {
    const batch = row.test_batch ?? "";
    const model = row.model ?? "";
    if (!batch) continue;
    if (!byBatch.has(batch)) byBatch.set(batch, { test_batch: Number(batch) });
    const entry = byBatch.get(batch)!;
    entry[`${model}_${metric}`] = Number(row[metric] ?? NaN);
  }
  return Array.from(byBatch.values()).sort((a, b) => Number(a.test_batch) - Number(b.test_batch));
}

const EMPTY: { label: string; unit: string }[] = [
  { label: "Explanation fidelity", unit: "agreement score" },
  { label: "Explanation stability", unit: "rank correlation" },
  { label: "Explanation latency", unit: "ms" },
  { label: "Inference latency (physical)", unit: "ms" },
  { label: "Flash footprint", unit: "KB" },
  { label: "SRAM footprint", unit: "KB" },
  { label: "Inference energy (PPK2)", unit: "µJ" },
  { label: "Pareto frontier (accuracy / trust / resource)", unit: "n/a" },
];

export default function ResultsPage() {
  const baselines = getBaselines();
  const drift = getDrift();
  const accuracyData = pivotByBatch(baselines.fixed_origin_by_batch, "accuracy");
  const f1Data = pivotByBatch(baselines.fixed_origin_by_batch, "macro_f1");
  const dropData = baselines.fixed_origin_summary.map((r) => ({
    model: r.model ?? "unknown",
    value: Number(r.b2_to_b10_accuracy_drop_pp ?? NaN),
  }));
  const gapData = baselines.iid_generalization_gap.map((r) => ({
    model: r.model ?? "unknown",
    value: Number(r.accuracy_gap ?? NaN),
  }));

  return (
    <div className="container">
      <div className="section-label">Results</div>
      <div style={{ marginBottom: "0.75rem" }}>
        <EvidenceBadge status={baselines.evidence_status} />
      </div>
      <h1>Results dashboard</h1>
      <p className="lede">
        Every chart below is generated at build time directly from CSV artifacts in{" "}
        <code>results/baselines/</code> and <code>results/drift/</code> — see{" "}
        <ArtifactLink path="results/baselines/fixed_origin_summary.csv" /> and{" "}
        <ArtifactLink path="results/drift/global_drift_by_batch.csv" />.
      </p>

      <h2>Accuracy by chronological test batch (FIXED_ORIGIN)</h2>
      <BatchMetricLineChart data={accuracyData} metricKey="accuracy" models={MODELS} yLabel="Accuracy" />

      <h2>Macro-F1 by chronological test batch (FIXED_ORIGIN)</h2>
      <BatchMetricLineChart data={f1Data} metricKey="macro_f1" models={MODELS} yLabel="Macro-F1" />

      <h2>Drift degradation: accuracy drop, Batch 2 → Batch 10</h2>
      <ModelBarChart data={dropData} dataKey="accuracy drop (pp)" yLabel="Percentage points" />
      <p style={{ fontSize: "0.85rem" }}>
        Every evaluated model loses accuracy from Batch 2 to Batch 10 under FIXED_ORIGIN — see{" "}
        <ArtifactLink path="paper/claim_evidence_matrix.csv" label="claim C003" />.
      </p>

      <h2>IID vs. chronological generalization gap</h2>
      <ModelBarChart data={gapData} dataKey="accuracy gap" yLabel="Accuracy gap (IID − chronological mean)" />
      <p style={{ fontSize: "0.85rem" }}>
        The stratified-random IID diagnostic accuracy exceeds mean chronological future-batch
        accuracy for every model — quantifying how much a random split overstates performance
        (claim C005, <em>diagnostic only, never a primary result</em>).
      </p>

      <h2>Host-serialized model size</h2>
      <p style={{ fontSize: "0.85rem" }}>
        Serialized (joblib, host CPU) size — <strong>not</strong> an embedded or quantized
        footprint. Flash/SRAM figures remain <code>NOT EXECUTED</code> until stage 16.
      </p>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Model</th><th>Serialized size</th><th>Complexity detail</th></tr></thead>
          <tbody>
            {baselines.model_complexity.map((row) => (
              <tr key={row.model}>
                <td>{row.model_name}</td>
                <td>{(Number(row.serialized_host_bytes) / 1024).toFixed(1)} KB</td>
                <td style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
                  {row.tree_count ? `${row.tree_count} trees, depth ${row.max_tree_depth}` : null}
                  {row.support_vector_count ? `${row.support_vector_count} support vectors` : null}
                  {row.layer_dimensions ? `layers ${row.layer_dimensions}` : null}
                  {row.coefficient_count ? `${row.coefficient_count} coefficients` : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Global feature drift vs. Batch 1</h2>
      {drift.global_drift_by_batch.length > 0 ? (
        <div className="figure">
          {/* eslint-disable-next-line @next/next/no-img-element -- SVG figure from GitHub; next/image's raster pipeline isn't a fit for vector output */}
          <img
            src={githubRawUrl("results/figures/global_drift_trajectory.svg")}
            alt="Global drift trajectory across chronological batches"
          />
          <figcaption>
            Median normalized Wasserstein distance and standardized mean shift, batches 2–10 vs.
            Batch 1. Source: <ArtifactLink path="results/drift/global_drift_by_batch.csv" />
          </figcaption>
        </div>
      ) : (
        <div className="empty-state">Measurement not executed yet.</div>
      )}

      <h2>Generated figures and tables</h2>
      <p style={{ fontSize: "0.88rem" }}>
        15 figures and 5 publication tables are generated directly from evidence — browse the
        full index on <a href="/paper">the Paper page</a>.
      </p>

      <h2>Not yet executed</h2>
      <p style={{ fontSize: "0.88rem", color: "var(--text-muted)" }}>
        Per-class F1, confusion matrices (see figure gallery on the Paper page for the
        chronological confusion-matrix evolution figure — that one already exists), explanation
        fidelity, explanation stability, latency, Flash/SRAM, and energy remain below.
      </p>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Measurement</th><th>Unit</th><th>Status</th></tr></thead>
          <tbody>
            {EMPTY.map((row) => (
              <tr key={row.label}>
                <td>{row.label}</td>
                <td>{row.unit}</td>
                <td><EvidenceBadge status="NOT_EXECUTED" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
