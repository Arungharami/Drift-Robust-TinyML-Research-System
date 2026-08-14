#!/usr/bin/env bash
# scripts/colab/stop.sh — stop a named session and VERIFY it actually stopped before reporting
# success. Never report SESSION_STOPPED = YES without this verification (Mission 29).
# Usage: stop.sh [SESSION]  (defaults to the canonical CPU session)
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd colab

SESSION="${1:-$(cfg colab.sessions.cpu.name drift-tinyml-cpu)}"

log "Stopping session '${SESSION}'..."
colab --auth=oauth2 stop -s "${SESSION}" || die "stop command FAILED for ${SESSION}"

log "Verifying stop via 'colab sessions'..."
if colab --auth=oauth2 sessions | grep -q "${SESSION}"; then
  die "SESSION_STOPPED = NO — '${SESSION}' still listed. Do not report as stopped."
fi
log "SESSION_STOPPED = YES (verified) for '${SESSION}'."
