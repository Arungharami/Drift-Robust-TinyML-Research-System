#!/usr/bin/env bash
# scripts/colab/run_notebook.sh — execute one notebook on the remote session as an execution
# copy (the canonical notebook file is never modified in place), then persist the executed
# copy locally under runs/<RUN_ID>/executed_notebooks (Mission 18).
# Usage: run_notebook.sh <notebook_path_relative_to_repo> <RUN_ID>
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd colab

NOTEBOOK="${1:?usage: run_notebook.sh <notebook> <run_id>}"
RUN_ID="${2:?usage: run_notebook.sh <notebook> <run_id>}"
SESSION="$(cfg colab.sessions.cpu.name drift-tinyml-cpu)"
REMOTE_WORKSPACE="$(cfg colab.remote_workspace /content/drift_tinyml_enose)"
NB_NAME="$(basename "${NOTEBOOK}")"
REMOTE_RUN_DIR="runs/${RUN_ID}/executed_notebooks"

log "Executing ${NOTEBOOK} as an execution copy on '${SESSION}'..."
colab --auth=oauth2 exec -s "${SESSION}" -- bash -lc "
  cd '${REMOTE_WORKSPACE}' &&
  mkdir -p '${REMOTE_RUN_DIR}' &&
  jupyter nbconvert --to notebook --execute '${NOTEBOOK}' \
    --output '${REMOTE_RUN_DIR}/${NB_NAME}' --ExecutePreprocessor.timeout=1800
" || die "Notebook execution FAILED: ${NOTEBOOK}"

mkdir -p "${REPO_ROOT}/runs/${RUN_ID}/executed_notebooks"
log "Downloading executed notebook copy..."
colab --auth=oauth2 download -s "${SESSION}" \
  "${REMOTE_WORKSPACE}/${REMOTE_RUN_DIR}/${NB_NAME}" \
  "${REPO_ROOT}/runs/${RUN_ID}/executed_notebooks/${NB_NAME}" \
  || die "Download of executed notebook FAILED"

log "Notebook ${NB_NAME} executed and persisted for run ${RUN_ID}."
