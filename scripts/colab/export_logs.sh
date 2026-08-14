#!/usr/bin/env bash
# scripts/colab/export_logs.sh — export session logs locally and (best-effort) to Drive.
# Markdown/JSONL preferred (Mission 27).
# Usage: export_logs.sh <RUN_ID> [SESSION]
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd colab

RUN_ID="${1:?usage: export_logs.sh <RUN_ID> [SESSION]}"
SESSION="${2:-$(cfg colab.sessions.cpu.name drift-tinyml-cpu)}"
LOCAL_DIR="${REPO_ROOT}/results/reproducibility/logs/${RUN_ID}"
mkdir -p "${LOCAL_DIR}"

log "Exporting logs for session '${SESSION}'..."
colab --auth=oauth2 log -s "${SESSION}" --format jsonl > "${LOCAL_DIR}/session.jsonl" \
  || die "log export FAILED for ${SESSION}"
colab --auth=oauth2 log -s "${SESSION}" --format markdown > "${LOCAL_DIR}/session.md" \
  || log "markdown log export not supported by this CLI version; jsonl retained"

DRIVE_ROOT="$(cfg colab.drive_root /content/drive/MyDrive/Drift-Robust-TinyML-Research-System)"
log "Persisting a copy to Drive (best-effort; requires mount_drive.sh already run)..."
colab --auth=oauth2 exec -s "${SESSION}" -- bash -lc "mkdir -p '${DRIVE_ROOT}/logs/${RUN_ID}'" \
  && colab --auth=oauth2 upload -s "${SESSION}" "${LOCAL_DIR}/session.jsonl" "${DRIVE_ROOT}/logs/${RUN_ID}/session.jsonl" \
  || log "Drive copy skipped (Drive not mounted or upload unsupported for this path)"

log "Logs exported to ${LOCAL_DIR}"
