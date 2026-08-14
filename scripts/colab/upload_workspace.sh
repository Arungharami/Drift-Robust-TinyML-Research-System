#!/usr/bin/env bash
# scripts/colab/upload_workspace.sh — upload dist/colab_workspace.tar.gz to the canonical remote
# workspace and verify extraction before allowing anything downstream to proceed (Mission 13).
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd colab

cd "${REPO_ROOT}"
ARCHIVE="dist/colab_workspace.tar.gz"
[ -f "${ARCHIVE}" ] || die "Missing ${ARCHIVE}; run prepare_workspace.sh first"

SESSION="$(cfg colab.sessions.cpu.name drift-tinyml-cpu)"
REMOTE_WORKSPACE="$(cfg colab.remote_workspace /content/drift_tinyml_enose)"

log "Uploading ${ARCHIVE} to session '${SESSION}'..."
colab --auth=oauth2 upload -s "${SESSION}" "${ARCHIVE}" "/content/colab_workspace.tar.gz"

log "Extracting on remote to ${REMOTE_WORKSPACE}..."
colab --auth=oauth2 exec -s "${SESSION}" -- bash -lc \
  "mkdir -p '${REMOTE_WORKSPACE}' && tar -xzf /content/colab_workspace.tar.gz -C '${REMOTE_WORKSPACE}'"

log "Verifying required paths exist remotely..."
colab --auth=oauth2 exec -s "${SESSION}" -- bash -lc "
  test -f '${REMOTE_WORKSPACE}/README.md' &&
  test -d '${REMOTE_WORKSPACE}/src' &&
  test -d '${REMOTE_WORKSPACE}/configs' &&
  test -d '${REMOTE_WORKSPACE}/notebooks' &&
  echo WORKSPACE_VERIFIED_OK
" || die "Remote workspace verification FAILED — do not proceed to install/execute steps"
