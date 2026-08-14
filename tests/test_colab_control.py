"""Unit tests for the Colab CLI control plane (src/colab_control).

Covers only logic that does not require a real Colab allocation (Mission 40): configuration
parsing, run-id creation, manifest schema, artifact paths, environment labels, CLI command
construction, workspace exclusions, and result comparison.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from src.colab_control import commands, comparison, manifest, workspace
from src.colab_control.config import ColabConfigError, get_value, load_config
from src.colab_control.environments import (
    ALLOWED_ENVIRONMENT_LABELS,
    InvalidEnvironmentLabelError,
    validate_environment_label,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_CONFIG_PATH = REPO_ROOT / "configs" / "colab.yaml"


# --- config -------------------------------------------------------------------------------


def test_real_config_loads_and_validates():
    config = load_config(REAL_CONFIG_PATH)
    assert config["colab"]["sessions"]["cpu"]["name"] == "drift-tinyml-cpu"
    assert config["colab"]["dataset_gate"]["samples"] == 13910


def test_get_value_dotted_path():
    config = load_config(REAL_CONFIG_PATH)
    assert get_value(config, "colab.remote_workspace") == "/content/drift_tinyml_enose"
    assert get_value(config, "colab.does.not.exist", "fallback") == "fallback"


@pytest.mark.parametrize(
    "broken",
    [
        {},
        {"output_root": "results", "seed": 42},  # missing colab
        {"output_root": "results", "seed": 42, "colab": {}},  # missing colab subkeys
    ],
)
def test_missing_required_keys_raise(tmp_path, broken):
    path = tmp_path / "colab.yaml"
    path.write_text(yaml.safe_dump(broken), encoding="utf-8")
    with pytest.raises(ColabConfigError):
        load_config(path)


def test_missing_file_raises(tmp_path):
    with pytest.raises(ColabConfigError):
        load_config(tmp_path / "does_not_exist.yaml")


# --- environment labels ---------------------------------------------------------------------


def test_allowed_labels_include_required_set():
    required = {
        "LOCAL_WINDOWS_CPU",
        "LOCAL_WINDOWS_GPU",
        "WSL_LOCAL",
        "COLAB_CPU",
        "COLAB_T4",
        "COLAB_L4",
        "COLAB_G4",
        "COLAB_A100",
        "COLAB_H100",
        "PHYSICAL_NRF52840",
    }
    assert required == ALLOWED_ENVIRONMENT_LABELS


def test_validate_environment_label_accepts_allowed():
    assert validate_environment_label("COLAB_CPU") == "COLAB_CPU"


def test_validate_environment_label_rejects_unknown():
    with pytest.raises(InvalidEnvironmentLabelError):
        validate_environment_label("MCU_LATENCY")
    with pytest.raises(InvalidEnvironmentLabelError):
        validate_environment_label("colab_cpu")  # case-sensitive, no silent normalization


# --- run id ---------------------------------------------------------------------------------


def test_new_run_id_format():
    ts = datetime(2026, 8, 10, 15, 30, 0, tzinfo=timezone.utc)
    run_id = manifest.new_run_id("fixed-origin cpu", timestamp=ts)
    assert run_id == "20260810T153000Z_FIXED_ORIGIN_CPU"
    assert manifest.RUN_ID_RE.match(run_id)


def test_new_run_id_rejects_empty_descriptor():
    with pytest.raises(ValueError):
        manifest.new_run_id("***", timestamp=datetime.now(timezone.utc))


# --- run manifest schema ---------------------------------------------------------------------


def _valid_pre_fields(run_id: str = "20260810T153000Z_SMOKE_TEST_CPU") -> dict:
    return dict(
        run_id=run_id,
        git_sha="deadbeef",
        branch="codex/colab-research-system",
        dataset_archive_sha256="91e8f466f202e7a093d657673ce47311c3e90416f7df3057966058961c351fe4",
        dataset_manifest_sha256="abc123",
        config_sha256="def456",
        environment="COLAB_CPU",
        colab_cli_version="0.0.0",
        session_name="drift-tinyml-cpu",
        requested_accelerator="none",
        actual_accelerator="none",
        python_version="3.11.0",
        package_versions={"numpy": "1.26.0"},
        start_timestamp="2026-08-10T15:30:00Z",
        status="RUNNING",
    )


def test_build_run_manifest_success():
    m = manifest.build_run_manifest(**_valid_pre_fields())
    assert m["environment"] == "COLAB_CPU"
    assert manifest.validate_run_manifest(m) == []


def test_build_run_manifest_missing_field_raises():
    fields = _valid_pre_fields()
    del fields["git_sha"]
    with pytest.raises(ValueError):
        manifest.build_run_manifest(**fields)


def test_build_run_manifest_invalid_environment_raises():
    fields = _valid_pre_fields()
    fields["environment"] = "MCU_LATENCY"
    with pytest.raises(InvalidEnvironmentLabelError):
        manifest.build_run_manifest(**fields)


def test_complete_run_manifest_requires_post_fields():
    m = manifest.build_run_manifest(**_valid_pre_fields())
    with pytest.raises(ValueError):
        manifest.complete_run_manifest(m)  # missing end_timestamp etc.
    completed = manifest.complete_run_manifest(
        m,
        end_timestamp="2026-08-10T16:00:00Z",
        notebooks_executed=["00_environment_and_reproducibility.ipynb"],
        result_paths=["runs/20260810T153000Z_SMOKE_TEST_CPU/metrics"],
    )
    assert manifest.validate_run_manifest(completed, require_complete=True) == []


def test_validate_run_manifest_reports_missing_without_raising():
    errors = manifest.validate_run_manifest({"run_id": "bad-format"})
    assert errors  # non-empty, and did not raise
    assert any("run_id" in e for e in errors)


# --- dataset gate -----------------------------------------------------------------------------


def _write_fake_executed_notebook(path: Path, body_text: str) -> None:
    nb = {
        "cells": [
            {
                "cell_type": "code",
                "outputs": [{"output_type": "stream", "text": [body_text]}],
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(nb), encoding="utf-8")


def test_check_dataset_gate_passes_on_matching_values(tmp_path):
    body = (
        "samples: 13910\nfeatures: 128\nbatches: 10\nclasses: 6\n"
        "archive sha256: 91e8f466f202e7a093d657673ce47311c3e90416f7df3057966058961c351fe4\n"
    )
    nb_path = tmp_path / "01_dataset_audit.ipynb"
    _write_fake_executed_notebook(nb_path, body)
    passed, details = manifest.check_dataset_gate(nb_path, REAL_CONFIG_PATH)
    assert passed is True
    assert details["sha256_match"] is True


def test_check_dataset_gate_fails_on_wrong_sha(tmp_path):
    body = "samples: 13910\nfeatures: 128\nbatches: 10\nclasses: 6\narchive sha256: " + "0" * 64
    nb_path = tmp_path / "01_dataset_audit.ipynb"
    _write_fake_executed_notebook(nb_path, body)
    passed, details = manifest.check_dataset_gate(nb_path, REAL_CONFIG_PATH)
    assert passed is False
    assert details["sha256_match"] is False


def test_check_dataset_gate_fails_on_wrong_dimensions(tmp_path):
    body = (
        "samples: 9999\nfeatures: 128\nbatches: 10\nclasses: 6\n"
        "archive sha256: 91e8f466f202e7a093d657673ce47311c3e90416f7df3057966058961c351fe4\n"
    )
    nb_path = tmp_path / "01_dataset_audit.ipynb"
    _write_fake_executed_notebook(nb_path, body)
    passed, details = manifest.check_dataset_gate(nb_path, REAL_CONFIG_PATH)
    assert passed is False
    assert details["samples"]["found_in_text"] is False


# --- workspace include/exclude ----------------------------------------------------------------


def test_collect_workspace_files_respects_excludes(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "keep.py").write_text("x = 1", encoding="utf-8")
    (tmp_path / "src" / "__pycache__").mkdir()
    (tmp_path / "src" / "__pycache__" / "keep.cpython-311.pyc").write_text("bin", encoding="utf-8")
    (tmp_path / "secrets.key").write_text("nope", encoding="utf-8")
    (tmp_path / "README.md").write_text("# readme", encoding="utf-8")

    files = workspace.collect_workspace_files(
        tmp_path,
        include=["src", "README.md", "secrets.key"],
        exclude_patterns=["*.key"],
    )
    rel_strs = {f.as_posix() for f in files}
    assert "src/keep.py" in rel_strs
    assert "README.md" in rel_strs
    assert not any("__pycache__" in s for s in rel_strs)
    assert "secrets.key" not in rel_strs


def test_collect_workspace_files_skips_missing_optional_entries(tmp_path):
    files = workspace.collect_workspace_files(tmp_path, include=["does_not_exist"], exclude_patterns=[])
    assert files == []


def test_real_config_workspace_excludes_credentials_and_caches():
    config = load_config(REAL_CONFIG_PATH)
    exclude = get_value(config, "colab.workspace_exclude_patterns", [])
    assert "*.key" in exclude
    assert "*.pem" in exclude
    assert ".env" in exclude


# --- CLI command construction -------------------------------------------------------------------


def test_colab_new_session_cpu():
    assert commands.colab_new_session("drift-tinyml-cpu") == [
        "colab",
        "--auth=oauth2",
        "new",
        "-s",
        "drift-tinyml-cpu",
    ]


def test_colab_new_session_gpu_profile():
    cmd = commands.colab_new_session("drift-tinyml-gpu", gpu="T4")
    assert cmd == ["colab", "--auth=oauth2", "new", "-s", "drift-tinyml-gpu", "--gpu", "T4"]


def test_colab_stop_and_sessions():
    assert commands.colab_stop("drift-tinyml-cpu") == ["colab", "--auth=oauth2", "stop", "-s", "drift-tinyml-cpu"]
    assert commands.colab_sessions() == ["colab", "--auth=oauth2", "sessions"]


def test_colab_exec_wraps_inner_command():
    cmd = commands.colab_exec("drift-tinyml-cpu", ["python3", "-c", "print(1)"])
    assert cmd == [
        "colab",
        "--auth=oauth2",
        "exec",
        "-s",
        "drift-tinyml-cpu",
        "--",
        "python3",
        "-c",
        "print(1)",
    ]


# --- local vs colab comparison -----------------------------------------------------------------


def test_compare_metrics_match():
    local = [{"model": "svm", "batch": 2, "metric": "accuracy", "value": 0.9}]
    colab = [{"model": "svm", "batch": 2, "metric": "accuracy", "value": 0.9}]
    rows = comparison.compare_metrics(local, colab)
    assert rows[0]["status"] == "MATCH"
    assert rows[0]["colab_value"] == 0.9


def test_compare_metrics_mismatch():
    local = [{"model": "svm", "batch": 2, "metric": "accuracy", "value": 0.9}]
    colab = [{"model": "svm", "batch": 2, "metric": "accuracy", "value": 0.5}]
    rows = comparison.compare_metrics(local, colab, tolerance=1e-6)
    assert rows[0]["status"] == "MISMATCH"


def test_compare_metrics_missing_colab_value_is_not_backfilled():
    local = [{"model": "svm", "batch": 2, "metric": "accuracy", "value": 0.9}]
    rows = comparison.compare_metrics(local, colab_rows=[])
    assert rows[0]["status"] == "MISSING_COLAB_VALUE"
    assert rows[0]["colab_value"] is None
