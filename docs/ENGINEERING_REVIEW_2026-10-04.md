# Engineering review — October 4, 2026

## Scope

Source review of `src/drift/metrics.py`, `tests/test_drift_metrics.py`, `configs/pipeline_stages.yaml`, `paper/claim_evidence_matrix.csv`, and the root README. This review addresses a bounded correctness issue; it does not certify the entire application, rerun all research experiments, or establish production readiness.

## Finding and repair

The drift functions accepted singleton/non-finite arrays and could emit NaN. The README described fidelity, stability and host export work as unexecuted even though the stage registry records later executed experiments.

Validate finite one-dimensional samples with at least two observations and a positive finite epsilon. Align README language with the registry, including failed original export, passed fused host experiments, and blocked physical hardware work.

## Verification

`python -m unittest discover -s tests -p test_drift_input_contract.py -v` — 3 tests passed.

All changed Python files were syntax-compiled. Package installation from this workspace is blocked, so full dependency-backed suites and production builds are not described as passed. GitHub checks on the pull request provide the remaining integration validation.

## Next implementation work

Execute the frozen weights-only INT8 experiment against the exact accepted C1 artifacts and protocol, then independently validate its output. Physical nRF52840/PPK2 measurements require the actual device, probe, and toolchain. Do not bypass the blocked hardware gate.

## Evidence boundary

No raw benchmark data, measured research results, corpus approval records, model releases or production deployments were changed. Any affected scientific output must be re-executed and linked to the accepted source commit before updating manuscript claims.
