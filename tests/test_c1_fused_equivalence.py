from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/embedded"
GEN = ROOT / "embedded/generated/c1_fused"


def test_c1_fused_required_artifacts_and_history():
    required = ["c1_fused_exp_input_manifest.csv", "c1_fused_parameter_derivation.csv",
                "c1_fused_raw_cast_analysis.csv", "c1_fused_golden_equivalence.csv",
                "c1_fused_boundary_equivalence.csv", "c1_fused_error_summary.csv",
                "c1_fused_class_batch_summary.csv", "c1_fused_operation_validation.csv",
                "c1_fused_storage_validation.csv", "c1_fused_claim_evaluation.csv",
                "c1_fused_manifest.csv", "c1_fused_build_environment.json"]
    assert all((OUT / name).is_file() for name in required)
    assert pd.read_csv(OUT / "stage14r_candidate_summary.csv").mandatory_pass.eq(False).all()
    assert (GEN / "model_c1_fused.c").is_file()


def test_c1_fused_universal_criteria():
    g = pd.read_csv(OUT / "c1_fused_golden_equivalence.csv")
    b = pd.read_csv(OUT / "c1_fused_boundary_equivalence.csv")
    assert g.filter(regex="^score_absolute_error_").to_numpy().max() <= 2e-3
    assert g.filter(regex="^probability_absolute_error_").to_numpy().max() <= 1e-3
    assert g.probability_vector_L1.max() <= 4e-3
    assert max(g.normalization_error.max(), b.normalization_error.max()) <= 2e-6
    assert g.prediction_agreement.all() and b.prediction_agreement.all()


def test_c1_fused_source_obeys_fp_policy_and_scope():
    source = "\n".join((GEN / name).read_text() for name in ["model_c1_fused.c", "inference_c1_fused.c", "test_harness_c1_fused.c"])
    assert "double" not in source
    assert "scale" not in (GEN / "inference_c1_fused.c").read_text().lower()
    assert "int8" not in source.lower() and "quant" not in source.lower()
    assert "attribution" not in source.lower() and "contribution" not in source.lower()
    env = (OUT / "c1_fused_build_environment.json").read_text()
    assert "-fno-fast-math" in env and "-ffp-contract=off" in env


def test_c1_fused_lineage_is_complete():
    manifest = pd.read_csv(OUT / "c1_fused_manifest.csv")
    assert manifest.sha256.str.fullmatch(r"[0-9a-f]{64}").all()
    assert manifest.result.eq("PASSED").all()
    claims = pd.read_csv(OUT / "c1_fused_claim_evaluation.csv").set_index("claim_id")
    assert claims.loc["C-EMBED-C1-FUSED-01", "status"] == "SUPPORTED"
    assert claims.loc["C-EMBED-C1-FUSED-02", "status"] == "SUPPORTED"
    assert claims.loc["C-EMBED-C1-FUSED-XAI-01", "status"] == "NOT_EXECUTED"
