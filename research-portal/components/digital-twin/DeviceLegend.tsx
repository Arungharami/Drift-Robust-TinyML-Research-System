import { StatusLegendKey } from "./StatusLegendKey";

/** Device-view disclaimer: this is the mandatory "conceptual engineering view" label from the device-view spec. */
export function DeviceLegend() {
  return (
    <div className="twin-legend">
      <p className="twin-legend-disclaimer twin-conceptual-flag">CONCEPTUAL ENGINEERING VIEW</p>
      <p className="twin-legend-disclaimer">
        This exploded model is a schematic engineering placeholder for the planned physical
        enclosure, PCB, and MCU stack — not a CAD export or photogrammetric reconstruction of any
        built device. No electrical components are named unless they are already selected in the
        repository (currently only the nRF52840 target itself). Every status shown is pulled from
        the same evidence data as the rest of this portal.
      </p>
      <StatusLegendKey />
    </div>
  );
}
