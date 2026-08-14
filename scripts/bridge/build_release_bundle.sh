#!/usr/bin/env bash
# scripts/bridge/build_release_bundle.sh — build dist/research_bridge/ from small validated
# evidence (manifests, metrics, tables, dataset/model cards, configs). Never includes secrets
# or the raw UCI archive (Mission 17). Secret-scans the assembled bundle before declaring it safe.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

cd "${REPO_ROOT}"
OUT_DIR="dist/research_bridge"
rm -rf "${OUT_DIR}"
mkdir -p "${OUT_DIR}"

log "Resolving release-bundle file list via src/research_bridge/release_bundle.py..."
FILELIST="$(mktemp)"
trap 'rm -f "${FILELIST}"' EXIT
python3 -c "
import sys
sys.path.insert(0, '.')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(newline='\n')  # avoid \r\n on Windows breaking the bash 'while read' below
from pathlib import Path
from src.research_bridge.config import load_config, get_value
from src.research_bridge.release_bundle import collect_release_files
config = load_config()
include = get_value(config, 'release_bundle.include', [])
exclude = get_value(config, 'release_bundle.exclude_patterns', [])
for f in collect_release_files(Path('.'), include, exclude):
    print(f.as_posix())
" > "${FILELIST}"

COUNT=$(wc -l < "${FILELIST}")
[ "${COUNT}" -gt 0 ] || die "release bundle file list is empty; refusing to build an empty bundle"
log "Copying ${COUNT} files into ${OUT_DIR}..."

while IFS= read -r rel; do
  rel="${rel%$'\r'}"  # defense-in-depth: strip a stray CR even if the python-side fix above is bypassed
  mkdir -p "${OUT_DIR}/$(dirname "${rel}")"
  cp "${rel}" "${OUT_DIR}/${rel}"
done < "${FILELIST}"

log "Secret-scanning the assembled bundle before declaring it safe..."
python3 -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
from src.research_bridge.secrets import scan_path
findings = scan_path(Path('${OUT_DIR}'))
if findings:
    for f in findings:
        print(f'  SECRET_FINDING: {f.category} in {f.location}', file=sys.stderr)
    sys.exit(1)
print('secret scan: clean')
" || die "secret scan flagged the release bundle — fix before distributing"

log "Release bundle ready: ${OUT_DIR} (${COUNT} files)"
