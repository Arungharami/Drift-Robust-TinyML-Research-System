import type { Metadata } from "next";
import Link from "next/link";
import { HardwareStatus } from "@/components/HardwareStatus";
import { DeviceLoader } from "@/components/digital-twin/DeviceLoader";
import { DeviceStatusTimeline } from "@/components/digital-twin/DeviceStatusTimeline";
import { buildDeviceLayers } from "@/components/digital-twin/device-data";

export const metadata: Metadata = { title: "Device View" };

export default function DigitalTwinDevicePage() {
  const layers = buildDeviceLayers();

  return (
    <div className="container digital-twin-page">
      <div className="section-label">Interactive system model</div>
      <p className="twin-conceptual-flag">CONCEPTUAL ENGINEERING VIEW</p>
      <h1>Device View</h1>
      <p className="lede">
        An exploded, layer-by-layer look at the planned physical TinyML device — from enclosure
        down to the nRF52840 MCU.
      </p>
      <p style={{ maxWidth: "62ch" }}>
        This is a schematic engineering placeholder, not a CAD export or photogrammetric
        reconstruction of a built device. Every status below is read from the same evidence as{" "}
        <Link href="/hardware">/hardware</Link> and <Link href="/tinyml">/tinyml</Link> — nothing
        here is estimated or simulated.
      </p>
      <p className="btn-row" style={{ margin: "0 0 1.5rem" }}>
        <Link className="btn" href="/digital-twin">
          ← Digital twin overview
        </Link>
        <Link className="btn" href="/system-map">
          Explore full system architecture →
        </Link>
      </p>

      <DeviceLoader layers={layers} />

      <h2>Engineering progress</h2>
      <DeviceStatusTimeline />

      <h2>Resource evidence</h2>
      <p style={{ maxWidth: "62ch" }}>
        No zeros, estimates, simulated values, or host-to-MCU conversions are presented — see the
        full <Link href="/hardware">hardware page</Link> for the measurement methodology.
      </p>
      <HardwareStatus />
    </div>
  );
}
