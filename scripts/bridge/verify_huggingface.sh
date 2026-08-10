#!/usr/bin/env bash
# scripts/bridge/verify_huggingface.sh — verify the CURRENT `hf` CLI + auth; write
# huggingface_status.json. Never uses the deprecated `huggingface-cli`.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd hf

log "=== hf version ==="
HF_VERSION="$(hf version 2>&1 || true)"
echo "${HF_VERSION}"

log "=== hf auth whoami ==="
WHOAMI="$(hf auth whoami 2>&1 || true)"
echo "${WHOAMI}"

python3 "${BRIDGE_LIB_DIR}/write_platform_status.py" huggingface \
  --cli-version "${HF_VERSION}" \
  --whoami "${WHOAMI}"

log "huggingface_status.json written to results/reproducibility/bridge/huggingface_status.json"
if echo "${WHOAMI}" | grep -qi "not logged in"; then
  log "NOT AUTHENTICATED. Run: hf auth login   (interactive browser login — never pass a token on the command line in a shared shell)"
fi
