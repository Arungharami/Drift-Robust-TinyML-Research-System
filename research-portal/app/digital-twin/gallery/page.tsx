import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

export const metadata: Metadata = { title: "3D Concept Gallery" };

const visuals = [
  {
    src: "/3d/drifttwin-dashboard-concept.webp",
    title: "Integrated DriftTwin lab dashboard concept",
    alt: "Conceptual DriftTwin AI Lab dashboard showing a sensor chamber, signal acquisition, nRF52840 edge device, gateway laptop, AI cloud, telemetry charts, and evidence-aware status panels.",
    caption:
      "AI-generated concept visualization of the intended integrated laboratory experience. It is explanatory artwork, not a photograph of the physical laboratory and not evidence of hardware execution.",
  },
  {
    src: "/3d/drifttwin-system-overview.webp",
    title: "System and exploded-device concept",
    alt: "Conceptual engineering infographic showing the DriftTwin sensor-to-edge pipeline, an exploded device view, and example 3D implementation stages.",
    caption:
      "AI-generated concept visualization of the system architecture and planned device presentation. The exploded geometry is conceptual and does not represent verified CAD or a measured physical assembly.",
  },
] as const;

export default function DigitalTwinGalleryPage() {
  return (
    <div className="container digital-twin-page">
      <div className="section-label">Concept visualization</div>
      <h1>3D Concept Gallery</h1>
      <p className="lede">
        Visual design references for the DriftTwin AI Lab experience, kept separate from scientific
        evidence and physical-lab documentation.
      </p>
      <p className="twin-conceptual-flag">CONCEPT VISUALS — NOT EXPERIMENTAL EVIDENCE</p>
      <p style={{ maxWidth: "68ch" }}>
        These images communicate the intended device, laboratory, and digital-twin experience. They
        introduce no new measurement or hardware claim. Research status continues to come from the
        project evidence registry and the live <Link href="/digital-twin">Digital Twin</Link>.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 28rem), 1fr))",
          gap: "1.25rem",
          margin: "1.5rem 0 2rem",
        }}
      >
        {visuals.map((visual) => (
          <figure className="card" key={visual.src} style={{ margin: 0, overflow: "hidden" }}>
            <Image
              src={visual.src}
              alt={visual.alt}
              width={512}
              height={341}
              sizes="(max-width: 760px) 100vw, 50vw"
              style={{
                display: "block",
                width: "100%",
                height: "auto",
                borderRadius: "6px",
                border: "1px solid var(--border)",
              }}
              priority={visual.src.includes("dashboard")}
            />
            <figcaption style={{ marginTop: "1rem" }}>
              <h2 style={{ fontSize: "1.05rem", marginBottom: "0.45rem" }}>{visual.title}</h2>
              <p style={{ marginBottom: 0 }}>{visual.caption}</p>
            </figcaption>
          </figure>
        ))}
      </div>

      <p className="btn-row">
        <Link className="btn btn-primary" href="/digital-twin">
          Open interactive Digital Twin
        </Link>
        <Link className="btn" href="/digital-twin/device">
          Open exploded device view
        </Link>
        <Link className="btn" href="/system-map">
          Open system map
        </Link>
      </p>
    </div>
  );
}
