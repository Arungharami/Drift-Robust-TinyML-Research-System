#!/usr/bin/env bash
# scripts/colab/lib.sh — shared helpers sourced by every scripts/colab/*.sh script.
# Not meant to be executed directly. Intended to run inside WSL2 Ubuntu.
set -euo pipefail

COLAB_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${COLAB_LIB_DIR}/../.." && pwd)"
CONFIG_PATH="${REPO_ROOT}/configs/colab.yaml"

log()  { printf '[colab] %s\n' "$*" >&2; }
die()  { printf '[colab][ERROR] %s\n' "$*" >&2; exit 1; }

# cfg <dotted.key> [default] — read one value out of configs/colab.yaml.
cfg() {
  python3 "${COLAB_LIB_DIR}/read_config.py" "$1" "${2:-}"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

timestamp_utc() { date -u +%Y%m%dT%H%M%SZ; }
