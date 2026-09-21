"use client";

import { useState } from "react";
import type { BatchJourneyRow } from "./DriftJourneyPanel";

/**
 * Section 21 — an optional, collapsible rapid-summary layer for judges/reviewers. Every number
 * is computed from the same rows the hero/AccuracyCollapse use, never re-typed independently, so
 * it can't drift out of sync with the evidence-linked story above it.
 */
export function JudgeMode({ rows, hardwareStatus }: { rows: BatchJourneyRow[]; hardwareStatus: string }) {
  const [open, setOpen] = useState(false);
  const before = rows.find((r) => r.batch === 2);
  const after = rows.find((r) => r.batch === 10);
  const fmtPct = (v: number | null | undefined) => (v === null || v === undefined ? "NOT EXECUTED" : `${(v * 100).toFixed(1)}%`);

  return (
    <div className="threemt-judge">
      <button type="button" className="btn threemt-judge-toggle" aria-expanded={open} onClick={() => setOpen((v) => !v)}>
        {open ? "Close 3MT Judge View" : "3MT Judge View — 60-second summary"}
      </button>
      {open ? (
        <div className="threemt-judge-panel" role="region" aria-label="3MT judge summary">
          <div className="threemt-judge-item">
            <span className="section-label">Problem</span>
            <p>Sensor drift can challenge long-term model reliability.</p>
          </div>
          <div className="threemt-judge-item">
            <span className="section-label">Approach</span>
            <p>Chronological drift-aware evaluation, resource-aware explainability, and TinyML deployment constraints, evaluated as separate research questions.</p>
          </div>
          <div className="threemt-judge-item">
            <span className="section-label">Result</span>
            <p>
              Baseline (MODEL-C1) accuracy drops from <strong>{fmtPct(before?.modelC1Accuracy)}</strong> at
              Batch 2 to <strong>{fmtPct(after?.modelC1Accuracy)}</strong> at Batch 10 — the same
              never-retrained model, later chronological data.
            </p>
          </div>
          <div className="threemt-judge-item">
            <span className="section-label">Contribution</span>
            <p>An evidence-driven framework connecting drift detection, explanation, and edge-deployment constraints, with every claim traced to a saved artifact.</p>
          </div>
          <div className="threemt-judge-item">
            <span className="section-label">Limitation</span>
            <p>Physical hardware validation remains {hardwareStatus.replace(/_/g, " ").toLowerCase()} — no nRF52840 board has been detected.</p>
          </div>
        </div>
      ) : null}
    </div>
  );
}
