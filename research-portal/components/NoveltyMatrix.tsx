const COLUMNS = [
  "Chronological eval.",
  "Sensor drift",
  "TinyML",
  "XAI",
  "On-device XAI",
  "Fidelity",
  "Stability",
  "Physical latency",
  "Flash/SRAM",
  "Physical energy",
  "PPK2",
  "Reproducibility",
];

export interface NoveltyRow {
  paper: string;
  dataset: string;
  marks: Record<string, boolean>; // key = column name in COLUMNS
}

export function NoveltyMatrix({ rows }: { rows: NoveltyRow[] }) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Paper</th>
            <th>Dataset</th>
            {COLUMNS.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.paper}>
              <td>{row.paper}</td>
              <td>{row.dataset}</td>
              {COLUMNS.map((c) => (
                <td key={c} style={{ textAlign: "center" }}>
                  {row.marks[c] ? "✓" : "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
