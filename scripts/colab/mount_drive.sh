#!/usr/bin/env bash
# scripts/colab/mount_drive.sh — mount Google Drive on the remote session and create the
# canonical persistent folder tree (Mission 15). Drive is persistent storage only — GitHub
# remains the canonical source-code repository.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd colab

SESSION="$(cfg colab.sessions.cpu.name drift-tinyml-cpu)"
DRIVE_ROOT="$(cfg colab.drive_root /content/drive/MyDrive/Drift-Robust-TinyML-Research-System)"

log "Mounting Drive on '${SESSION}'..."
colab --auth=oauth2 drivemount -s "${SESSION}" || die "drivemount FAILED"

log "Creating canonical persistent folder tree under ${DRIVE_ROOT}..."
colab --auth=oauth2 exec -s "${SESSION}" -- bash -lc \
  "mkdir -p '${DRIVE_ROOT}'/{environment,runs,results,artifacts,executed_notebooks,logs,checkpoints}"

log "Drive mounted and folder tree ready."
