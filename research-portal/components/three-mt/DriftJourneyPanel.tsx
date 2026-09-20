"use client";

import { useState } from "react";
import { BatchMetricLineChart } from "@/components/ResultsCharts";

export interface BatchJourneyRow {
  batch: number;
  driftWasserstein: number | null;
  modelC1Accuracy: number | null;
}

interface DriftJourneyPanelProps {
  rows: BatchJourneyRow[];
  chartData: Record<string, number | string>[];
}

const MODELS = ["MODEL-C1", "MODEL-C2", "MODEL-C3", "MODEL-C4"];

/**
 * Real-data "move between chronological batches" interaction for the 3MT page. Every number
 * shown is read from research-portal/data/evidence/{drift,baselines}.json (generated from
 * results/drift/global_drift_by_batch.csv and results/baselines/fixed_origin_by_batch.csv) —
 * nothing here is a conceptual placeholder. The always-rendered table below the controls is
 * the full non-JS/screen-reader-equivalent of the interactive readout.
 */
export function DriftJourneyPanel({ rows, chartData }: DriftJourneyPanelProps) {
  const [selectedBatch, setSelectedBatch] = useState(rows[0]?.batch ?? 2);
  const selected = rows.find((r) => r.batch === selectedBatch) ?? rows[0];

  return (
    <div className="threemt-journey">
      <div className="threemt-journey-controls" role="group" aria-label="Select a chronological test batch">
        {rows.map((row) => (
          <button
            key={row.batch}
            type="button"
            className="threemt-journey-batch-btn"
            aria-pressed={row.batch === selectedBatch}
            onClick={() => setSelectedBatch(row.batch)}
          >
            Batch {row.batch}
          </button>
        ))}
      </div>

      {selected && (
        <div className="threemt-journey-readout" aria-live="polite">
          <div>
            <span className="k">Drift vs. Batch 1 (normalized Wasserstein, median across features)</span>
            <span className="v">{selected.driftWasserstein !== null ? selected.driftWasserstein.toFixed(3) : "NOT_AVAILABLE"}</span>
          </div>
          <div>
            <span className="k">MODEL-C1 (Logistic Regression) accuracy at this batch</span>
            <span className="v">{selected.modelC1Accuracy !== null ? `${(selected.modelC1Accuracy * 100).toFixed(1)}%` : "NOT_AVAILABLE"}</span>
          </div>
        </div>
      )}

      <h3>All four baseline models, accuracy by batch</h3>
      <BatchMetricLineChart data={chartData} metricKey="accuracy" models={MODELS} yLabel="Accuracy" />

      <h3>Full data (text equivalent)</h3>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Batch</th>
              <th>Drift vs. Batch 1 (normalized Wasserstein)</th>
              <th>MODEL-C1 accuracy</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.batch}>
                <td>{row.batch}</td>
                <td>{row.driftWasserstein !== null ? row.driftWasserstein.toFixed(3) : "NOT_AVAILABLE"}</td>
                <td>{row.modelC1Accuracy !== null ? `${(row.modelC1Accuracy * 100).toFixed(1)}%` : "NOT_AVAILABLE"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
