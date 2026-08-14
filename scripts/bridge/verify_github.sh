#!/usr/bin/env bash
# scripts/bridge/verify_github.sh — verify GitHub CLI + repo state; write github_status.json.
# GitHub is canonical (Mission 3). Never uses --show-token.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd gh
require_cmd git

log "=== gh --version ==="
GH_VERSION="$(gh --version | head -n1)"
echo "${GH_VERSION}"

log "=== gh auth status ==="
AUTH_STATUS="$(gh auth status 2>&1 || true)"
echo "${AUTH_STATUS}"

log "=== git remote -v ==="
git remote -v

log "=== git branch --show-current ==="
BRANCH="$(git branch --show-current)"
echo "${BRANCH}"

log "=== git rev-parse HEAD ==="
SHA="$(git rev-parse HEAD)"
echo "${SHA}"

python3 "${BRIDGE_LIB_DIR}/write_platform_status.py" github \
  --cli-version "${GH_VERSION}" \
  --auth-status "${AUTH_STATUS}" \
  --repository "$(cfg github.repository)" \
  --branch "${BRANCH}" \
  --commit "${SHA}" \
  --remote "$(git remote get-url origin 2>/dev/null || echo unknown)"

log "github_status.json written to results/reproducibility/bridge/github_status.json"
