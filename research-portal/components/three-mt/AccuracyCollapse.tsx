import type { BatchJourneyRow } from "./DriftJourneyPanel";
import { RevealOnView } from "./RevealOnView";

/**
 * The project's single most understandable finding: the same fixed, never-retrained baseline
 * model, evaluated on later chronological batches. Both numbers are read from the same rows
 * DriftJourneyPanel uses (results/baselines/fixed_origin_metrics.csv) — batch 2 and batch 10 are
 * not hardcoded independently; if either is ever missing from the evidence, this renders
 * NOT EXECUTED instead of a stale number.
 */
export function AccuracyCollapse({ rows }: { rows: BatchJourneyRow[] }) {
  const before = rows.find((r) => r.batch === 2);
  const after = rows.find((r) => r.batch === 10);
  const driftBefore = before?.driftWasserstein ?? null;
  const driftAfter = after?.driftWasserstein ?? null;

  const fmtPct = (v: number | null | undefined) => (v === null || v === undefined ? "NOT EXECUTED" : `${(v * 100).toFixed(1)}%`);
  const fmtDrift = (v: number | null | undefined) => (v === null || v === undefined ? "NOT EXECUTED" : v.toFixed(3));

  return (
    <RevealOnView as="section" className="threemt-collapse">
      <div className="section-label">The clearest finding</div>
      <div className="threemt-collapse-grid">
        <div className="threemt-collapse-figure threemt-collapse-before">
          <span className="k">BATCH_02 · early sensor data</span>
          <span className="threemt-collapse-number">{fmtPct(before?.modelC1Accuracy)}</span>
          <span className="threemt-collapse-caption">MODEL-C1 (logistic regression) accuracy</span>
        </div>
        <div className="threemt-collapse-arrow" aria-hidden="true">→</div>
        <div className="threemt-collapse-figure threemt-collapse-after">
          <span className="k">BATCH_10 · later sensor data</span>
          <span className="threemt-collapse-number">{fmtPct(after?.modelC1Accuracy)}</span>
          <span className="threemt-collapse-caption">same model, never retrained</span>
        </div>
      </div>

      <p className="threemt-collapse-message">Same baseline model. Later sensor data.</p>

      <p className="threemt-collapse-note">
        Drift relative to Batch 1 (normalized Wasserstein) is <strong>{fmtDrift(driftBefore)}</strong> at
        Batch 2 and <strong>{fmtDrift(driftAfter)}</strong> at Batch 10 — it is time-varying, not a
        steady climb (it peaks mid-series). What does not recover is accuracy: the model degrades
        and stays degraded, even where the drift number itself later drops.
      </p>
    </RevealOnView>
  );
}
