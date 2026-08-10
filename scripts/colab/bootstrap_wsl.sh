#!/usr/bin/env bash
# scripts/colab/bootstrap_wsl.sh — run INSIDE WSL2 Ubuntu.
# Installs/verifies uv, python3, git needed to host the Colab CLI control plane.
# Idempotent: safe to re-run.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

log "Verifying WSL2 host prerequisites..."
uname -a || true

if ! command -v python3 >/dev/null 2>&1; then
  die "python3 not found. Install with: sudo apt-get update && sudo apt-get install -y python3 python3-pip"
fi
log "python3: $(python3 --version)"

if ! command -v git >/dev/null 2>&1; then
  die "git not found. Install with: sudo apt-get update && sudo apt-get install -y git"
fi
log "git: $(git --version)"

if command -v uv >/dev/null 2>&1; then
  log "uv already installed: $(uv --version)"
else
  log "Installing uv (astral-sh)..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  require_cmd uv
  log "uv installed: $(uv --version)"
fi

log "WSL2 bootstrap complete."
