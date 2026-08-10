#!/usr/bin/env bash
# scripts/colab/run_core_repro.sh — real-Colab 00 -> 01 (hard dataset gate) -> 02 orchestration
# (Missions 18-22). Stops before Notebook 02 if the Notebook-01 dataset gate fails.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
trap 'log "run_core_repro.sh exiting with status $?"' EXIT

RUN_ID="$(python3 -m src.colab_control.manifest new-run-id --descriptor FIXED_ORIGIN_CPU)"
log "RUN_ID=${RUN_ID}"

"${COLAB_LIB_DIR}/run_notebook.sh" notebooks/00_environment_and_reproducibility.ipynb "${RUN_ID}"
log "Notebook 00 COMPLETED for ${RUN_ID}."

"${COLAB_LIB_DIR}/run_notebook.sh" notebooks/01_dataset_audit_and_drift_characterization.ipynb "${RUN_ID}"

log "Checking Notebook-01 dataset gate..."
if ! python3 -m src.colab_control.manifest check-dataset-gate \
    --notebook "${REPO_ROOT}/runs/${RUN_ID}/executed_notebooks/01_dataset_audit_and_drift_characterization.ipynb" \
    --config "${CONFIG_PATH}"; then
  log "COLAB_DATASET_GATE = FAILED. Stopping before Notebook 02."
  exit 3
fi
log "COLAB_DATASET_GATE = PASSED."

"${COLAB_LIB_DIR}/run_notebook.sh" notebooks/02_classical_chronological_baselines.ipynb "${RUN_ID}"
log "Notebook 02 COMPLETED for ${RUN_ID}."

log "Core reproduction sequence finished for RUN_ID=${RUN_ID}."
log "Evaluate COLAB_CORE_REPRO_GATE against results/reproducibility/COLAB_STATUS.md criteria before declaring PASSED."
