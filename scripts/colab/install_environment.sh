#!/usr/bin/env bash
# scripts/colab/install_environment.sh — install requirements-colab.txt on the remote session
# and verify the required baseline imports actually succeed (Mission 14). Deep-learning
# dependencies (torch/tensorflow) are intentionally NOT installed here.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cmd colab

SESSION="$(cfg colab.sessions.cpu.name drift-tinyml-cpu)"
REMOTE_WORKSPACE="$(cfg colab.remote_workspace /content/drift_tinyml_enose)"

log "Installing requirements-colab.txt on '${SESSION}'..."
colab --auth=oauth2 exec -s "${SESSION}" -- bash -lc \
  "cd '${REMOTE_WORKSPACE}' && pip install -q -r requirements-colab.txt"

log "Verifying baseline imports..."
colab --auth=oauth2 exec -s "${SESSION}" -- python3 -c "
import numpy, pandas, scipy, sklearn, matplotlib, yaml, joblib
print('BASELINE_IMPORTS_OK', numpy.__version__, pandas.__version__, scipy.__version__, sklearn.__version__)
" || die "Baseline import verification FAILED"
