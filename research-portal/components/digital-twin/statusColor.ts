// Maps evidence status to a 3D-material color. Mirrors the semantic badge
// colors in globals.css (green=verified, yellow=planned, red=failed,
// gray=not measured/blocked) so the twin never invents its own color language.

const STATUS_COLORS: Record<string, string> = {
  EXECUTED: "#3f8f5c",
  VALIDATED: "#3f8f5c",
  PLANNED: "#c9a227",
  RUNNING: "#3f6fb0",
  FAILED: "#b0473d",
  BLOCKED: "#8a8375",
  BLOCKED_HARDWARE: "#8a8375",
  PROTOCOL_FROZEN: "#8a8375",
  NOT_EXECUTED: "#8a8375",
  NOT_MEASURED: "#8a8375",
};

export function statusColor(status: string): string {
  return STATUS_COLORS[status] ?? "#8a8375";
}
