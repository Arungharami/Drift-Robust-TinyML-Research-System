import type { Metadata } from "next";
import Link from "next/link";
import { PipelineStageCard } from "@/components/PipelineStage";
import { getPipeline } from "@/lib/evidence";

export const metadata: Metadata = { title: "Pipeline" };

export default function PipelinePage() {
  const stages = getPipeline();

  return (
    <div className="container">
      <div className="section-label">Pipeline</div>
      <h1>{stages.length}-stage research pipeline</h1>
      <p className="lede">
        Every stage below is defined in a version-controlled registry (
        <code>configs/pipeline_stages.yaml</code>) and exported verbatim — the web app never
        re-derives or guesses a stage&apos;s status. Prefer a visual walkthrough?{" "}
        <Link href="/process">See how these stages connect →</Link>
      </p>
      {stages.map((stage) => (
        <PipelineStageCard key={stage.id} stage={stage} />
      ))}
    </div>
  );
}
