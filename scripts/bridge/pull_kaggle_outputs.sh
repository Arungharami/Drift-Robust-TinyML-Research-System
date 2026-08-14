#!/usr/bin/env bash
# scripts/bridge/pull_kaggle_outputs.sh — download outputs from a Kaggle kernel run.
# Usage: pull_kaggle_outputs.sh <kernel_id, e.g. user/drift-robust-tinyml-reproduction>
# Follow with verify_cross_platform_hashes.py to index and hash-verify what was pulled.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd kaggle

KERNEL_ID="${1:?usage: pull_kaggle_outputs.sh <kernel_id>}"
OUT_DIR="${REPO_ROOT}/results/reproducibility/kaggle_outputs/$(echo "${KERNEL_ID}" | tr '/' '_')"
mkdir -p "${OUT_DIR}"

log "Pulling outputs for ${KERNEL_ID}..."
kaggle kernels pull "${KERNEL_ID}" -p "${OUT_DIR}" -m

log "Outputs pulled to ${OUT_DIR}."
log "Run: python3 scripts/bridge/verify_cross_platform_hashes.py <local> ${OUT_DIR}/<file> --platform kaggle --remote-identifier ${KERNEL_ID} --remote-revision <version>"
