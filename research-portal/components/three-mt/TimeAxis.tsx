const STEPS = [
  { label: "Before deployment", detail: "AI learns.", note: "Preprocessing is frozen and a baseline model is trained once, on Batch 1 only." },
  { label: "During deployment", detail: "Sensors age.", note: "Temperature, humidity, and hardware aging shift the electronic nose's raw signal." },
  { label: "Over time", detail: "The input distribution changes.", note: "Later chronological batches diverge from Batch 1 by a measured, non-zero drift score." },
  { label: "Consequence", detail: "The original model may degrade.", note: "A model frozen at Batch 1 is evaluated — never retrained — against every later batch." },
  { label: "Research question", detail: "Can we detect and understand that degradation?", note: "This is the question the rest of this page, and this project, answers with evidence." },
];

/** Section 6 — time as the page's design system, not just another paragraph. */
export function TimeAxis() {
  return (
    <section className="threemt-timeaxis" aria-labelledby="threemt-timeaxis-title">
      <h2 id="threemt-timeaxis-title">This research is fundamentally about time</h2>
      <ol className="threemt-timeaxis-list">
        {STEPS.map((step, i) => (
          <li key={step.label} className="threemt-timeaxis-step">
            <span className="threemt-timeaxis-index">{i + 1}</span>
            <div>
              <span className="threemt-timeaxis-label">{step.label}</span>
              <strong className="threemt-timeaxis-detail">{step.detail}</strong>
              <p className="threemt-timeaxis-note">{step.note}</p>
            </div>
            {i < STEPS.length - 1 ? <span className="threemt-timeaxis-connector" aria-hidden="true" /> : null}
          </li>
        ))}
      </ol>
    </section>
  );
}
