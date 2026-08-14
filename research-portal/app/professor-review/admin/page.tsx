import { notFound } from "next/navigation";

/**
 * No moderator screen is exposed before a server-side Supabase session and role
 * guard are deployed. This prevents an unconfigured deployment from presenting
 * inert controls as if they were an authorization boundary.
 */
export default function ProfessorReviewAdminPage() {
  notFound();
}
