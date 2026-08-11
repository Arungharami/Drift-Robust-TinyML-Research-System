import type { Metadata } from "next";
import { ArtifactLink } from "@/components/ArtifactLink";
import { getResearchIntelligence } from "@/lib/evidence";

export const metadata: Metadata = { title: "Failure Analysis" };

export default function FailureAnalysisPage() {
  const intel = getResearchIntelligence();
  const byModel = new Map<string, Record<string, string>>();
  for (const row of intel.failure_rows) {
    const key = row.model ?? "UNKNOWN";
    const previous = byModel.get(key);
    if (!previous || Number(row.macro_f1) < Number(previous.macro_f1)) byModel.set(key, row);
  }
  return <div className="container"><div className="section-label">Negative and limiting evidence</div><h1>Failure Analysis</h1><p className="lede">Worst chronological cases are computed from the registered fixed-origin metric artifact. Confidence and adaptation conclusions remain absent unless their dedicated analyses execute.</p>
    <div className="card-grid">{[...byModel.entries()].map(([model, row]) => <article className="card" key={model}><div className="section-label">What failed?</div><h3>{model}</h3><dl><dt>When</dt><dd>Batch {row.test_batch}</dd><dt>How badly</dt><dd>Macro-F1 {Number(row.macro_f1).toFixed(3)}</dd><dt>Protocol</dt><dd>{row.protocol}</dd><dt>Experiment</dt><dd><code>{row.experiment_id}</code></dd></dl><p>Dominant sensors, confidently-wrong behavior, and recovery attribution require registered sensor/error joins; they are not inferred here.</p></article>)}</div>
    <p>Source: <ArtifactLink path="results/baselines/fixed_origin_metrics.csv" />. Unit: proportion; protocol: fixed origin, train Batch 1/test Batches 2–10.</p></div>;
}
