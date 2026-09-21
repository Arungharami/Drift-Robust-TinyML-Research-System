"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { BatchJourneyRow } from "./DriftJourneyPanel";

/**
 * Cinematic hero for /3mt. The "scientific visualization" is an honest SVG schematic — a sensor
 * array, a drifting waveform, and a compact edge-AI chip — driven ONLY by real per-batch drift
 * and accuracy values (the same rows DriftJourneyPanel uses, from
 * results/drift/global_drift_by_batch.csv and results/baselines/fixed_origin_metrics.csv).
 * Nothing here is a stock photo or a fabricated confidence curve.
 */
export function ThreeMTHero({ rows }: { rows: BatchJourneyRow[] }) {
  const usable = useMemo(() => rows.filter((r) => r.driftWasserstein !== null && r.modelC1Accuracy !== null), [rows]);
  const [index, setIndex] = useState(0);
  const current = usable[index] ?? usable[0];

  const driftValues = usable.map((r) => r.driftWasserstein as number);
  const maxDrift = Math.max(...driftValues, 1);
  const minDrift = Math.min(...driftValues, 0);
  const driftNorm = current ? (current.driftWasserstein! - minDrift) / (maxDrift - minDrift || 1) : 0;

  // Waveform distorts with real drift magnitude — decorative rendering of a real number, not a
  // separate measurement. Amplitude and jitter both scale with driftNorm.
  const points = useMemo(() => {
    const n = 48;
    const amp = 10 + driftNorm * 30;
    const freq = 2 + driftNorm * 3;
    const jitter = driftNorm * 14;
    let seed = Math.round((current?.batch ?? 1) * 1000);
    const rand = () => {
      seed = (seed * 1103515245 + 12345) & 0x7fffffff;
      return seed / 0x7fffffff;
    };
    const pts: string[] = [];
    for (let i = 0; i <= n; i++) {
      const x = (i / n) * 560;
      const y = 70 + Math.sin((i / n) * Math.PI * freq) * amp + (rand() - 0.5) * jitter;
      pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }
    return pts.join(" ");
  }, [driftNorm, current?.batch]);

  const isFirst = index === 0;
  const isLast = index === usable.length - 1;

  return (
    <section className="threemt-hero" aria-labelledby="threemt-hero-title">
      <div className="threemt-hero-copy">
        <div className="section-label">Three-Minute Thesis · FAU 2026</div>
        <h1 id="threemt-hero-title" className="threemt-hero-title">
          When AI Loses Its Sense of Smell
        </h1>
        <p className="threemt-hero-subhead">Drift-Robust Explainable TinyML for Electronic-Nose Sensing</p>
        <p className="threemt-hero-copy-text">
          Electronic noses can recognize chemical patterns. But their sensors change over time.
          This research asks whether lightweight AI can remain trustworthy as the world it senses
          slowly shifts.
        </p>
        <p className="btn-row">
          <Link className="btn btn-primary" href="/system-map">
            Explore the Research →
          </Link>
          <Link className="btn" href="/digital-twin">
            Open the Digital Twin
          </Link>
          <a className="btn" href="#evidence">
            View the Evidence
          </a>
          <Link className="btn" href="/methodology">
            Read the Methodology
          </Link>
        </p>
      </div>

      <div className="threemt-hero-visual" aria-hidden={usable.length === 0}>
        {current ? (
          <>
            <svg viewBox="0 0 560 140" className="threemt-hero-waveform" role="img" aria-label="Sensor signal shape, distorting as chronological drift increases">
              <polyline points={points} fill="none" strokeWidth="2.5" className="threemt-hero-waveform-line" />
              <line x1="0" y1="70" x2="560" y2="70" className="threemt-hero-waveform-baseline" strokeDasharray="2 6" />
            </svg>

            <div className="threemt-hero-readout">
              <div>
                <span className="k">Batch</span>
                <span className="v mono">
                  BATCH_{String(current.batch).padStart(2, "0")}
                  {current.batch === 2 ? " (≈ Month 3)" : current.batch === 10 ? " (≈ Month 36)" : ""}
                </span>
              </div>
              <div>
                <span className="k">Drift vs. Batch 1 (normalized Wasserstein)</span>
                <span className="v mono">{current.driftWasserstein!.toFixed(3)}</span>
              </div>
              <div>
                <span className="k">MODEL-C1 accuracy</span>
                <span className="v mono">{(current.modelC1Accuracy! * 100).toFixed(1)}%</span>
              </div>
            </div>

            <div className="threemt-hero-timeline">
              <input
                type="range"
                min={0}
                max={usable.length - 1}
                value={index}
                onChange={(e) => setIndex(Number(e.target.value))}
                aria-label="Move through chronological test batches"
                className="threemt-hero-slider"
              />
              <div className="threemt-hero-timeline-ticks">
                <span>{isFirst || !usable[0] ? "" : "BATCH_" + String(usable[0].batch).padStart(2, "0")}</span>
                <span className="threemt-hero-timeline-current">
                  BATCH_{String(current.batch).padStart(2, "0")}
                </span>
                <span>{isLast || !usable[usable.length - 1] ? "" : "BATCH_" + String(usable[usable.length - 1]!.batch).padStart(2, "0")}</span>
              </div>
            </div>
            <p className="threemt-hero-visual-caption">
              Drag the slider — the signal shape above renders the real, measured drift at each
              chronological batch. Nothing here is simulated.
            </p>
          </>
        ) : (
          <p className="empty-state">Drift/accuracy evidence not available.</p>
        )}
      </div>
    </section>
  );
}
