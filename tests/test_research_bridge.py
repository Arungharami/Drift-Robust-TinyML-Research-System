"""Unit tests for the multi-platform research bridge (src/research_bridge).

Covers only logic that does not require live tokens or network access (Mission 29): bridge
config, manifest schema, artifact SHA calculation, safe release-bundle resolution, secret
exclusions, HF/Kaggle command construction, platform status parsing, cross-platform hash
comparison.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from src.research_bridge import commands, hashing, manifest, release_bundle, secrets, status
from src.research_bridge.config import BridgeConfigError, get_value, load_config

REPO_ROOT = Path(__file__).resolve().parents[1]
REAL_CONFIG_PATH = REPO_ROOT / "configs" / "research_bridge.yaml"


# --- config -------------------------------------------------------------------------------


def test_real_config_loads_and_validates():
    config = load_config(REAL_CONFIG_PATH)
    assert config["github"]["canonical"] is True
    assert config["huggingface"]["private_by_default"] is True
    assert config["kaggle"]["private_by_default"] is True


def test_get_value_dotted_path():
    config = load_config(REAL_CONFIG_PATH)
    assert get_value(config, "huggingface.dataset_repo") == "drift-robust-tinyml-research-data"
    assert get_value(config, "does.not.exist", "fallback") == "fallback"


def test_github_must_be_canonical(tmp_path):
    broken = {
        "github": {"canonical": False, "repository": "x/y"},
        "colab": {},
        "huggingface": {"private_by_default": True},
        "kaggle": {"private_by_default": True},
        "drive": {},
    }
    path = tmp_path / "research_bridge.yaml"
    path.write_text(yaml.safe_dump(broken), encoding="utf-8")
    with pytest.raises(BridgeConfigError, match="canonical"):
        load_config(path)


@pytest.mark.parametrize("platform", ["huggingface", "kaggle"])
def test_platforms_must_default_private(tmp_path, platform):
    config = {
        "github": {"canonical": True, "repository": "x/y"},
        "colab": {},
        "huggingface": {"private_by_default": True},
        "kaggle": {"private_by_default": True},
        "drive": {},
    }
    config[platform]["private_by_default"] = False
    path = tmp_path / "research_bridge.yaml"
    path.write_text(yaml.safe_dump(config), encoding="utf-8")
    with pytest.raises(BridgeConfigError, match="private_by_default"):
        load_config(path)


def test_missing_file_raises(tmp_path):
    with pytest.raises(BridgeConfigError):
        load_config(tmp_path / "does_not_exist.yaml")


# --- manifest schema ------------------------------------------------------------------------


def _full_manifest(**overrides) -> dict:
    fields = dict(
        project="drift-robust-tinyml",
        git_repository="Arungharami/Drift-Robust-TinyML-Research-System",
        git_branch="codex/colab-research-system",
        git_sha="16f3987c452a064c8f7b3acd1238b2e1e918c95d",
        dataset=manifest.dataset_block(
            source="UCI Gas Sensor Array Drift",
            archive_sha256="91e8f466f202e7a093d657673ce47311c3e90416f7df3057966058961c351fe4",
        ),
        experiment=manifest.experiment_block(),
        github=manifest.github_block(commit="16f3987"),
        colab=manifest.colab_block(),
        huggingface=manifest.huggingface_block(),
        kaggle=manifest.kaggle_block(),
        created_at="2026-08-10T00:00:00Z",
        status="DRAFT",
    )
    fields.update(overrides)
    return fields


def test_build_platform_manifest_success():
    m = manifest.build_platform_manifest(**_full_manifest())
    assert manifest.validate_platform_manifest(m) == []


def test_build_platform_manifest_missing_field_raises():
    fields = _full_manifest()
    del fields["git_sha"]
    with pytest.raises(ValueError):
        manifest.build_platform_manifest(**fields)


def test_validate_platform_manifest_reports_missing_nested_field():
    m = manifest.build_platform_manifest(**_full_manifest())
    del m["colab"]["status"]
    errors = manifest.validate_platform_manifest(m)
    assert any("colab.status" in e for e in errors)


def test_placeholder_statuses_are_the_only_unknown_markers():
    block = manifest.colab_block()
    assert block["run_id"] == manifest.NOT_EXECUTED
    assert block["run_id"] in manifest.PLACEHOLDER_STATUSES
    hf_block = manifest.huggingface_block()
    assert hf_block["dataset_repo"] == manifest.NOT_CREATED


# --- hashing --------------------------------------------------------------------------------


def test_sha256_file_matches_hashlib(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_bytes(b"drift-robust-tinyml research bridge")
    expected = hashlib.sha256(b"drift-robust-tinyml research bridge").hexdigest()
    assert hashing.sha256_file(f) == expected


def test_compare_hashes_match_and_mismatch():
    assert hashing.compare_hashes("abc123", "ABC123") == "MATCH"  # case-insensitive
    assert hashing.compare_hashes("abc123", "def456") == "MISMATCH"


def test_compare_hashes_empty_is_mismatch_not_silent_pass():
    assert hashing.compare_hashes("", "") == "MISMATCH"
    assert hashing.compare_hashes("abc123", "") == "MISMATCH"


def test_build_artifact_index_row_has_all_columns():
    row = hashing.build_artifact_index_row(
        artifact_id="metrics-01",
        experiment_id="EXP-001",
        local_path="results/reproducibility/metrics.json",
        sha256="a" * 64,
        size_bytes=1024,
        git_sha="16f3987",
        platform="huggingface",
        remote_identifier="user/drift-robust-tinyml-research-data",
        remote_revision="main",
        upload_timestamp="2026-08-10T00:00:00Z",
    )
    assert set(row) == set(hashing.ARTIFACT_INDEX_COLUMNS)
    assert row["verification_status"] == "NOT_EXECUTED"


# --- secret scanning --------------------------------------------------------------------------


def test_scan_text_detects_github_token():
    findings = secrets.scan_text("export GH_TOKEN=ghp_" + "a" * 36)
    assert any(f.category == "github_token" for f in findings)


def test_scan_text_detects_hf_token():
    findings = secrets.scan_text("HF_TOKEN=hf_" + "b" * 34)
    assert any(f.category in {"huggingface_token", "hf_token_assignment"} for f in findings)


def test_scan_text_ignores_shell_reference_and_placeholder():
    findings = secrets.scan_text("HF_TOKEN=$HF_TOKEN\nKAGGLE_API_TOKEN=changeme\nGH_TOKEN=")
    assert findings == []


def test_scan_text_ignores_mere_mention_in_docs():
    findings = secrets.scan_text("Set the HF_TOKEN environment variable before running this script.")
    assert findings == []


def test_is_denylisted_filename():
    assert secrets.is_denylisted_filename(Path("kaggle.json"))
    assert secrets.is_denylisted_filename(Path("secrets/id_rsa"))
    assert secrets.is_denylisted_filename(Path("service.pem"))
    assert not secrets.is_denylisted_filename(Path("README.md"))


def test_scan_path_finds_denylisted_file_and_embedded_token(tmp_path):
    (tmp_path / "kaggle.json").write_text('{"username":"x","key":"y"}', encoding="utf-8")
    (tmp_path / "notes.txt").write_text("GH_TOKEN=ghp_" + "c" * 36, encoding="utf-8")
    (tmp_path / "clean.txt").write_text("nothing secret here", encoding="utf-8")
    findings = secrets.scan_path(tmp_path)
    locations = {f.location for f in findings}
    assert "kaggle.json" in locations
    assert "notes.txt" in locations
    assert "clean.txt" not in locations


# --- release bundle resolution -----------------------------------------------------------------


def test_collect_release_files_excludes_secrets_even_if_included(tmp_path):
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "keep.yaml").write_text("a: 1", encoding="utf-8")
    (tmp_path / "kaggle.json").write_text("{}", encoding="utf-8")
    (tmp_path / "secret.pem").write_text("nope", encoding="utf-8")

    files = release_bundle.collect_release_files(
        tmp_path, include=["configs", "kaggle.json", "secret.pem"], exclude_patterns=[]
    )
    rel_strs = {f.as_posix() for f in files}
    assert "configs/keep.yaml" in rel_strs
    assert "kaggle.json" not in rel_strs
    assert "secret.pem" not in rel_strs


def test_real_config_release_bundle_excludes_raw_data():
    config = load_config(REAL_CONFIG_PATH)
    exclude = get_value(config, "release_bundle.exclude_patterns", [])
    assert "data/raw/*" in exclude
    assert "kaggle.json" in exclude


# --- command construction -----------------------------------------------------------------------


def test_gh_commands():
    assert commands.gh_auth_status() == ["gh", "auth", "status"]
    assert commands.git_rev_parse_head() == ["git", "rev-parse", "HEAD"]


def test_hf_repo_create_private_by_default():
    cmd = commands.hf_repo_create("user/drift-robust-tinyml-research-data", repo_type="dataset")
    assert cmd == [
        "hf",
        "repos",
        "create",
        "user/drift-robust-tinyml-research-data",
        "--type",
        "dataset",
        "--private",
        "--exist-ok",
    ]


def test_hf_repo_create_rejects_bad_type():
    with pytest.raises(ValueError):
        commands.hf_repo_create("user/x", repo_type="bogus")


def test_hf_upload_shape():
    cmd = commands.hf_upload("user/repo", "dist/research_bridge", ".", repo_type="dataset", commit_message="evidence")
    assert cmd[:5] == ["hf", "upload", "user/repo", "dist/research_bridge", "."]
    assert "--commit-message" in cmd
    assert "evidence" in cmd


def test_kaggle_datasets_create_private_unless_public_requested():
    assert commands.kaggle_datasets_create("platforms/kaggle/dataset") == [
        "kaggle",
        "datasets",
        "create",
        "-p",
        "platforms/kaggle/dataset",
    ]
    assert "-u" in commands.kaggle_datasets_create("platforms/kaggle/dataset", public=True)


def test_kaggle_kernels_push_and_pull():
    assert commands.kaggle_kernels_push("platforms/kaggle/kernel") == [
        "kaggle",
        "kernels",
        "push",
        "-p",
        "platforms/kaggle/kernel",
    ]
    cmd = commands.kaggle_kernels_pull("user/drift-robust-tinyml-reproduction", "runs/output")
    assert cmd == ["kaggle", "kernels", "pull", "user/drift-robust-tinyml-reproduction", "-p", "runs/output", "-m"]


# --- platform status parsing --------------------------------------------------------------------


def test_parse_gh_auth_status_authenticated():
    text = (
        "github.com\n"
        "  ✓ Logged in to github.com account Arungharami (keyring)\n"
        "  - Active account: true\n"
    )
    result = status.parse_gh_auth_status(text)
    assert result.authenticated is True
    assert result.account == "Arungharami"


def test_parse_hf_whoami_not_logged_in():
    result = status.parse_hf_whoami("Error: Not logged in")
    assert result.authenticated is False
    assert result.username is None


def test_parse_hf_whoami_logged_in():
    result = status.parse_hf_whoami("some-user\n")
    assert result.authenticated is True
    assert result.username == "some-user"


def test_parse_kaggle_auth_probe():
    assert status.parse_kaggle_auth_probe("Authentication required to call the Kaggle API.").authenticated is False
    assert status.parse_kaggle_auth_probe('{"username": "someone"}').authenticated is True


@pytest.mark.parametrize(
    "cli_installed,authenticated,expected",
    [
        (False, None, status.NOT_CONFIGURED),
        (True, None, status.NOT_EXECUTED),
        (True, False, status.BLOCKED),
        (True, True, status.READY),
    ],
)
def test_platform_status_matrix(cli_installed, authenticated, expected):
    assert status.platform_status(cli_installed, authenticated) == expected


def test_all_status_constants_are_valid():
    for value in (status.READY, status.BLOCKED, status.NOT_CONFIGURED, status.NOT_EXECUTED, status.FAILED):
        assert value in status.VALID_STATUSES
