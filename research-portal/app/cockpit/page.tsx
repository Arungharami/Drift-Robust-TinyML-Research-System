import type { Metadata } from "next";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { getPipeline, getResearchIntelligence, getXai } from "@/lib/evidence";

export const metadata: Metadata = { title: "Research Cockpit" };

export default function CockpitPage() {
  const intel = getResearchIntelligence();
  const pipeline = getPipeline();
  const xai = getXai();
  const blocked = pipeline.filter((s) => s.status === "BLOCKED" || s.status === "NOT_EXECUTED");
  const supported = intel.registries.claims.filter((c) => c.status === "SUPPORTED");
  const unsupported = intel.registries.claims.filter((c) => c.status !== "SUPPORTED");
  const latest = intel.registries.experiments.at(-1);
  const latestArtifact = intel.registries.artifacts.at(-1);
  return <div className="container">
    <div className="section-label">Research intelligence</div><h1>Research Cockpit</h1>
    <p className="lede">What is evidenced, what is not, and why the next experiment exists.</p>
    <div className="card-grid">
      <div className="card"><div className="section-label">Evidence system</div><EvidenceBadge status={intel.evidence_status} /><p>{intel.registries.experiments.length} normalized experiments; {intel.registries.artifacts.length} hashed artifacts.</p></div>
      <div className="card"><div className="section-label">Claims</div><span className="metric-value">{supported.length}</span><span className="metric-unit"> supported</span><p>{unsupported.length} unsupported or pending.</p></div>
      <div className="card"><div className="section-label">Next experiment</div><code>{intel.next_experiment}</code><p>Stage 11 produced mixed evidence; Stage 12 remains unexecuted pending a separately frozen protocol.</p></div>
      <div className="card"><div className="section-label">Largest blocker</div><EvidenceBadge status="BLOCKED" /><p>{intel.hardware_blocker}</p></div>
    </div>
    <h2>Current frontier</h2>
    <div className="kv-grid"><div className="kv-item"><div className="k">Latest registered experiment</div><div className="v">{latest?.experiment_id ?? "NONE"}</div></div><div className="kv-item"><div className="k">Latest registered artifact</div><div className="v">{latestArtifact?.path ?? "NONE"}</div></div><div className="kv-item"><div className="k">Feature ontology</div><div className="v">{intel.feature_structure.physical_sensors} sensors × {intel.feature_structure.features_per_sensor} responses</div></div><div className="kv-item"><div className="k">Blocked/pending stages</div><div className="v">{blocked.length}</div></div></div>
    <h2>Blocked dependencies</h2><div className="table-scroll"><table><thead><tr><th>Stage</th><th>State</th><th>Requirement</th></tr></thead><tbody>{blocked.map(s => <tr key={s.id}><td>{s.id} — {s.name}</td><td><EvidenceBadge status={s.status} /></td><td>{s.notes}</td></tr>)}</tbody></table></div>
    <h2>Fidelity × stability evidence matrix</h2><p>Interpretation is <code>MIXED</code> when both stages executed but their broad candidate claims remain unsupported. This is not a trustworthiness label.</p>
    <div className="table-scroll"><table><thead><tr><th>Model</th><th>Method</th><th>Fidelity evidence</th><th>Stability evidence</th><th>Interpretation</th></tr></thead><tbody>{xai.fidelity_stability_link.map((row, i) => <tr key={i}><td>{row.model_id}</td><td><code>{row.method}</code></td><td>{row.fidelity_metric}</td><td>Spearman {Number(row.spearman).toFixed(3)} [{Number(row.ci_low).toFixed(3)}, {Number(row.ci_high).toFixed(3)}], N={row.n}</td><td><code>MIXED</code></td></tr>)}</tbody></table></div>
    <h2>Pre-hardware fidelity × stability × cost</h2>
    <p><strong>Host latency is not an estimate of nRF52840 latency or energy.</strong> Missing evidence remains missing; no zeroes or composite trust score are substituted.</p>
    <div className="table-scroll"><table><thead><tr><th>Model</th><th>Method</th><th>Fidelity</th><th>Stability</th><th>Host cost</th><th>MCU cost</th></tr></thead><tbody>{xai.latency_tradeoff.map((row, i) => <tr key={i}><td>{row.model_id}</td><td><code>{row.method}</code><br /><small>{row.scope}</small></td><td>{row.stage10_fidelity_evidence && row.stage10_fidelity_evidence !== "nan" ? Number(row.stage10_fidelity_evidence).toFixed(4) : "NOT_MEASURED"}</td><td>{row.stage11_stability_evidence && row.stage11_stability_evidence !== "nan" ? Number(row.stage11_stability_evidence).toFixed(4) : "NOT_MEASURED"}</td><td>{Number(row.median_us).toLocaleString(undefined, { maximumFractionDigits: 3 })} µs median</td><td><code>NOT_MEASURED</code></td></tr>)}</tbody></table></div>
  </div>;
}
