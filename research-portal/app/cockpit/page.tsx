import type { Metadata } from "next";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { getPipeline, getResearchIntelligence } from "@/lib/evidence";

export const metadata: Metadata = { title: "Research Cockpit" };

export default function CockpitPage() {
  const intel = getResearchIntelligence();
  const pipeline = getPipeline();
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
      <div className="card"><div className="section-label">Next experiment</div><code>{intel.next_experiment}</code><p>Method-specific Stage 10 fidelity; Stage 09 generation alone is not fidelity evidence.</p></div>
      <div className="card"><div className="section-label">Largest blocker</div><EvidenceBadge status="BLOCKED" /><p>{intel.hardware_blocker}</p></div>
    </div>
    <h2>Current frontier</h2>
    <div className="kv-grid"><div className="kv-item"><div className="k">Latest registered experiment</div><div className="v">{latest?.experiment_id ?? "NONE"}</div></div><div className="kv-item"><div className="k">Latest registered artifact</div><div className="v">{latestArtifact?.path ?? "NONE"}</div></div><div className="kv-item"><div className="k">Feature ontology</div><div className="v">{intel.feature_structure.physical_sensors} sensors × {intel.feature_structure.features_per_sensor} responses</div></div><div className="kv-item"><div className="k">Blocked/pending stages</div><div className="v">{blocked.length}</div></div></div>
    <h2>Blocked dependencies</h2><div className="table-scroll"><table><thead><tr><th>Stage</th><th>State</th><th>Requirement</th></tr></thead><tbody>{blocked.map(s => <tr key={s.id}><td>{s.id} — {s.name}</td><td><EvidenceBadge status={s.status} /></td><td>{s.notes}</td></tr>)}</tbody></table></div>
  </div>;
}
