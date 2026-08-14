#!/usr/bin/env bash
# scripts/colab/download_results.sh — download only small validated artifacts (metrics,
# manifests, logs, figures, tables, executed notebooks). Large model checkpoints stay in
# Drive/artifact store and are never downloaded here (Mission 28).
# Usage: download_results.sh <RUN_ID>
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd colab

RUN_ID="${1:?usage: download_results.sh <RUN_ID>}"
SESSION="$(cfg colab.sessions.cpu.name drift-tinyml-cpu)"
REMOTE_WORKSPACE="$(cfg colab.remote_workspace /content/drift_tinyml_enose)"
LOCAL_DIR="${REPO_ROOT}/runs/${RUN_ID}"
mkdir -p "${LOCAL_DIR}"

for sub in manifest.json config predictions metrics figures tables logs executed_notebooks; do
  log "Downloading runs/${RUN_ID}/${sub} ..."
  colab --auth=oauth2 download -s "${SESSION}" \
    "${REMOTE_WORKSPACE}/runs/${RUN_ID}/${sub}" "${LOCAL_DIR}/${sub}" 2>/dev/null \
    || log "  (skipped: ${sub} not present remotely)"
done

log "Download complete: ${LOCAL_DIR}"
