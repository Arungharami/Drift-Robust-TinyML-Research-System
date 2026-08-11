import type { Metadata } from "next";
import { ReferenceCard } from "@/components/ReferenceCard";
import { NoveltyMatrix, type NoveltyRow } from "@/components/NoveltyMatrix";
import { getReferences } from "@/lib/evidence";

export const metadata: Metadata = { title: "References" };

const NOVELTY_ROWS: NoveltyRow[] = [
  {
    paper: "Gama et al. 2014 (concept drift survey)",
    dataset: "General (survey)",
    marks: { "Chronological eval.": true, "Sensor drift": false, TinyML: false, Reproducibility: false },
  },
  {
    paper: "Lundberg & Lee 2017 (SHAP)",
    dataset: "General (tabular/image)",
    marks: { XAI: true, Fidelity: false, "On-device XAI": false, Reproducibility: false },
  },
  {
    paper: "Ribeiro et al. 2016 (LIME)",
    dataset: "General (tabular/text/image)",
    marks: { XAI: true, Fidelity: false, "On-device XAI": false, Reproducibility: false },
  },
  {
    paper: "Sanchez-Iborra & Skarmeta 2020 (TinyML survey)",
    dataset: "General (survey)",
    marks: { TinyML: true, "Flash/SRAM": true, "Physical latency": true, "Physical energy": false, PPK2: false },
  },
  {
    paper: "This work (proposed)",
    dataset: "UCI Gas Sensor Array Drift",
    marks: {
      "Chronological eval.": true,
      "Sensor drift": true,
      TinyML: true,
      XAI: true,
      "On-device XAI": false,
      Fidelity: false,
      Stability: false,
      "Physical latency": false,
      "Flash/SRAM": false,
      "Physical energy": false,
      PPK2: false,
      Reproducibility: true,
    },
  },
];

export default function ReferencesPage() {
  const references = getReferences();

  return (
    <div className="container">
      <div className="section-label">References</div>
      <h1>Literature and novelty positioning</h1>
      <p className="lede">
        Every reference below was fetched/verified from an authoritative source (UCI, ACM, IEEE,
        NeurIPS proceedings) before being cited — none are invented. Structured source:{" "}
        <code>data/literature/references.json</code>.
      </p>

      {references.length === 0 ? (
        <div className="empty-state">No references recorded yet.</div>
      ) : (
        references.map((ref) => <ReferenceCard key={ref.id} reference={ref} />)
      )}

      <h2>Novelty matrix</h2>
      <p style={{ fontSize: "0.88rem", maxWidth: "68ch" }}>
        Marks reflect only what each cited work actually demonstrates — this project&apos;s own
        row is marked honestly by current evidence state (see <a href="/pipeline">Pipeline</a>),
        not by aspiration. Cells for unexecuted stages are intentionally unmarked.
      </p>
      <NoveltyMatrix rows={NOVELTY_ROWS} />
    </div>
  );
}
