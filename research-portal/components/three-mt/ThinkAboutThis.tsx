import { RevealOnView } from "./RevealOnView";

/**
 * Section 7 — the quiet conceptual bridge between "the accuracy collapsed" and the rest of the
 * research. Three lines, no data, no animation beyond the shared one-shot reveal.
 */
export function ThinkAboutThis() {
  return (
    <RevealOnView as="section" className="threemt-think" aria-label="Conceptual bridge">
      <p className="threemt-think-line">The sensor changed.</p>
      <p className="threemt-think-line">The model stayed the same.</p>
      <p className="threemt-think-line threemt-think-line-question">What should a trustworthy edge AI system do?</p>
    </RevealOnView>
  );
}
