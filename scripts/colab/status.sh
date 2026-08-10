#!/usr/bin/env bash
# scripts/colab/status.sh — report all sessions plus explicit status of the canonical CPU/GPU sessions.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd colab

log "=== colab sessions ==="
colab --auth=oauth2 sessions

CPU_SESSION="$(cfg colab.sessions.cpu.name drift-tinyml-cpu)"
GPU_SESSION="$(cfg colab.sessions.gpu.name drift-tinyml-gpu)"

log "=== status: ${CPU_SESSION} ==="
colab --auth=oauth2 status -s "${CPU_SESSION}" || log "${CPU_SESSION} not running"

log "=== status: ${GPU_SESSION} ==="
colab --auth=oauth2 status -s "${GPU_SESSION}" || log "${GPU_SESSION} not running"
