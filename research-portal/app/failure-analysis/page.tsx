import type { Metadata } from "next";
import { ArtifactLink } from "@/components/ArtifactLink";
import { getResearchIntelligence, getXai } from "@/lib/evidence";

export const metadata: Metadata = { title: "Failure Analysis" };

export default function FailureAnalysisPage() {
  const intel = getResearchIntelligence();
  const xai = getXai();
  const byModel = new Map<string, Record<string, string>>();
  for (const row of intel.failure_rows) {
    const key = row.model ?? "UNKNOWN";
    const previous = byModel.get(key);
    if (!previous || Number(row.macro_f1) < Number(previous.macro_f1)) byModel.set(key, row);
  }
  return <div className="container">
    <div className="section-label">Negative and limiting evidence</div><h1>Failure Analysis</h1>
    <p className="lede">Worst chronological cases and explanation behavior around frozen failure-context audit samples.</p>
    <div className="card-grid">{[...byModel.entries()].map(([model, row]) => <article className="card" key={model}><div className="section-label">What failed?</div><h3>{model}</h3><dl><dt>When</dt><dd>Batch {row.test_batch}</dd><dt>How badly</dt><dd>Macro-F1 {Number(row.macro_f1).toFixed(3)}</dd><dt>Protocol</dt><dd>{row.protocol}</dd><dt>Experiment</dt><dd><code>{row.experiment_id}</code></dd></dl></article>)}</div>
    <p>Source: <ArtifactLink path="results/baselines/fixed_origin_metrics.csv" />. Unit: proportion; fixed-origin protocol.</p>
    <h2>Explanation behavior around failure contexts</h2><p>Natural-neighbor stability summaries use frozen Stage 09 audit samples; they are not repeated observations of one physical event.</p>
    <div className="table-scroll"><table><thead><tr><th>Model</th><th>Context</th><th>N pairs</th><th>Explanation distance</th><th>Jaccard@10</th></tr></thead><tbody>{xai.stability_local_category_summary.map((row, i) => <tr key={i}><td>{row.model_id}</td><td>{row.category}</td><td>{row.n}</td><td>{row.mean_explanation_distance.toFixed(3)}</td><td>{row.mean_jaccard_at_10.toFixed(3)}</td></tr>)}</tbody></table></div>
    <p>Sources: <ArtifactLink path="results/xai/stage10_fidelity_local.csv" /> and <ArtifactLink path="results/xai/stage11_local_neighbor_stability.csv" />. The evidence does not support a general claim that explanations become less stable exactly when predictions fail.</p>
  </div>;
}
