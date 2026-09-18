const LEGEND: Array<{ label: string; color: string }> = [
  { label: "Executed / validated", color: "#3f8f5c" },
  { label: "Planned", color: "#c9a227" },
  { label: "Running", color: "#3f6fb0" },
  { label: "Failed", color: "#b0473d" },
  { label: "Blocked / not measured", color: "#8a8375" },
];

/** Status-color key plus the mandatory conceptual-model disclaimer. Color is never the only signal — labels are always shown too. */
export function DigitalTwinLegend() {
  return (
    <div className="twin-legend">
      <p className="twin-legend-disclaimer">
        <strong>Conceptual 3D model.</strong> These shapes are schematic placeholders for the physical
        sensor array, nRF52840 board, and gateway — not a photogrammetric or CAD reconstruction of any
        real device. Every status shown is pulled from the same evidence data as the rest of this portal.
      </p>
      <ul className="twin-legend-key">
        {LEGEND.map((item) => (
          <li key={item.label}>
            <span className="twin-legend-swatch" style={{ background: item.color }} aria-hidden="true" />
            {item.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
