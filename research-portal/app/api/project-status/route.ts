import { NextResponse } from "next/server";
import { getPipeline, getPlatform, getProjectStatus } from "@/lib/evidence";

export const dynamic = "force-static";

export async function GET() {
  const status = getProjectStatus();
  const pipeline = getPipeline();
  const platform = getPlatform();

  return NextResponse.json({
    project: status.project,
    repository: status.repository,
    branch: status.branch,
    git_commit: status.git_commit,
    last_updated: status.last_updated,
    pipeline_stages: pipeline.map((s) => ({ id: s.id, name: s.name, status: s.status })),
    hardware_state: status.hardware_state,
    paper_state: status.paper_state,
    platform_bridge: {
      github: platform.github?.authenticated ?? false,
      huggingface: platform.huggingface?.authenticated ?? false,
      kaggle: platform.kaggle?.authenticated ?? false,
    },
  });
}
