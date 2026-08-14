/** Server-safe collaboration configuration. No client role or moderation field is trusted. */
export const COLLABORATION_NOT_CONFIGURED = "COLLABORATION_NOT_CONFIGURED";

export type ReviewRole = "PUBLIC_READER" | "REVIEWER" | "MODERATOR" | "ADMIN";

export function collaborationConfigured(): boolean {
  return process.env.COLLABORATION_FEATURE_STATE === "enabled"
    && Boolean(process.env.NEXT_PUBLIC_SUPABASE_URL)
    && Boolean(process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY);
}

export function collaborationState() {
  return collaborationConfigured() ? "CONFIGURED" : "BLOCKED_CONFIGURATION";
}

export const uploadPolicy = {
  maxBytes: Number(process.env.COLLABORATION_MAX_UPLOAD_BYTES ?? 10 * 1024 * 1024),
  extensions: ["pdf", "docx", "txt", "md", "csv", "png", "jpg", "jpeg"],
  rejectedExtensions: ["exe", "msi", "bat", "cmd", "ps1", "sh", "html", "htm", "svg", "zip", "rar", "7z", "docm", "xlsm"],
} as const;

export function safeDisplayFilename(name: string): string {
  return name.normalize("NFKC").replace(/[\\/:*?"<>|\u0000-\u001f]/g, "_").replace(/\s+/g, " ").trim().slice(0, 160) || "review-document";
}

export function validatePlainTextComment(body: unknown): string | null {
  if (typeof body !== "string") return null;
  const value = body.trim();
  if (!value || value.length > 5000 || /<\/?[a-z][^>]*>/i.test(value)) return null;
  return value;
}
