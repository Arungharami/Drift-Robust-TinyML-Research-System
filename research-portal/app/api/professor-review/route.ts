import { NextResponse } from "next/server";
import { COLLABORATION_NOT_CONFIGURED, collaborationConfigured } from "@/lib/collaboration";

/** Mutations deliberately stay unavailable until Supabase auth/RLS is configured. */
export async function POST() {
  if (!collaborationConfigured()) {
    return NextResponse.json({ error: COLLABORATION_NOT_CONFIGURED, message: "Reviewer collaboration is not configured." }, { status: 503 });
  }
  return NextResponse.json({ error: "NOT_IMPLEMENTED", message: "Use the server-authorized Supabase mutation handlers after deployment configuration." }, { status: 501 });
}
