import { EvidenceBadge } from "./EvidenceBadge";

const ROWS = [
  { label: "Linked ROM / Flash", unit: "KB" },
  { label: "Static / peak SRAM", unit: "KB" },
  { label: "MCU inference latency", unit: "ms" },
  { label: "MCU explanation latency", unit: "ms" },
  { label: "PPK2 inference energy", unit: "µJ" },
  { label: "PPK2 explanation energy", unit: "µJ" },
];

/** Always renders NOT_EXECUTED until real PPK2/MCU artifacts exist — never a placeholder number. */
export function HardwareStatus() {
  return (
    <div className="hardware-measurements" aria-label="Hardware measurement status">
      <div className="hardware-measurement-table table-scroll"><table>
        <thead>
          <tr>
            <th>Measurement</th>
            <th>Unit</th>
            <th>Current state</th>
          </tr>
        </thead>
        <tbody>
          {ROWS.map((row) => (
            <tr key={row.label}>
              <td>{row.label}</td>
              <td>{row.unit}</td>
              <td>
                <EvidenceBadge status="NOT_MEASURED" />
              </td>
            </tr>
          ))}
        </tbody>
      </table></div>
      <div className="hardware-measurement-cards">
        {ROWS.map((row) => <article className="measurement-card" key={row.label}><div><strong>{row.label}</strong><span>{row.unit}</span></div><EvidenceBadge status="NOT_MEASURED" /></article>)}
      </div>
    </div>
  );
}
