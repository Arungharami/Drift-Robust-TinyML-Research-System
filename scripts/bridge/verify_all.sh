#!/usr/bin/env bash
# scripts/bridge/verify_all.sh — verify GitHub + Hugging Face + Kaggle bridges in one pass.
# Colab status is intentionally NOT touched here; it stays governed by scripts/colab/*.sh and
# results/reproducibility/COLAB_STATUS.md (WSL2 gate) — this script must never overwrite that.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

"${BRIDGE_LIB_DIR}/verify_github.sh"
"${BRIDGE_LIB_DIR}/verify_huggingface.sh"
"${BRIDGE_LIB_DIR}/verify_kaggle.sh"

log "All platform status files written under results/reproducibility/bridge/"
log "Run: python3 scripts/bridge/bridge_status.py   for a consolidated summary (includes Colab/Drive)."
