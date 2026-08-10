#!/usr/bin/env bash
# scripts/colab/run_checkpoint2.sh — Checkpoint-2 orchestration: runtime verify -> workspace
# verify -> dataset gate -> fixed-origin baselines -> expanding-window evaluation -> IID
# diagnostic -> metrics/figures -> artifact collection (Mission 23). Deep learning is
# intentionally NOT included here.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
trap 'log "run_checkpoint2.sh exiting with status $?"' EXIT

RUN_ID="$(python3 -m src.colab_control.manifest new-run-id --descriptor CHECKPOINT2_CPU)"
log "RUN_ID=${RUN_ID}"

"${COLAB_LIB_DIR}/status.sh"
"${COLAB_LIB_DIR}/run_notebook.sh" notebooks/00_environment_and_reproducibility.ipynb "${RUN_ID}"
"${COLAB_LIB_DIR}/run_notebook.sh" notebooks/01_dataset_audit_and_drift_characterization.ipynb "${RUN_ID}"

if ! python3 -m src.colab_control.manifest check-dataset-gate \
    --notebook "${REPO_ROOT}/runs/${RUN_ID}/executed_notebooks/01_dataset_audit_and_drift_characterization.ipynb" \
    --config "${CONFIG_PATH}"; then
  log "COLAB_DATASET_GATE = FAILED. Aborting Checkpoint 2 before any baselines run."
  exit 3
fi

"${COLAB_LIB_DIR}/run_notebook.sh" notebooks/02_classical_chronological_baselines.ipynb "${RUN_ID}"
"${COLAB_LIB_DIR}/run_notebook.sh" notebooks/03_temporal_adaptation_and_iid_diagnostic.ipynb "${RUN_ID}"

"${COLAB_LIB_DIR}/download_results.sh" "${RUN_ID}"
"${COLAB_LIB_DIR}/export_logs.sh" "${RUN_ID}"

log "Checkpoint 2 orchestration finished for RUN_ID=${RUN_ID}."
