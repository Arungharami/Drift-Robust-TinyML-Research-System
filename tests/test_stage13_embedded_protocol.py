from __future__ import annotations

import hashlib, json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/embedded"


def test_gate_states_and_hard_stop() -> None:
    decision = pd.read_csv(OUT / "stage13_decision.csv").iloc[0]
    assert decision.stage13_protocol_status == "FROZEN"
    for field in ["model_export_status", "quantization_status", "firmware_status", "mcu_measurement_status", "energy_status"]:
        assert decision[field] == "NOT_EXECUTED"
    pipeline = yaml.safe_load((ROOT / "configs/pipeline_stages.yaml").read_text(encoding="utf-8"))["stages"]
    assert next(s for s in pipeline if s["id"] == "13")["status"] == "PROTOCOL_FROZEN"
    assert next(s for s in pipeline if s["id"] == "14")["status"] in {"NOT_EXECUTED", "FAILED", "EXECUTED"}


def test_exact_model_inventory_complete() -> None:
    inv = pd.read_csv(OUT / "stage13_model_inventory.csv")
    assert dict(zip(inv.model_id, inv.python_estimator_class)) == {"MODEL-C1":"LogisticRegression", "MODEL-C2":"RandomForestClassifier", "MODEL-C3":"SVC", "MODEL-C4":"MLPClassifier"}
    assert inv.python_estimator_class.notna().all()
    assert (inv.number_of_input_features == 128).all()
    assert (inv.number_of_classes == 6).all()
    assert (inv.source_sha256.str.len() == 64).all()


def test_feature_order_and_scaler_constants_match_frozen_pipelines() -> None:
    prep = pd.read_csv(OUT / "stage13_preprocessing_inventory.csv")
    fmap = pd.read_csv(ROOT / "results/xai/stage09_feature_map.csv").sort_values("feature_index")
    expected_order = fmap.original_name.astype(str).tolist()
    expected_hash = hashlib.sha256("\n".join(expected_order).encode()).hexdigest()
    for row in prep.itertuples():
        assert json.loads(row.feature_order) == expected_order
        assert row.feature_order_sha256 == expected_hash
        pipe = joblib.load(ROOT / f"artifacts/models/BASE-FIXED-{row.model_id.replace('MODEL-', '')}-001.joblib")
        scaler = pipe.named_steps["scaler"]
        constants = np.concatenate([scaler.mean_, scaler.scale_, scaler.var_])
        assert hashlib.sha256(constants.astype("<f8").tobytes()).hexdigest() == row.constants_sha256


def test_golden_and_boundary_vectors_have_reference_outputs() -> None:
    golden = pd.read_csv(ROOT / "data/manifests/embedded_golden_vectors.csv")
    boundary = pd.read_csv(ROOT / "data/manifests/embedded_boundary_vectors.csv")
    assert len(golden) >= 72 and len(boundary) == 24
    assert set(golden.batch) == {2, 6, 10} and set(golden.true_label) == {1, 2, 3, 4, 5, 6}
    assert golden.correct_prediction.astype(str).str.lower().isin(["true", "false"]).all()
    assert golden.predicted_label.notna().all() and golden.decision_scores.notna().all() and golden.probabilities.notna().all()
    assert len([c for c in golden if c.startswith("raw_feature_")]) == 128
    assert len([c for c in golden if c.startswith("transformed_feature_")]) == 128
    assert (golden.source_sample_sha256.str.len() == 64).all()


def test_golden_preprocessing_regenerates_exactly() -> None:
    golden = pd.read_csv(ROOT / "data/manifests/embedded_golden_vectors.csv")
    raw_cols = [f"raw_feature_{i:03d}" for i in range(128)]; transformed_cols = [f"transformed_feature_{i:03d}" for i in range(128)]
    for model_id, rows in golden.groupby("model_id"):
        pipe = joblib.load(ROOT / f"artifacts/models/BASE-FIXED-{model_id.replace('MODEL-', '')}-001.joblib")
        regenerated = pipe.named_steps["scaler"].transform(rows[raw_cols].to_numpy())
        assert np.allclose(regenerated, rows[transformed_cols].to_numpy(), rtol=0, atol=1e-12)
        assert np.array_equal(pipe.predict(rows[raw_cols].to_numpy()), rows.predicted_label.to_numpy())


def test_equivalence_tolerances_and_candidate_compatibility_present() -> None:
    protocol = yaml.safe_load((ROOT / "configs/embedded_equivalence_protocol.yaml").read_text(encoding="utf-8"))
    assert protocol["levels"]["level_1_preprocessing"]["fp32_max_absolute_error"] > 0
    assert set(protocol["levels"]["level_2_model_numerical"]["fp32"]) == {"MODEL-C1", "MODEL-C2", "MODEL-C3", "MODEL-C4"}
    assert protocol["levels"]["level_3_decision"]["fp32_boundary_vector_class_agreement"] == 1.0
    paths = pd.read_csv(OUT / "stage13_export_path_matrix.csv")
    assert paths[["model_id", "export_path", "model_type_supported", "selection_status", "reason"]].notna().all().all()
    assert not paths.selection_status.eq("EXECUTED").any()


def test_analytical_storage_never_claims_measured_hardware() -> None:
    memory = pd.read_csv(OUT / "stage13_analytical_memory.csv")
    assert set(memory.measurement_type) == {"DERIVED_ANALYTICAL"}
    assert set(memory.compiled_flash) == {"NOT_MEASURED"}
    assert set(memory.compiled_sram) == {"NOT_MEASURED"}
    budget = yaml.safe_load((ROOT / "configs/nrf52840_resource_budget.yaml").read_text(encoding="utf-8"))
    assert budget["compiled_flash"] == "NOT_MEASURED" and budget["compiled_sram"] == "NOT_MEASURED"


def test_stage09_to_12_lineage_is_verified() -> None:
    manifest = pd.read_csv(OUT / "stage13_input_manifest.csv")
    assert manifest.verification_status.eq("VERIFIED").all()
    for row in manifest.itertuples():
        assert hashlib.sha256((ROOT / row.path).read_bytes()).hexdigest() == row.sha256
    assert all(any(manifest.path.str.contains(f"stage{stage:02d}")) for stage in [9, 10, 11, 12])
