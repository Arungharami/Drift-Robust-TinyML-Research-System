#!/usr/bin/env bash
# scripts/colab/start_gpu.sh — create/reuse the optional GPU session with a requested profile.
# Usage: start_gpu.sh [T4|L4|G4|A100]   (defaults to T4)
# An allocation failure is reported as GPU_ALLOCATION_UNAVAILABLE, never as a scientific failure.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd colab

GPU_TYPE="${1:-T4}"
SESSION="$(cfg colab.sessions.gpu.name drift-tinyml-gpu)"

case "${GPU_TYPE}" in
  T4|L4|G4|A100) ;;
  *) die "Unsupported GPU profile '${GPU_TYPE}'. Supported: T4 L4 G4 A100" ;;
esac

log "Inspecting supported flags before relying on syntax: colab new --help"
colab new --help || true

log "Requesting GPU session '${SESSION}' (${GPU_TYPE})..."
if ! colab --auth=oauth2 new -s "${SESSION}" --gpu "${GPU_TYPE}"; then
  log "GPU_ALLOCATION_UNAVAILABLE (or GPU_NOT_AVAILABLE_TO_ACCOUNT) for profile ${GPU_TYPE}."
  log "This is an allocation/account limitation, not a scientific failure."
  exit 2
fi

colab --auth=oauth2 status -s "${SESSION}"
