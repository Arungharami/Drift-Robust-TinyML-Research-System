import type { Metadata } from "next";
import { EvidenceBadge } from "@/components/EvidenceBadge";
import { ArtifactLink } from "@/components/ArtifactLink";
import { getDataset } from "@/lib/evidence";

export const metadata: Metadata = { title: "Dataset" };

const CLASS_NAMES: Record<string, string> = {
  "1": "Ethanol",
  "2": "Ethylene",
  "3": "Ammonia",
  "4": "Acetaldehyde",
  "5": "Acetone",
  "6": "Toluene",
};

export default function DatasetPage() {
  const dataset = getDataset();
  const v = dataset.validation;

  return (
    <div className="container">
      <div className="section-label">Dataset</div>
      <div style={{ marginBottom: "0.75rem" }}>
        <EvidenceBadge status={dataset.evidence_status} />
      </div>
      <h1>UCI Gas Sensor Array Drift Dataset</h1>
      <p className="lede">
        Source: <a href={dataset.source_url} target="_blank" rel="noreferrer">{dataset.source}</a>{" "}
        (Vergara et al.). Collected over 36 months from a 16-sensor chemical array exposed to six
        gases at varying concentrations. This project does not redistribute the raw archive —
        download it directly from UCI and verify the hash below.
      </p>

      {v ? (
        <>
          <h2>Verified structure</h2>
          <div className="kv-grid">
            <div className="kv-item"><div className="k">Observations</div><div className="v">{v.samples.toLocaleString()}</div></div>
            <div className="kv-item"><div className="k">Features</div><div className="v">{v.features}</div></div>
            <div className="kv-item"><div className="k">Chronological batches</div><div className="v">{v.batches}</div></div>
            <div className="kv-item"><div className="k">Gas classes</div><div className="v">{v.classes}</div></div>
            <div className="kv-item"><div className="k">Missing values</div><div className="v">{v.missing_values}</div></div>
            <div className="kv-item"><div className="k">Malformed rows</div><div className="v">{v.malformed_rows.length}</div></div>
          </div>

          <h2>Batch composition (chronological)</h2>
          <div className="table-scroll">
            <table>
              <thead><tr><th>Batch</th><th>Observations</th><th>Batch archive SHA-256</th></tr></thead>
              <tbody>
                {Object.entries(v.batch_rows).map(([batch, rows]) => (
                  <tr key={batch}>
                    <td>Batch {batch}</td>
                    <td>{rows.toLocaleString()}</td>
                    <td><code style={{ fontSize: "0.72rem" }}>{v.batch_hashes[`batch${batch}.dat`]}</code></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h2>Gas classes</h2>
          <div className="table-scroll">
            <table>
              <thead><tr><th>Class ID</th><th>Gas</th><th>Total labeled observations</th></tr></thead>
              <tbody>
                {Object.entries(v.labels).map(([cls, count]) => (
                  <tr key={cls}>
                    <td>{cls}</td>
                    <td>{CLASS_NAMES[cls] ?? "—"}</td>
                    <td>{count.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h2>Processed dataset hash</h2>
          <p>
            <code style={{ fontSize: "0.8rem" }}>{v.dataset_hash}</code>
          </p>
          <p style={{ fontSize: "0.85rem" }}>
            Full validation artifact: <ArtifactLink path={dataset.artifact_path} />
          </p>
        </>
      ) : (
        <div className="empty-state">Dataset validation artifact not found.</div>
      )}

      <h2>Why chronological, not random, splitting</h2>
      <p style={{ maxWidth: "68ch" }}>
        Sensor drift means the feature distribution at batch 10 differs measurably from batch 1
        (see <a href="/results">drift evidence</a>). A random train/test split mixes observations
        from all batches into both sets, letting a model implicitly learn future-batch
        characteristics it would never have access to in deployment — inflating apparent
        accuracy. This project treats <code>FIXED_ORIGIN</code> (train on Batch 1 only, evaluate
        on Batches 2–10 in order) as the primary protocol, and includes an explicit{" "}
        <code>IID_DIAGNOSTIC</code> split only to quantify how much random splitting overstates
        performance — never as a headline result. See{" "}
        <a href="/methodology">Methodology</a> for the full protocol definition.
      </p>

      <h2>Chronological split, visualized</h2>
      <div className="diagram-flow" role="img" aria-label="Batch 1 trains the model; batches 2 through 10 are evaluated in chronological order">
        <span className="diagram-step" style={{ background: "var(--status-executed-bg)", color: "var(--status-executed-fg)", borderColor: "transparent" }}>
          Batch 1 — train
        </span>
        <span className="diagram-arrow" aria-hidden="true">→</span>
        {[2, 3, 4, 5, 6, 7, 8, 9, 10].map((b) => (
          <span key={b} className="diagram-step">Batch {b} — test</span>
        ))}
      </div>
    </div>
  );
}
