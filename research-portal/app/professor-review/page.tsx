import type { Metadata } from "next";
import { ArtifactLink } from "@/components/ArtifactLink";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { getPipeline, getProjectStatus } from "@/lib/evidence";

export const metadata: Metadata = { title: "Professor Review" };

const QUESTIONS = [
  "Is the chronological protocol (train Batch 1, evaluate 2-10 without retraining) defensible as the primary evaluation, with EXPANDING_WINDOW and IID_DIAGNOSTIC as secondary/diagnostic only?",
  "Which model families should remain in scope — is Logistic Regression / Random Forest / RBF-SVM / MLP sufficient, or is a compact deep model required before the XAI stage?",
  "Is the planned explanation-fidelity design (perturbation-based agreement with a reference explainer) appropriate, or is a different fidelity definition expected for this venue?",
  "Is the planned drift-stability definition (rank correlation / top-k overlap of explanations across batches) publishable, or does it need a stronger theoretical grounding?",
  "Which experiments are strictly required before manuscript submission — is physical PPK2 energy measurement mandatory, or can quantized-model estimates suffice for a first submission?",
  "Which venue best matches this work — a TinyML/embedded systems venue, an XAI venue, or a sensors/analytical-chemistry venue?",
  "Should real iSENSE/e-nose physical measurements be added, or is the UCI dataset sufficient for the intended contribution?",
];

export default function ProfessorReviewPage() {
  const status = getProjectStatus();
  const pipeline = getPipeline();
  const executed = pipeline.filter((s) => s.status === "EXECUTED");
  const pending = pipeline.filter((s) => s.status !== "EXECUTED");

  return (
    <div className="container">
      <div className="section-label">For advisor / committee review</div>
      <h1>Professor review summary</h1>
      <p className="lede">
        A faculty-oriented summary of this project&apos;s current state, suitable for bringing
        to a research meeting. Nothing below overstates completed work.
      </p>

      <h2>Research problem</h2>
      <p style={{ maxWidth: "68ch" }}>
        Electronic-nose (chemical sensor array) readings drift over time due to sensor aging,
        contamination, and environmental variation, degrading naive ML classifier performance.
        Standard practice often evaluates such models with random train/test splits, which mixes
        future-batch characteristics into training and overstates real-world performance.
      </p>

      <h2>Research gap</h2>
      <p style={{ maxWidth: "68ch" }}>
        Prior concept-drift and TinyML literature (see <a href="/references">References</a>)
        addresses drift adaptation, general explainability, or embedded deployment constraints
        largely in isolation. No identified prior work combines chronological e-nose drift
        evaluation, resource-aware explainability with measured fidelity/stability, and physical
        TinyML deployment evidence (Flash/SRAM/latency/energy via PPK2) in one evidence chain.
      </p>

      <h2>Research question</h2>
      <p style={{ maxWidth: "68ch" }}>See the full framing on the <a href="/research">Research</a> page.</p>

      <h2>Methodology</h2>
      <p style={{ maxWidth: "68ch" }}>
        Frozen chronological protocols (<code>FIXED_ORIGIN</code>, <code>EXPANDING_WINDOW</code>,{" "}
        <code>IID_DIAGNOSTIC</code>) defined in{" "}
        <ArtifactLink path="configs/chronological_protocol.yaml" />; see{" "}
        <a href="/methodology">Methodology</a> for full detail.
      </p>

      <h2>Current evidence ({executed.length} / {status.pipeline_total_stages} pipeline stages executed)</h2>
      <ul style={{ fontSize: "0.9rem" }}>
        {executed.map((s) => (
          <li key={s.id}>
            <strong>{s.name}</strong> — {s.notes}
          </li>
        ))}
      </ul>

      <h2>Pending experiments</h2>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Stage</th><th>Status</th><th>Notes</th></tr></thead>
          <tbody>
            {pending.map((s) => (
              <tr key={s.id}>
                <td>{s.id} — {s.name}</td>
                <td><EvidenceBadge status={s.status} /></td>
                <td style={{ fontSize: "0.85rem" }}>{s.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Known novelty threats</h2>
      <p style={{ maxWidth: "68ch" }}>
        See the novelty matrix on the <a href="/references">References</a> page. The clearest
        threat: individually, chronological evaluation, SHAP/LIME-style explainability, and
        TinyML deployment surveys each exist; the combination with measured fidelity/stability
        under drift and physical PPK2 energy has not been located in the literature reviewed so
        far, but that search has not been exhaustive.
      </p>

      <h2>Hardware plan</h2>
      <p style={{ maxWidth: "68ch" }}>
        Target: Nordic nRF52840 (Cortex-M4F) for inference/explanation deployment, Nordic PPK2
        for physical energy measurement. No physical measurement has occurred —{" "}
        <a href="/hardware">Hardware</a> and <a href="/tinyml">TinyML</a> pages record this
        honestly as <code>NOT EXECUTED</code>.
      </p>

      <h2>Expected publication contribution</h2>
      <p style={{ maxWidth: "68ch" }}>
        A systems-level contribution combining chronological e-nose drift evaluation with
        resource-aware, fidelity/stability-measured explanations and physically measured TinyML
        deployment cost — not a single novel algorithm.
      </p>

      <h2>Questions for advisor</h2>
      <ol style={{ maxWidth: "68ch" }}>
        {QUESTIONS.map((q) => (
          <li key={q} style={{ marginBottom: "0.5rem" }}>{q}</li>
        ))}
      </ol>

      <h2>Ways the professor can contribute</h2>
      <ul style={{ maxWidth: "68ch" }}>
        <li>Confirm the chronological protocol and model scope before further experiments are locked in.</li>
        <li>Advise on fidelity/stability metric choice before stage 09-11 are implemented.</li>
        <li>Help identify whether physical hardware (nRF52840 dev kit, PPK2) is accessible through the lab.</li>
        <li>Suggest a target venue so the manuscript structure and required evidence bar can be set now.</li>
      </ul>
    </div>
  );
}
