import type { Metadata } from "next";
import Link from "next/link";
import { SystemMapExplorer } from "@/components/system-map/SystemMapExplorer";
import { buildSystemComponents } from "@/lib/digital-twin/system-components";

export const metadata: Metadata = { title: "System Map" };

interface SystemMapPageProps {
  searchParams: Promise<{ stage?: string }>;
}

export default async function SystemMapPage({ searchParams }: SystemMapPageProps) {
  const components = buildSystemComponents();
  const { stage } = await searchParams;

  return (
    <div className="container digital-twin-page">
      <div className="section-label">Complete research architecture</div>
      <h1>System Map</h1>
      <p className="lede">
        The end-to-end pipeline from physical sample to evidence ledger, grouped by domain and
        linked by dependency.
      </p>
      <p style={{ maxWidth: "68ch" }}>
        <strong>Every status below is a research/evidence status, not a software-implementation status.</strong>{" "}
        A stage appearing on this map means it is documented here — it does not mean the stage
        itself has been implemented or executed. Statuses are read from the same evidence as{" "}
        <Link href="/pipeline">/pipeline</Link>, <Link href="/xai">/xai</Link>, and{" "}
        <Link href="/hardware">/hardware</Link>.
      </p>
      <p className="btn-row" style={{ margin: "0 0 1.5rem" }}>
        <Link className="btn" href="/digital-twin">
          Open 3D digital twin →
        </Link>
        <Link className="btn" href="/digital-twin/device">
          Open device view →
        </Link>
      </p>

      <SystemMapExplorer components={components} initialStage={stage ?? null} />
    </div>
  );
}
