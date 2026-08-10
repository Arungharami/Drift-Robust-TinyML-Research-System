import { NextResponse } from "next/server";
import { getExperiments } from "@/lib/evidence";

export const dynamic = "force-static";

export async function GET() {
  return NextResponse.json({ experiments: getExperiments() });
}
