import type { Metadata } from "next";
import Link from "next/link";
import { ProcessExplorer } from "@/components/process/ProcessExplorer";
import { getPipeline, getProjectStatus } from "@/lib/evidence";
import { buildProcessPhases } from "@/lib/process-phases";

export const metadata: Metadata = { title: "How It Works" };

export default function ProcessPage() {
  const stages = getPipeline();
  const phases = buildProcessPhases(stages);
  const status = getProjectStatus();

  return (
    <div className="container process-page">
      <div className="section-label">Process overview</div>
      <h1>How the research system works</h1>
      <p className="lede">
        An interactive walk through all {status.pipeline_total_stages} pipeline stages, grouped into six phases from raw
        sensor data to embedded deployment. Drag to rotate, or switch to the list view — either way, every color and
        dependency line below reads the same registry as the <Link href="/pipeline">full pipeline page</Link>. Nothing here
        is illustrative or invented.
      </p>

      <ProcessExplorer phases={phases} />

      <div className="process-footer-links">
        <p>
          <Link href="/pipeline">See every stage, artifact, and dependency in detail →</Link>
        </p>
        <p>
          <Link href="/hardware">See the planned physical deployment →</Link>
        </p>
      </div>
    </div>
  );
}
