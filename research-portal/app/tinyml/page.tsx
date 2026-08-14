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

    {embedded.stage15_hardware_gate && <>
      <h2>Stage 15 physical MCU port</h2>
      <p>Experiment <code>EXP-MCU-C1-FP32-PORT-001</code>: <code>BLOCKED_HARDWARE</code>. No supported physical board/debug probe was detected, so no board target was guessed and no build, flash, physical correctness, linked ROM, or linked static-RAM claim was produced.</p>
      <p><a href="/hardware">Review the hardware blocker, planned connection, and evidence artifacts</a>.</p>
    </>}

    {embedded.c1_repair_summary.length > 0 && <>
      <h2>Stage 14R C1 explicit-preprocessing repair</h2>
      <p>Outcome: <code>FAILED</code>. The original failure reproduced, and none of the five prospectively frozen all-FP32 candidates passed every unchanged preprocessing criterion. No candidate was selected.</p>
      <div className="table-scroll"><table><thead><tr><th>Candidate</th><th>Max abs</th><th>Max relative</th><th>Failed rows</th><th>Score max abs</th><th>Probability max abs</th><th>Golden</th><th>Boundary</th><th>Mandatory</th></tr></thead><tbody>{embedded.c1_repair_summary.map(row => <tr key={row.candidate_id}><td><code>{row.candidate_id}</code></td><td>{Number(row.preprocessing_max_absolute_error).toExponential(3)}</td><td>{Number(row.preprocessing_max_relative_error).toExponential(3)}</td><td>{row.failed_feature_rows}</td><td>{Number(row.score_max_absolute_error).toExponential(3)}</td><td>{Number(row.probability_max_absolute_error).toExponential(3)}</td><td>{(Number(row.golden_agreement)*100).toFixed(0)}%</td><td>{(Number(row.boundary_agreement)*100).toFixed(0)}%</td><td><code>FAIL</code></td></tr>)}</tbody></table></div>
      <p>Conclusion: <code>STRICT_FP32_EXPLICIT_STANDARDIZATION_REPAIR_NOT_DEMONSTRATED</code>. The next proposal is a separately frozen fused preprocessing/inference experiment—not a retroactive repair and not quantization.</p>
    </>}

    {embedded.c1_fused_gate && <>
      <h2>C1 fused preprocessing architecture gate</h2>
      <p>Gate <code>{embedded.c1_fused_gate.gate_id}</code>: <code>{embedded.c1_fused_gate.gate_status}</code>. Experiment <code>{embedded.c1_fused_gate.future_experiment_id}</code> subsequently executed and <code>PASSED</code> every frozen criterion on the host.</p>
      <p>The architecture folds the frozen scaler into raw-domain linear weights and biases. It deliberately does not materialize standardized features, so it does not retroactively repair Stage 14 or Stage 14R.</p>
      <div className="table-scroll"><table><thead><tr><th>Architecture</th><th>Scaler subtractions</th><th>Scaler divisions</th><th>Classifier multiplications</th><th>Transformed buffer</th><th>Evidence</th></tr></thead><tbody>{embedded.c1_fused_operations.filter(row => row.architecture !== "FUSED_MINUS_EXPLICIT").map(row => <tr key={row.architecture}><td><code>{row.architecture}</code></td><td>{row.scaler_subtractions}</td><td>{row.scaler_divisions}</td><td>{row.classifier_multiplications}</td><td>{row.transformed_buffer_elements} elements</td><td><code>DERIVED_ANALYTICAL</code></td></tr>)}</tbody></table></div>
      <p>Fused local XAI is not included. Inference must pass first; a baseline-preserving explanation representation requires a separate experiment.</p>
      <p>Golden maximum score error: <code>{Number(embedded.c1_fused_execution.find(row => row.population === "GOLDEN" && row.metric === "score_absolute_error")?.max).toExponential(3)}</code>. Claims <code>C-EMBED-C1-FUSED-01</code> and <code>C-EMBED-C1-FUSED-02</code> are supported; fused XAI remains <code>NOT_EXECUTED</code>.</p>
      {embedded.c1_fused_xai_summary.length > 0 && <p>Fused local XAI subsequently <code>PASSED</code> across {embedded.c1_fused_xai_summary.length} Stage-09 audit samples. Maximum vector L1 error was <code>{Math.max(...embedded.c1_fused_xai_summary.map(row => Number(row.attribution_vector_l1_error))).toExponential(3)}</code>; <code>C-EMBED-C1-FUSED-XAI-01</code> is supported for the host representation.</p>}
    </>}

    <h2>Analytical storage — derived estimate</h2>
    <p><strong>These values are not measured Flash or SRAM.</strong> They count raw scalar-equivalent parameters and omit compiled code, runtime metadata, stack, heap, buffers, and instrumentation.</p>
    <div className="table-scroll"><table><thead><tr><th>Model</th><th>FP32 parameter bytes</th><th>Preprocessing bytes</th><th>Evidence type</th></tr></thead><tbody>{fp32.map(row => <tr key={row.model_id}><td>{row.model_id}</td><td>{Number(row.analytical_parameter_bytes).toLocaleString()}</td><td>{Number(row.preprocessing_constant_bytes).toLocaleString()}</td><td><code>DERIVED_ANALYTICAL</code></td></tr>)}</tbody></table></div>

    <h2>Frozen evidence</h2>
    <ul>{embedded.artifact_paths.map(path => <li key={path}><ArtifactLink path={path} /></li>)}</ul>
  </div>;
}
