#!/usr/bin/env bash
# scripts/bridge/push_hf_model.sh — create (if needed) and upload the PRIVATE Hugging Face
# model repo. REFUSES to run unless a bundle with manifest.json status == COMPLETED is passed
# (Mission 21). No model evidence exists yet at this checkpoint, so this script is inert until
# one does — that is intentional, not a bug.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd hf

MODEL_BUNDLE_DIR="${1:-}"
[ -n "${MODEL_BUNDLE_DIR}" ] || die "usage: push_hf_model.sh <path to a COMPLETED experiment's model bundle>"
[ -f "${MODEL_BUNDLE_DIR}/manifest.json" ] || die "missing ${MODEL_BUNDLE_DIR}/manifest.json — refusing to publish an unvalidated bundle"

STATUS="$(python3 -c "import json; print(json.load(open('${MODEL_BUNDLE_DIR}/manifest.json')).get('status','UNKNOWN'))")"
[ "${STATUS}" = "COMPLETED" ] || die "bundle status is '${STATUS}', not COMPLETED — refusing to publish (Mission 21)"

REPO_SUFFIX="$(cfg huggingface.model_repo drift-robust-tinyml-models)"
WHOAMI="$(hf auth whoami 2>&1 || true)"
if echo "${WHOAMI}" | grep -qi "not logged in"; then
  die "Not authenticated with Hugging Face. Run: hf auth login"
fi
NAMESPACE="$(echo "${WHOAMI}" | head -n1 | tr -d '[:space:]')"
REPO_ID="${NAMESPACE}/${REPO_SUFFIX}"

log "Secret-scanning ${MODEL_BUNDLE_DIR}..."
python3 -c "
import sys; sys.path.insert(0, '.')
from pathlib import Path
from src.research_bridge.secrets import scan_path
findings = scan_path(Path('${MODEL_BUNDLE_DIR}'))
if findings:
    for f in findings: print(f'  SECRET_FINDING: {f.category} in {f.location}', file=sys.stderr)
    sys.exit(1)
" || die "secret scan flagged the model bundle"

log "Creating (or confirming) PRIVATE model repo ${REPO_ID}..."
hf repos create "${REPO_ID}" --type model --private --exist-ok

log "Uploading model bundle..."
hf upload "${REPO_ID}" "${MODEL_BUNDLE_DIR}" . --type model --commit-message "validated model release"

log "Done. Repo: https://huggingface.co/${REPO_ID} (PRIVATE). Verify with verify_cross_platform_hashes.py before trusting the upload."
