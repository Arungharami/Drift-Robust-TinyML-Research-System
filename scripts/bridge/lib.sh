#!/usr/bin/env bash
# scripts/bridge/lib.sh — shared helpers sourced by every scripts/bridge/*.sh script.
# Not meant to be executed directly. Unlike scripts/colab/, these run natively on Windows via
# Git Bash — gh/hf/kaggle are not WSL-gated.
set -euo pipefail

BRIDGE_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${BRIDGE_LIB_DIR}/../.." && pwd)"
BRIDGE_CONFIG_PATH="${REPO_ROOT}/configs/research_bridge.yaml"

log()  { printf '[bridge] %s\n' "$*" >&2; }
die()  { printf '[bridge][ERROR] %s\n' "$*" >&2; exit 1; }

# cfg <dotted.key> [default] — read one value out of configs/research_bridge.yaml.
cfg() {
  python3 "${BRIDGE_LIB_DIR}/read_config.py" "$1" "${2:-}"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}
