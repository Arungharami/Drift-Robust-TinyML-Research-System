import { ArchitectureDiagram } from "@/components/ArchitectureDiagram";
import { MetricCard } from "@/components/MetricCard";
import { getDataset, getProjectStatus } from "@/lib/evidence";

export default function HomePage() {
  const dataset = getDataset();
  const status = getProjectStatus();
  const v = dataset.validation;

  return (
    <div className="container">
      <div className="section-label">Research system</div>
      <h1>Drift-Robust Explainable TinyML for Electronic-Nose Sensing</h1>
      <p className="lede">
        Chronological Evaluation, Resource-Aware Explanations, and Reproducible Edge Deployment
      </p>

      <p style={{ maxWidth: "62ch" }}>
        This project studies three linked ideas: (1) electronic-nose sensors drift over time,
        degrading naive machine-learning performance; (2) explanation methods for those models
        must themselves be evaluated for cost and stability, not assumed reliable; and (3) any
        claim about TinyML deployment must be backed by real embedded measurements, not software
        proxies. The site below distinguishes executed evidence from planned work throughout —
        see the <a href="/reproducibility">reproducibility policy</a>.
      </p>

      <ArchitectureDiagram />

      <div className="btn-row">
        <a className="btn btn-primary" href="/methodology">Explore Methodology</a>
        <a className="btn" href="/experiments">View Experiments</a>
        <a className="btn" href="/reproducibility">Reproduce Research</a>
        <a className="btn" href={`https://github.com/${status.repository}`} target="_blank" rel="noreferrer">View Source</a>
        <a className="btn" href="/paper">Open Paper</a>
        <a className="btn" href="/huggingface">Hugging Face</a>
      </div>

      <h2>Dataset, at a glance</h2>
      <div className="card-grid">
        <MetricCard label="Observations" value={v?.samples ?? null} status={dataset.evidence_status} />
        <MetricCard label="Features" value={v?.features ?? null} status={dataset.evidence_status} />
        <MetricCard label="Chronological batches" value={v?.batches ?? null} status={dataset.evidence_status} />
        <MetricCard label="Gas classes" value={v?.classes ?? null} status={dataset.evidence_status} />
      </div>
      <p style={{ fontSize: "0.88rem" }}>
        <a href="/dataset">Full dataset documentation and verified archive hash →</a>
      </p>

      <h2>Pipeline status</h2>
      <div className="card-grid">
        {Object.entries(status.pipeline_stage_counts).map(([key, count]) => (
          <div className="card" key={key}>
            <div className="section-label">{key.replace("_", " ")}</div>
            <span className="metric-value">{count}</span>
            <span className="metric-unit">/ {status.pipeline_total_stages} stages</span>
          </div>
        ))}
      </div>
      <p style={{ fontSize: "0.88rem" }}>
        <a href="/pipeline">Full 23-stage pipeline with artifacts and dependencies →</a>
      </p>
    </div>
  );
}
