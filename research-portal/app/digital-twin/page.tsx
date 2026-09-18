import type { Metadata } from "next";
import Link from "next/link";
import { DigitalTwinLoader } from "@/components/digital-twin/DigitalTwinLoader";
import { buildTwinComponents } from "@/components/digital-twin/twin-data";

export const metadata: Metadata = { title: "Digital Twin" };

export default function DigitalTwinPage() {
  const components = buildTwinComponents();

  return (
    <div className="container digital-twin-page">
      <div className="section-label">Interactive system model</div>
      <h1>Digital Twin</h1>
      <p className="lede">
        An interactive, conceptual 3D model of the sensing-to-inference pipeline — from the sample
        chamber to the currently hardware-blocked nRF52840 edge target.
      </p>
      <p style={{ maxWidth: "62ch" }}>
        Every status shown below is read from the same evidence data as the rest of this portal —
        see the <Link href="/reproducibility">reproducibility policy</Link>. This view adds no new
        claim about hardware, models, or measurements; it visualizes the ones already documented on
        the <Link href="/pipeline">pipeline</Link> and <Link href="/hardware">hardware</Link> pages.
      </p>
      <DigitalTwinLoader components={components} />
    </div>
  );
}
