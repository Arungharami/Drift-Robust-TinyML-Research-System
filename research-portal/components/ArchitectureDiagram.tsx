const STEPS = [
  "Dataset",
  "Chronological ML",
  "Drift evaluation",
  "Explainability",
  "Quantization",
  "nRF52840",
  "PPK2",
  "Reproducible artifacts",
  "Publication",
];

/** Restrained text-flow diagram — deliberately not a decorative illustration. */
export function ArchitectureDiagram() {
  return (
    <div className="diagram-flow" role="img" aria-label={`Research system flow: ${STEPS.join(" to ")}`}>
      {STEPS.map((step, i) => (
        <span key={step} className="diagram-node">
          <span className="diagram-step">{step}</span>
          {i < STEPS.length - 1 ? <span className="diagram-arrow" aria-hidden="true">→</span> : null}
        </span>
      ))}
    </div>
  );
}
