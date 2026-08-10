#!/usr/bin/env bash
# scripts/colab/verify_cli.sh — verify (and update, never duplicate-install) the real
# google-colab-cli inside WSL2. Never reports `gh` (GitHub CLI) as the Colab CLI.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

require_cmd uv

if command -v colab >/dev/null 2>&1; then
  log "colab CLI found at: $(command -v colab)"
  if [ "$(command -v colab)" = "$(command -v gh 2>/dev/null || true)" ]; then
    die "'colab' resolves to the GitHub CLI binary — this is the wrong tool. Fix PATH."
  fi
  colab version || die "colab found but 'colab version' failed"
  log "Checking for an update via uv..."
  uv tool upgrade google-colab-cli || log "no update available or upgrade unsupported by this uv version; continuing"
else
  log "colab CLI not found. Installing google-colab-cli via uv..."
  uv tool install google-colab-cli
  require_cmd colab
fi

log "=== colab version ==="
colab version

log "=== colab --help (first 40 lines) ==="
colab --help | head -n 40
