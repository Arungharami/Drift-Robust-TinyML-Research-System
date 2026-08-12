import type { Metadata } from "next";
import { ArtifactLink } from "@/components/ArtifactLink";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { getEmbedded } from "@/lib/evidence";

export const metadata: Metadata = { title: "Embedded Deployment" };

export default function TinyMlPage() {
  const embedded = getEmbedded();
  const fp32 = embedded.analytical_memory.filter(row => row.numeric_type === "FP32");
  return <div className="container">
    <div className="section-label">Stage 13 architecture gate</div>
    <div style={{ marginBottom: "0.75rem" }}><EvidenceBadge status="PROTOCOL_FROZEN" /></div>
    <h1>Embedded deployment</h1>
    <p className="lede">Target: {embedded.target.mcu}, {embedded.target.core}, {Number(embedded.target.clock_hz).toLocaleString()} Hz. Gate <code>{embedded.gate_id}</code> freezes architecture and equivalence criteria; it did not export a model.</p>

    <h2>Execution boundary</h2>
    <div className="table-scroll"><table><thead><tr><th>Item</th><th>Status</th></tr></thead><tbody>
      <tr><td>Protocol</td><td><code>FROZEN</code></td></tr>
      <tr><td>Model export</td><td><code>{embedded.statuses.model_export}</code></td></tr>
      <tr><td>Quantization</td><td><code>{embedded.statuses.quantization}</code></td></tr>
      <tr><td>Compiled Flash</td><td><code>{embedded.statuses.compiled_flash}</code></td></tr>
      <tr><td>SRAM</td><td><code>{embedded.statuses.sram}</code></td></tr>
      <tr><td>MCU latency</td><td><code>{embedded.statuses.mcu_latency}</code></td></tr>
      <tr><td>Energy</td><td><code>{embedded.statuses.energy}</code></td></tr>
    </tbody></table></div>

    <h2>Candidate tiers</h2>
    <div className="table-scroll"><table><thead><tr><th>Model</th><th>Confirmed type</th><th>Initial path</th><th>XAI path</th><th>Tier</th><th>Reason</th></tr></thead><tbody>{embedded.candidates.map(row => <tr key={row.candidate_id}><td>{row.model_id}</td><td>{row.model_type}</td><td><code>{row.export_path}</code></td><td>{row.XAI_method}</td><td><code>{row.status}</code></td><td>{row.reason}</td></tr>)}</tbody></table></div>

    {embedded.fp32_summary && <>
      <h2>Stage 14 host-compiled FP32 equivalence</h2>
      <p><strong>Host-compiled FP32 equivalence proves numerical portability of the implementation. It does not prove nRF52840 performance or resource feasibility.</strong></p>
      <p>Experiment <code>{embedded.fp32_summary.experiment_id}</code> completed with outcome <code>{embedded.fp32_summary.scientific_outcome}</code>. Both candidates retained every golden and boundary decision but failed frozen preprocessing criteria.</p>
      <div className="table-scroll"><table><thead><tr><th>Model</th><th>Status</th><th>Preprocess max abs</th><th>Preprocess max rel</th><th>Score max abs</th><th>Probability max abs</th><th>Golden</th><th>Boundary</th></tr></thead><tbody>{Object.entries(embedded.fp32_summary.candidates).map(([model, result]) => <tr key={model}><td>{model}</td><td><code>{result.status}</code></td><td>{result.max_preprocessing_absolute_error.toExponential(3)}</td><td>{result.max_preprocessing_relative_error.toExponential(3)}</td><td>{result.max_score_absolute_error.toExponential(3)}</td><td>{result.max_probability_absolute_error.toExponential(3)}</td><td>{(result.golden_agreement * 100).toFixed(0)}%</td><td>{(result.boundary_agreement * 100).toFixed(0)}%</td></tr>)}</tbody></table></div>
      <p>C1 local-XAI equivalence: <code>{embedded.fp32_summary.c1_xai_status}</code>. Quantization and MCU deployment remain <code>NOT_EXECUTED</code>.</p>
    </>}

    <h2>Analytical storage — derived estimate</h2>
    <p><strong>These values are not measured Flash or SRAM.</strong> They count raw scalar-equivalent parameters and omit compiled code, runtime metadata, stack, heap, buffers, and instrumentation.</p>
    <div className="table-scroll"><table><thead><tr><th>Model</th><th>FP32 parameter bytes</th><th>Preprocessing bytes</th><th>Evidence type</th></tr></thead><tbody>{fp32.map(row => <tr key={row.model_id}><td>{row.model_id}</td><td>{Number(row.analytical_parameter_bytes).toLocaleString()}</td><td>{Number(row.preprocessing_constant_bytes).toLocaleString()}</td><td><code>DERIVED_ANALYTICAL</code></td></tr>)}</tbody></table></div>

    <h2>Frozen evidence</h2>
    <ul>{embedded.artifact_paths.map(path => <li key={path}><ArtifactLink path={path} /></li>)}</ul>
  </div>;
}
