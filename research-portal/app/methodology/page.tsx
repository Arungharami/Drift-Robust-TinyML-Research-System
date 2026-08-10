import type { Metadata } from "next";
import { ArtifactLink } from "@/components/ArtifactLink";
import { getBaselines } from "@/lib/evidence";

export const metadata: Metadata = { title: "Methodology" };

export default function MethodologyPage() {
  const baselines = getBaselines();

  return (
    <div className="container">
      <div className="section-label">Methodology</div>
      <h1>Experimental protocol</h1>
      <p className="lede">
        Three protocols are defined in a frozen, version-controlled config
        (<ArtifactLink path="configs/chronological_protocol.yaml" />). The split policy is never
        silently changed — any revision creates a new named protocol version.
      </p>

      <h2>Protocols</h2>
      <div className="card-grid">
        <div className="card">
          <h3 style={{ marginTop: 0 }}>FIXED_ORIGIN (primary)</h3>
          <p style={{ fontSize: "0.9rem" }}>
            Fit all preprocessing and models on Batch 1 only. Evaluate, without retraining, on
            Batches 2–10 in chronological order. This is the primary evaluation protocol — it
            reflects a deployed model that is never quietly updated as drift accumulates.
          </p>
        </div>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>EXPANDING_WINDOW (adaptation)</h3>
          <p style={{ fontSize: "0.9rem" }}>
            Before evaluating batch <em>k</em>, retrain using all batches strictly before{" "}
            <em>k</em>. Measures how much periodic retraining recovers the accuracy lost to
            drift, still respecting chronology (never trains on future data).
          </p>
        </div>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>IID_DIAGNOSTIC (diagnostic only)</h3>
          <p style={{ fontSize: "0.9rem" }}>
            A stratified random 80/20 split across all batches pooled together, ignoring
            chronology. Reported <strong>only</strong> to quantify how much a random split
            overstates future-batch performance — never used as a primary result.
          </p>
        </div>
      </div>

      <h2>Models in scope</h2>
      <p style={{ maxWidth: "68ch" }}>
        Four lightweight, interpretable candidates were selected — not dozens of models chosen to
        inflate a benchmark table. Configuration:{" "}
        <ArtifactLink path="configs/classical_baselines.yaml" />.
      </p>
      <div className="table-scroll">
        <table>
          <thead><tr><th>ID</th><th>Model</th><th>Rationale</th></tr></thead>
          <tbody>
            <tr><td>MODEL-C1</td><td>Logistic Regression</td><td>Linear, fully interpretable coefficients</td></tr>
            <tr><td>MODEL-C2</td><td>Random Forest</td><td>Non-linear baseline with native feature importance</td></tr>
            <tr><td>MODEL-C3</td><td>RBF-SVM</td><td>Non-linear margin-based baseline</td></tr>
            <tr><td>MODEL-C4</td><td>MLP Classifier</td><td>Small neural classifier, TinyML-plausible size</td></tr>
          </tbody>
        </table>
      </div>
      <p style={{ fontSize: "0.85rem" }}>{baselines.protocol_note}</p>

      <h2>Data flow</h2>
      <p>See the full stage-by-stage breakdown on the <a href="/pipeline">Pipeline</a> page.</p>
    </div>
  );
}
