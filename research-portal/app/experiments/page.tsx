import type { Metadata } from "next";
import { ExperimentCard } from "@/components/ExperimentCard";
import { getExperiments } from "@/lib/evidence";

export const metadata: Metadata = { title: "Experiments" };

export default function ExperimentsPage() {
  const experiments = getExperiments();
  const families = [...new Set(experiments.map((experiment) =>
    experiment.experiment_id.startsWith("EXP-XAI") ? "XAI" : experiment.experiment_id.split("-")[0]
  ))];

  return (
    <div className="container">
      <div className="section-label">Experiment registry</div>
      <h1>Experiments</h1>
      <p className="lede">
        Machine-readable registry of every executed experiment — {experiments.length} entries,
        sourced from the generated evidence registry. Registered experiment families: {families.join(", ")}.
      </p>
      {experiments.length === 0 ? (
        <div className="empty-state">No experiments recorded yet.</div>
      ) : (
        experiments.map((exp) => <ExperimentCard key={exp.experiment_id} experiment={exp} />)
      )}
    </div>
  );
}
