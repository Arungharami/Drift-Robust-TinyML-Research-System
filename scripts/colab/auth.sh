#!/usr/bin/env bash
# scripts/colab/auth.sh — explicit OAuth2 authentication against the Colab backend.
# Interactive: follow the printed browser URL/code manually. Never prints or commits tokens —
# session state lives under ~/.config/colab-cli/ inside WSL2 only.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd colab

log "Starting OAuth2 authentication against the Colab backend."
log "If a browser URL or device code is printed below, complete it manually now."
colab --auth=oauth2 sessions

log "If the command above listed sessions (even an empty list) without an auth error, authentication succeeded."
log "Token/session state lives under ~/.config/colab-cli/ inside WSL2 and must never be committed to git."
