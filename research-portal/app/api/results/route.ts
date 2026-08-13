import { NextResponse } from "next/server";
import { getBaselines, getDrift } from "@/lib/evidence";

export const dynamic = "force-static";

export async function GET() {
  const baselines = getBaselines();
  const drift = getDrift();
  return NextResponse.json({
    evidence_status: baselines.evidence_status,
    fixed_origin_summary: baselines.fixed_origin_summary,
    iid_generalization_gap: baselines.iid_generalization_gap,
    global_drift_by_batch: drift.global_drift_by_batch,
    not_executed: [
      "explanation_fidelity",
      "explanation_stability",
      "explanation_latency_ms",
      "inference_latency_ms_physical",
      "flash_kb",
      "sram_kb",
      "inference_energy_uj",
      "pareto_frontier",
    ],
  });
}
