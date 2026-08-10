#!/usr/bin/env bash
# scripts/colab/start_cpu.sh — create/reuse the canonical CPU session (drift-tinyml-cpu).
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd colab

SESSION="$(cfg colab.sessions.cpu.name drift-tinyml-cpu)"

log "Checking for existing session '${SESSION}'..."
if colab --auth=oauth2 sessions | grep -q "${SESSION}"; then
  log "Session '${SESSION}' already exists; reusing it."
else
  log "Creating CPU session '${SESSION}'..."
  colab --auth=oauth2 new -s "${SESSION}"
fi

colab --auth=oauth2 status -s "${SESSION}"
