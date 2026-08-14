import type { Metadata } from "next";
import { ArtifactLink } from "@/components/ArtifactLink";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { HardwareConnectionDiagram } from "@/components/HardwareConnectionDiagram";
import { HardwareStatus } from "@/components/HardwareStatus";
import { HardwareWorkflow } from "@/components/HardwareWorkflow";
import { ProfessorReviewTabs } from "@/components/ProfessorReviewTabs";
import { getPipeline, getProjectStatus } from "@/lib/evidence";

export const metadata: Metadata = { title: "Advisor / Committee Review" };

const priorities = [
  ["Evaluation hierarchy and model scope", "Whether FIXED_ORIGIN should remain primary, EXPANDING_WINDOW secondary, IID_DIAGNOSTIC diagnostic only, and whether a compact deep model is scientifically necessary."],
  ["Interpretation of explanation evidence", "Stages 10–11 were executed but their tested candidate claims were unsupported. Guidance is requested on whether this reflects weak explanation behaviour, definitions requiring refinement, or a need for sensitivity analysis."],
  ["Publication evidence bar", "Advice is requested on venue positioning, physical nRF52840/PPK2 requirements, an additional e-nose dataset, and whether a systems contribution is sufficient without a new algorithm."],
] as const;

export default function ProfessorReviewPage() {
  const status = getProjectStatus();
  const pipeline = getPipeline();
  const stage = (id: string) => pipeline.find((item) => item.id === id);

  const brief = <>
    <div className="section-label">Advisor / Committee Review</div>
    <h1>Evidence-driven review brief</h1>
    <p className="lede">This review brief summarizes the project&apos;s current evidence, unresolved scientific decisions, and immediate execution constraints for advisor and committee discussion. It distinguishes completed experiments, unsupported candidate claims, retained failed outcomes, frozen protocols, blocked hardware work, and proposed contributions.</p>

    <section>
      <h2>Research problem and provisional gap</h2>
      <p>Electronic-nose sensors drift through aging, contamination, and environmental variation. Chronological evaluation tests future-batch degradation directly; random splits can mix future characteristics into training and give an overly favourable deployment estimate.</p>
      <p>The literature reviewed so far has not identified a study that unifies chronological e-nose drift evaluation, quantitatively assessed explanation fidelity and stability, and physically measured TinyML deployment cost in one traceable evidence chain. This remains a provisional literature finding rather than a claim of exhaustive novelty.</p>
    </section>

    <section>
      <h2>Research design</h2>
      <p><code>FIXED_ORIGIN</code> is the primary prospective protocol; <code>EXPANDING_WINDOW</code> is secondary adaptation analysis; <code>IID_DIAGNOSTIC</code> is diagnostic only. Preprocessing is training-only and four frozen model families underpin the current results. <ArtifactLink path="configs/chronological_protocol.yaml" /></p>
    </section>

    <section>
      <h2>Current evidence</h2>
      <div className="review-statuses">{Object.entries(status.pipeline_stage_counts).map(([name, count]) => <span key={name}><EvidenceBadge status={name} /> {count}</span>)}</div>
      <p>Counts are derived from the declared pipeline registry, not a progress percentage. Negative outcomes remain distinct from unexecuted work.</p>
      <div className="table-scroll"><table><thead><tr><th>Area</th><th>Status</th><th>Boundary</th></tr></thead><tbody>
        {["10", "11", "12", "13", "14", "14R", "15"].map((id) => {
          const item = stage(id);
          return item && <tr key={id}><td>{item.id} — {item.name}</td><td><EvidenceBadge status={id === "15" ? "BLOCKED_HARDWARE" : item.status} /></td><td>{item.notes}</td></tr>;
        })}
      </tbody></table></div>
    </section>

    <section>
      <h2>Findings requiring interpretation</h2>
      <p>Stage 10 fidelity and Stage 11 stability experiments were executed, but their tested candidate claims were unsupported. These retained results may indicate weak explanation behaviour, limitations in the tested definitions, or both; this branch does not alter metrics or rerun experiments. <ArtifactLink path="results/xai/stage10_fidelity_summary.csv" /> <ArtifactLink path="results/xai/stage11_stability_summary.csv" /></p>
      <p>Stages 14 and 14R retain failed export/preprocessing outcomes; later host equivalence does not establish physical deployment.</p>
    </section>

    <section>
      <h2>Hardware constraint</h2>
      <p>Prerequisite detection was executed, but no supported nRF52840 board or debug interface was detected. Board identity was not guessed. Physical deployment, Flash/SRAM, MCU latency, and PPK2 energy remain unmeasured.</p>
      <HardwareConnectionDiagram />
      <HardwareWorkflow />
      <HardwareStatus />
      <p><a href="/hardware">Hardware record</a> · <a href="/tinyml">TinyML record</a> · <ArtifactLink path="results/embedded/stage15_hardware_detection.json" /></p>
    </section>

    <section><h2>Proposed systems contribution</h2><p>A reproducible systems-level study connecting chronological drift evaluation, resource-aware explanation analysis, numerical equivalence, and physical deployment cost. It is not necessarily a new learning algorithm, and final scope depends on remaining hardware work.</p></section>

    <section><h2>Discussion priorities</h2><div className="discussion-priorities">{priorities.map(([title, text], index) => <article key={title}><span>{index + 1}</span><h3>{title}</h3><p>{text}</p></article>)}</div></section>

    <section><h2>Evidence and collaboration notices</h2><p>Evidence last exported {status.last_updated} from commit <code>{status.git_commit.slice(0, 12)}</code> on <code>{status.branch}</code>. Reviewer uploads and comments are collaborative material, not validated scientific evidence, unless separately reviewed and registered through the evidence pipeline.</p></section>
  </>;

  return <main className="container professor-review"><ProfessorReviewTabs brief={brief} /></main>;
}
