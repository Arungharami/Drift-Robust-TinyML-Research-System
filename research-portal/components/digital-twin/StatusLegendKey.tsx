export const STATUS_LEGEND: Array<{ label: string; color: string }> = [
  { label: "Executed / validated", color: "#3f8f5c" },
  { label: "Planned", color: "#c9a227" },
  { label: "Running", color: "#3f6fb0" },
  { label: "Failed", color: "#b0473d" },
  { label: "Blocked / not measured", color: "#8a8375" },
];

/** Shared status-color key list, used by both the digital-twin and device-view legends. */
export function StatusLegendKey() {
  return (
    <ul className="twin-legend-key">
      {STATUS_LEGEND.map((item) => (
        <li key={item.label}>
          <span className="twin-legend-swatch" style={{ background: item.color }} aria-hidden="true" />
          {item.label}
        </li>
      ))}
    </ul>
  );
}
