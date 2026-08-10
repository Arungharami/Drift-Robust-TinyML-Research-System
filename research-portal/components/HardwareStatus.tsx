import { EvidenceBadge } from "./EvidenceBadge";

const ROWS: { label: string; unit: string }[] = [
  { label: "Flash", unit: "KB" },
  { label: "SRAM", unit: "KB" },
  { label: "MCU inference latency", unit: "ms" },
  { label: "MCU explanation latency", unit: "ms" },
  { label: "PPK2 inference energy", unit: "µJ" },
  { label: "PPK2 explanation energy", unit: "µJ" },
];

/** Always renders NOT_EXECUTED until real PPK2/MCU artifacts exist — never a placeholder number. */
export function HardwareStatus() {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Measurement</th>
            <th>Unit</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {ROWS.map((row) => (
            <tr key={row.label}>
              <td>{row.label}</td>
              <td>{row.unit}</td>
              <td>
                <EvidenceBadge status="NOT_EXECUTED" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
