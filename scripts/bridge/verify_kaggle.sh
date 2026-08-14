#!/usr/bin/env bash
# scripts/bridge/verify_kaggle.sh — verify the official `kaggle` CLI + auth; write kaggle_status.json.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd kaggle

log "=== kaggle --version ==="
KAGGLE_VERSION="$(kaggle --version 2>&1 || true)"
echo "${KAGGLE_VERSION}"

log "=== kaggle config view (harmless authenticated probe) ==="
PROBE="$(kaggle config view 2>&1 || true)"
echo "${PROBE}"

python3 "${BRIDGE_LIB_DIR}/write_platform_status.py" kaggle \
  --cli-version "${KAGGLE_VERSION}" \
  --auth-probe "${PROBE}"

log "kaggle_status.json written to results/reproducibility/bridge/kaggle_status.json"
if echo "${PROBE}" | grep -qi "authentication required"; then
  log "NOT AUTHENTICATED. Run: kaggle auth login   (interactive browser login)"
fi
