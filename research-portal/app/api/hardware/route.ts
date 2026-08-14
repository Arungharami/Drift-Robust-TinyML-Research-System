import { NextResponse } from "next/server";

export const dynamic = "force-static";

// No physical hardware artifact exists yet. This endpoint reports that honestly rather than
// omitting the route or fabricating placeholder numbers.
export async function GET() {
  return NextResponse.json({
    target_mcu: "Nordic nRF52840 (ARM Cortex-M4F)",
    energy_instrument: "Nordic Power Profiler Kit II (PPK2)",
    measurements: {
      flash_kb: null,
      sram_kb: null,
      inference_latency_ms: null,
      explanation_latency_ms: null,
      inference_energy_uj: null,
      explanation_energy_uj: null,
    },
    evidence_status: "NOT_EXECUTED",
  });
}
