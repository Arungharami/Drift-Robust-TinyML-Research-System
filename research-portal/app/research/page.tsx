import type { Metadata } from "next";
import { EvidenceBadge } from "@/components/EvidenceBadge";

export const metadata: Metadata = { title: "Research" };

const CONTRIBUTIONS: { text: string; status: "VALIDATED" | "PLANNED" }[] = [
  { text: "Chronological (time-respecting) e-nose drift evaluation, replacing IID splitting as the primary protocol", status: "VALIDATED" },
  { text: "Quantified generalization gap between IID and chronological evaluation on this dataset", status: "VALIDATED" },
  { text: "Resource-aware explainability suitable for constrained inference", status: "PLANNED" },
  { text: "Explanation fidelity measurement under chronological drift", status: "PLANNED" },
  { text: "Explanation stability measurement across drifting batches", status: "PLANNED" },
  { text: "Quantized TinyML deployment on nRF52840 / Cortex-M4F", status: "PLANNED" },
  { text: "Physical energy measurement via Nordic PPK2 (inference and explanation)", status: "PLANNED" },
  { text: "Reproducible, hash-linked evidence lineage from dataset to publication", status: "VALIDATED" },
  { text: "Accuracy–trust–resource Pareto analysis across the above axes", status: "PLANNED" },
];

export default function ResearchPage() {
  return (
    <div className="container">
      <div className="section-label">Research framing</div>
      <h1>Research question and contributions</h1>

      <h2>Central research question</h2>
      <blockquote
        style={{
          margin: "1rem 0",
          padding: "1rem 1.25rem",
          borderLeft: "3px solid var(--accent)",
          background: "var(--bg-muted)",
          fontStyle: "italic",
        }}
      >
        Can lightweight machine-learning models combined with resource-aware explanation
        strategies maintain useful predictive performance and interpretable behavior under
        chronological electronic-nose sensor drift, while satisfying the memory, latency, and
        energy constraints of TinyML-class microcontrollers?
      </blockquote>
      <p>
        This question is not yet answered. Chronological evaluation of classical models
        (Checkpoint 1–2) provides partial evidence toward the first half; the explainability,
        quantization, and hardware components required to answer the second half are{" "}
        <strong>not executed</strong>. See <a href="/results">Results</a> for what is currently
        supported, and <a href="/pipeline">Pipeline</a> for what remains.
      </p>

      <h2>Why not &ldquo;Pareto-aware explainability for TinyML&rdquo;?</h2>
      <p>
        That framing understates the work. The intended contribution combines chronological
        e-nose drift evaluation, resource-aware explainability, explanation fidelity and
        stability under drift, quantized TinyML deployment, physical nRF52840/PPK2 measurement,
        reproducible evidence lineage, and an accuracy–trust–resource Pareto analysis — a
        multi-axis systems contribution, not a single explainability technique.
      </p>

      <h2>Contributions</h2>
      <p style={{ fontSize: "0.88rem", color: "var(--text-muted)" }}>
        Each contribution is labeled by its current evidence state, not its intended importance.
        A <code>Planned</code> label means genuinely not yet executed — see{" "}
        <a href="/pipeline">Pipeline</a> for the specific blocking stage.
      </p>
      <div className="card-grid">
        {CONTRIBUTIONS.map((c) => (
          <div className="card" key={c.text}>
            <div style={{ marginBottom: "0.5rem" }}>
              <EvidenceBadge status={c.status} />
            </div>
            <p style={{ margin: 0, fontSize: "0.92rem" }}>{c.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
