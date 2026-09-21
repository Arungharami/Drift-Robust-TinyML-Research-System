import { EvidenceBadge } from "@/components/EvidenceBadge";
import Link from "next/link";
import type { XaiEvidence } from "@/lib/types";

const METHOD_LABELS: Record<string, string> = {
  INTRINSIC_COEFFICIENT: "Intrinsic model coefficients",
  INTRINSIC_IMPURITY: "Intrinsic impurity importance",
  PERMUTATION_IMPORTANCE_MACRO_F1: "Permutation importance (macro-F1)",
  SINGLE_FEATURE_ABLATION_LOCAL: "Single-feature ablation (local)",
};

/**
 * Section 10 — "Why did the model decide this?", built only from methods this project actually
 * ran (xai.applicability_matrix). SHAP/LIME are deliberately absent from both the methodology
 * and this visual, per docs/experiments/STAGE09_RESOURCE_AWARE_XAI.md.
 */
export function ExplainabilityView({ xai }: { xai: XaiEvidence }) {
  const executedMethods = Array.from(
    new Set(xai.applicability_matrix.filter((r) => r.status === "EXECUTED").map((r) => r.method)),
  );

  return (
    <section className="threemt-xai" aria-labelledby="threemt-xai-title">
      <h2 id="threemt-xai-title">Why did the model decide this?</h2>

      <div className="threemt-xai-flow">
        <div className="threemt-xai-flow-step">
          <span className="section-label">Sensor features</span>
          <p>128 features — 16 chemical sensors × 8 response characteristics per reading.</p>
        </div>
        <div className="threemt-xai-flow-arrow" aria-hidden="true">→</div>
        <div className="threemt-xai-flow-step">
          <span className="section-label">Important signal characteristics</span>
          <p>Resource-aware attribution methods rank which of those 128 features drove a prediction.</p>
        </div>
        <div className="threemt-xai-flow-arrow" aria-hidden="true">→</div>
        <div className="threemt-xai-flow-step">
          <span className="section-label">Model decision</span>
          <p>One of six gas classes, with the attribution behind it — evaluated for fidelity and stability.</p>
        </div>
      </div>

      <h3>Methods actually executed</h3>
      <ul className="threemt-xai-methods">
        {executedMethods.map((m) => (
          <li key={m}>
            <code>{m}</code> — {METHOD_LABELS[m] ?? m}
          </li>
        ))}
      </ul>
      <p className="threemt-xai-note">
        Deliberately not SHAP or LIME — this project uses permutation importance, intrinsic
        model information, and single-feature ablation instead. Fidelity and stability were
        executed but the resulting claims are <strong>predominantly unsupported or mixed</strong>,
        stated plainly rather than minimized. <EvidenceBadge status={xai.evidence_status} /> — full
        detail on <Link href="/xai">/xai</Link>.
      </p>
    </section>
  );
}
