import { StatusLegendKey } from "./StatusLegendKey";

/** Status-color key plus the mandatory conceptual-model disclaimer. Color is never the only signal — labels are always shown too. */
export function DigitalTwinLegend() {
  return (
    <div className="twin-legend">
      <p className="twin-legend-disclaimer">
        <strong>Conceptual 3D model.</strong> These shapes are schematic placeholders for the physical
        sensor array, nRF52840 board, and gateway — not a photogrammetric or CAD reconstruction of any
        real device. Every status shown is pulled from the same evidence data as the rest of this portal.
      </p>
      <StatusLegendKey />
    </div>
  );
}
