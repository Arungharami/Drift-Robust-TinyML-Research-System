import { RevealOnView } from "./RevealOnView";

const STAGES = ["Sense", "Detect", "Explain", "Adapt", "Trust"];

/** Section 18 — the closing 3MT moment. Adaptation is named as the research goal, not a result. */
export function FinalStatement() {
  return (
    <RevealOnView as="section" className="threemt-final">
      <p className="threemt-final-line">AI should not only be accurate today.</p>
      <p className="threemt-final-line threemt-final-line-strong">It should know when its world has changed.</p>
      <p className="threemt-final-subline">Drift-Robust Explainable TinyML for Electronic-Nose Sensing</p>
      <ol className="threemt-final-stages">
        {STAGES.map((stage, i) => (
          <li key={stage}>
            {stage}
            {i < STAGES.length - 1 ? <span aria-hidden="true"> → </span> : null}
          </li>
        ))}
      </ol>
      <p className="threemt-final-caveat">
        Sense and Detect are executed and evidence-linked above. Explain is executed with mixed
        results, stated plainly. Adapt and full Trust are this research&apos;s goal, not yet a
        demonstrated result.
      </p>
      <p className="threemt-final-meta">FAU · 3MT 2026</p>
    </RevealOnView>
  );
}
