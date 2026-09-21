import { ArtifactLink } from "@/components/ArtifactLink";

const PRINCIPLES = [
  { title: "Chronological order is preserved", body: "Batches are never shuffled — training, drift measurement, and evaluation all follow real elapsed time." },
  { title: "Preprocessing is frozen appropriately", body: "Standardization is fit once on Batch 1 only, then frozen before any later batch is touched." },
  { title: "Train/test chronology is defined before training", body: "The chronological split is written down before any model sees data, not chosen after the fact." },
  { title: "Experiments are registered", body: "Every run gets an experiment ID, a dataset hash, a config hash, and a git commit — before results are reported." },
  { title: "Results link to artifacts", body: "Every number on this site traces back to a saved CSV/JSON artifact, not a paragraph of prose." },
  { title: "Unavailable measurements are marked explicitly", body: "NOT_EXECUTED, NOT_MEASURED, and BLOCKED_HARDWARE appear on this page instead of being omitted." },
];

/** Section 14. */
export function NoMagicSection() {
  return (
    <section className="threemt-nomagic" aria-labelledby="threemt-nomagic-title">
      <h2 id="threemt-nomagic-title">No Black Boxes. No Hidden Numbers.</h2>
      <div className="card-grid">
        {PRINCIPLES.map((p) => (
          <div className="card" key={p.title}>
            <h3 style={{ marginTop: 0, fontSize: "1rem" }}>{p.title}</h3>
            <p style={{ fontSize: "0.88rem", marginBottom: 0 }}>{p.body}</p>
          </div>
        ))}
      </div>
      <p style={{ fontSize: "0.85rem", color: "var(--text-faint)" }}>
        The full chronological-evaluation protocol is frozen in{" "}
        <ArtifactLink path="configs/chronological_protocol.yaml" />.
      </p>
    </section>
  );
}
