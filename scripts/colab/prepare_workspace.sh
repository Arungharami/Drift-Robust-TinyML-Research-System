#!/usr/bin/env bash
# scripts/colab/prepare_workspace.sh — build dist/colab_workspace.tar.gz from the canonical
# local repo. Include/exclude rules come from configs/colab.yaml via src/colab_control/workspace.py
# (Mission 12). The Windows repo remains the source of truth; this bundle is disposable.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

cd "${REPO_ROOT}"
mkdir -p dist
OUT="dist/colab_workspace.tar.gz"

log "Resolving workspace file list via src/colab_control/workspace.py..."
FILELIST="$(mktemp)"
trap 'rm -f "${FILELIST}"' EXIT
python3 -m src.colab_control.workspace --root "${REPO_ROOT}" --config "${CONFIG_PATH}" > "${FILELIST}"
# Defense-in-depth: strip any stray CR (Windows text-mode stdout can emit \r\n even when the
# python-side fix in workspace.py's _cli() is bypassed) — `tar -T` treats a trailing \r as part
# of the filename and fails to find the file.
tr -d '\r' < "${FILELIST}" > "${FILELIST}.lf" && mv "${FILELIST}.lf" "${FILELIST}"

COUNT=$(wc -l < "${FILELIST}")
[ "${COUNT}" -gt 0 ] || die "workspace file list is empty; refusing to build an empty archive"
log "Bundling ${COUNT} files into ${OUT}..."

tar -czf "${OUT}" -T "${FILELIST}"
log "Workspace archive ready: ${OUT} ($(du -h "${OUT}" | cut -f1))"
