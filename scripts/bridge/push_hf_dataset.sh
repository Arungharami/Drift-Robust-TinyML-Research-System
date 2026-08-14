#!/usr/bin/env bash
# scripts/bridge/push_hf_dataset.sh — create (if needed) and upload the PRIVATE Hugging Face
# dataset repo with derived reproducibility evidence only. Never uploads the raw UCI archive
# (Missions 6, 33). Secret-scans the payload before every upload.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd hf

REPO_SUFFIX="$(cfg huggingface.dataset_repo drift-robust-tinyml-research-data)"
WHOAMI="$(hf auth whoami 2>&1 || true)"
if echo "${WHOAMI}" | grep -qi "not logged in"; then
  die "Not authenticated with Hugging Face. Run: hf auth login"
fi
NAMESPACE="$(echo "${WHOAMI}" | head -n1 | tr -d '[:space:]')"
REPO_ID="${NAMESPACE}/${REPO_SUFFIX}"

cd "${REPO_ROOT}"
[ -d "dist/research_bridge" ] || die "dist/research_bridge is missing; run build_release_bundle.sh first"
[ -f "platforms/huggingface/dataset/README.md" ] || die "missing dataset card: platforms/huggingface/dataset/README.md"

log "Secret-scanning upload payload..."
python3 -c "
import sys; sys.path.insert(0, '.')
from pathlib import Path
from src.research_bridge.secrets import scan_path
findings = scan_path(Path('dist/research_bridge')) + scan_path(Path('platforms/huggingface/dataset'))
if findings:
    for f in findings: print(f'  SECRET_FINDING: {f.category} in {f.location}', file=sys.stderr)
    sys.exit(1)
" || die "secret scan flagged the upload payload"

log "Creating (or confirming) PRIVATE dataset repo ${REPO_ID}..."
hf repos create "${REPO_ID}" --type dataset --private --exist-ok

log "Uploading dataset card..."
hf upload "${REPO_ID}" platforms/huggingface/dataset/README.md README.md --type dataset --commit-message "dataset card"

log "Uploading release bundle evidence..."
hf upload "${REPO_ID}" dist/research_bridge evidence --type dataset --commit-message "reproducibility evidence bundle"

log "Done. Repo: https://huggingface.co/datasets/${REPO_ID} (PRIVATE). Verify with verify_cross_platform_hashes.py before trusting the upload."
