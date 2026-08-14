# Professor Review Collaboration Setup

## Purpose and boundary

The `/professor-review` page is public and read-only. It presents generated project evidence, including retained failures and hardware blockers. Reviewer uploads, comments, profile details, moderation records, and invitations are **collaboration data**, not scientific evidence. They must not be used to alter a metric, claim, experiment status, or generated evidence JSON outside the established research pipeline.

The repository currently ships the safe fallback: `BLOCKED_CONFIGURATION`. This is a collaboration deployment state only; it is deliberately absent from the scientific `EvidenceStatus` enum. Without all required configuration, the UI has no write path and `POST /api/professor-review` returns `503 COLLABORATION_NOT_CONFIGURED`.

## Enablement checklist

1. Create a Supabase project with email/OAuth authentication and configure its approved redirect URLs for the review portal.
2. Apply `supabase/migrations/20260814_professor_review_collaboration.sql` with the Supabase CLI or dashboard SQL migration facility. Review its RLS policies in a non-production project first.
3. Provision the first administrator only through a server-side, audited bootstrap process. Do not allow profile self-assignment or put a service-role key in a browser.
4. Set `COLLABORATION_FEATURE_STATE=enabled`, `NEXT_PUBLIC_SUPABASE_URL`, and `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` in the deployment environment. The supplied `.env.example` is a names-only template.
5. Install the server-side Supabase auth/session adapter and replace the configuration-gated mutation stub with handlers that check the authenticated user and database role on every request. A client-supplied `role`, `author_id`, moderation state, storage path, or visibility value is never authoritative.
6. Add a moderator-only `/professor-review/admin` screen only after that session guard exists. The current route intentionally returns 404 so an unconfigured deployment cannot expose privileged controls.

## Invitation and moderation workflow

An administrator creates a time-limited invitation. Store only a hash of its email and token in `review_invites`; send the plaintext token by email once. On acceptance, the server creates an `ACTIVE` reviewer profile. Moderators can approve, reject, quarantine, or hide submitted documents, threads, and comments; each decision is recorded in the append-only `moderation_log` with actor, target, reason, and timestamp. Revoke an invitation by expiring it, suspend an account by setting `account_status`, and hide already-published material rather than silently rewriting it.

All comments are plain text with a 5,000-character cap, server validation, output escaping, a one-reply-depth database trigger, rate limiting, and a report/moderation path. New material begins `PENDING`; public readers see only `APPROVED` + `PUBLIC` material. Private metadata, emails, storage paths, scan notes, and audit logs are never publicly selectable.

## File controls

The `professor-review` Storage bucket is private, with a 10 MiB limit and a MIME allowlist. Server handlers must additionally verify extension, normalize display names, generate UUID-based paths, compute SHA-256, reject macros/archives/executables, inspect actual file signatures, and submit every upload to malware scanning before approval. An extension or browser-provided MIME value is not sufficient malware protection. Files are downloaded through an authorized server route or short-lived signed URL; never enable public bucket listing.

## Verification before production

Run RLS tests using separate anonymous, reviewer, moderator, and admin sessions: anonymous users can read only approved public records; reviewers can create and read only their own pending submissions; moderators can review; and reviewers cannot change a role, approve content, access another reviewer’s upload, or read audit records. Confirm a nested reply is rejected, oversized/disallowed uploads are rejected, direct object URLs fail, and configuration-off requests remain 503 without side effects. Record these checks as deployment verification, not experiment evidence.

For Vercel, add only the public URL/key and feature-state variable through project environment settings. Keep `SUPABASE_SERVICE_ROLE_KEY`, mail credentials, scanner credentials, and invitation secrets server-only. Restrict Supabase auth redirect URLs, rotate keys after any exposure, enable audit/log retention appropriate to the institution, and maintain encrypted backups. Define a retention schedule before enabling uploads (for example, delete rejected uploads promptly and review material after the committee process) and document any legal/institutional hold. A separate public-API assessment is in `docs/PUBLIC_API_INTEGRATION_ASSESSMENT.md`; no public provider is enabled by this feature.
