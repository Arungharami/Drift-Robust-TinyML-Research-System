import type { Metadata } from "next";
import { ExperimentCard } from "@/components/ExperimentCard";
import { getExperiments } from "@/lib/evidence";

export const metadata: Metadata = { title: "Experiments" };

export default function ExperimentsPage() {
  const experiments = getExperiments();

  return (
    <div className="container">
      <div className="section-label">Experiment registry</div>
      <h1>Experiments</h1>
      <p className="lede">
        Machine-readable registry of every executed experiment — {experiments.length} entries,
        sourced directly from <code>results/registry/experiment_registry.csv</code>. Deep
        learning, XAI, quantization, and hardware experiments are not yet registered because they
        have not been executed.
      </p>
      {experiments.length === 0 ? (
        <div className="empty-state">No experiments recorded yet.</div>
      ) : (
        experiments.map((exp) => <ExperimentCard key={exp.experiment_id} experiment={exp} />)
      )}
    </div>
  );
}
