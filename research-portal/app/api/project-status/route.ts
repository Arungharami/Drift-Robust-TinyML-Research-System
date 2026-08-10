import { NextResponse } from "next/server";
import { pipeline, project } from "@/lib/research";

export const dynamic = "force-static";

export function GET() {
  return NextResponse.json({
    project: project.title,
    researcher: project.author,
    evidence_policy: "Only executed, saved, traceable measurements may be reported as results.",
    stages: pipeline.map(({ id, title, status }) => ({ id, title, status })),
  });
}
