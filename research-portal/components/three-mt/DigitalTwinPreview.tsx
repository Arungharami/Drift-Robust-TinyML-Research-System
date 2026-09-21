import Link from "next/link";
import { DigitalTwinLoader } from "@/components/digital-twin/DigitalTwinLoader";
import type { TwinComponent } from "@/components/digital-twin/types";

const PIPELINE = [
  { label: "Real World", detail: "Sensor" },
  { label: "Digital Twin", detail: "Chronological data" },
  { label: "AI", detail: "Prediction" },
  { label: "XAI", detail: "Explanation" },
  { label: "Edge", detail: "nRF52840 target" },
  { label: "Evidence", detail: "Reproducible experiment record" },
];

/** Section 12 — frames the existing interactive digital twin as a research artifact, not decoration. */
export function DigitalTwinPreview({ components }: { components: TwinComponent[] }) {
  return (
    <section className="threemt-twin-preview" aria-labelledby="threemt-twin-title">
      <h2 id="threemt-twin-title">The Digital Twin</h2>
      <ol className="threemt-twin-pipeline">
        {PIPELINE.map((step, i) => (
          <li key={step.label}>
            <span className="threemt-twin-pipeline-label">{step.label}</span>
            <span className="threemt-twin-pipeline-detail">{step.detail}</span>
            {i < PIPELINE.length - 1 ? <span className="threemt-twin-pipeline-arrow" aria-hidden="true">→</span> : null}
          </li>
        ))}
      </ol>
      <p style={{ maxWidth: "68ch" }}>
        Every node below is real and evidence-linked — select one to see its actual status, not a
        decorative diagram. This is the same digital twin used on{" "}
        <Link href="/digital-twin">/digital-twin</Link>.
      </p>
      <DigitalTwinLoader components={components} />
    </section>
  );
}
