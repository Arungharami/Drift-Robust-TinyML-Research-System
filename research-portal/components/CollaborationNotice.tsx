import { collaborationState } from "@/lib/collaboration";

export function CollaborationNotice() {
  const state = collaborationState();
  if (state === "CONFIGURED") {
    return <aside className="collaboration-notice collaboration-ready"><strong>CONFIGURED</strong><p>Reviewer actions require an authenticated account and server-side role authorization.</p></aside>;
  }
  return <aside className="collaboration-notice" aria-live="polite"><strong>BLOCKED_CONFIGURATION</strong><p>Reviewer access is not configured. Public material remains read-only; no uploads, comments, accounts, or moderation records are created.</p><button type="button" disabled aria-describedby="collaboration-configuration-note">Reviewer actions unavailable</button><small id="collaboration-configuration-note">This is a deployment configuration state, not a scientific-evidence status.</small></aside>;
}
