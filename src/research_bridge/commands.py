"""CLI command construction for gh / hf / kaggle, isolated so it is unit-testable (Mission 29).

Every shape below was verified against the actually-installed CLI's --help output on this
machine (gh 2.97.0, hf 1.27.0 [huggingface_hub], kaggle 2.2.4) rather than guessed — see
docs/RESEARCH_PLATFORM_BRIDGE.md for the verification log. Re-verify on CLI upgrade.
"""
from __future__ import annotations

SYNTAX_VERIFIED = True  # against gh 2.97.0 / hf 1.27.0 / kaggle 2.2.4 --help output


# --- GitHub CLI ---------------------------------------------------------------------------


def gh_version() -> list[str]:
    return ["gh", "--version"]


def gh_auth_status() -> list[str]:
    return ["gh", "auth", "status"]


def git_remote_v() -> list[str]:
    return ["git", "remote", "-v"]


def git_branch_show_current() -> list[str]:
    return ["git", "branch", "--show-current"]


def git_rev_parse_head() -> list[str]:
    return ["git", "rev-parse", "HEAD"]


# --- Hugging Face CLI (`hf`, not the deprecated `huggingface-cli`) ------------------------


def hf_version() -> list[str]:
    return ["hf", "version"]


def hf_auth_whoami() -> list[str]:
    return ["hf", "auth", "whoami"]


def hf_auth_login(use_token_env: bool = False) -> list[str]:
    """Interactive browser login by default; --token $HF_TOKEN only for automated environments."""
    if use_token_env:
        return ["hf", "auth", "login", "--token", "$HF_TOKEN"]
    return ["hf", "auth", "login"]


def hf_repo_create(repo_id: str, repo_type: str = "dataset", private: bool = True, exist_ok: bool = True) -> list[str]:
    if repo_type not in {"model", "dataset", "space"}:
        raise ValueError(f"unsupported repo_type: {repo_type}")
    cmd = ["hf", "repos", "create", repo_id, "--type", repo_type]
    cmd.append("--private" if private else "--no-private")
    if exist_ok:
        cmd.append("--exist-ok")
    return cmd


def hf_upload(
    repo_id: str,
    local_path: str,
    path_in_repo: str = ".",
    repo_type: str = "dataset",
    commit_message: str | None = None,
) -> list[str]:
    if repo_type not in {"model", "dataset", "space"}:
        raise ValueError(f"unsupported repo_type: {repo_type}")
    cmd = ["hf", "upload", repo_id, local_path, path_in_repo, "--type", repo_type]
    if commit_message:
        cmd += ["--commit-message", commit_message]
    return cmd


def hf_download(
    repo_id: str,
    filenames: list[str] | None = None,
    repo_type: str = "dataset",
    local_dir: str | None = None,
    revision: str | None = None,
) -> list[str]:
    cmd = ["hf", "download", repo_id, *(filenames or [])]
    cmd += ["--type", repo_type]
    if local_dir:
        cmd += ["--local-dir", local_dir]
    if revision:
        cmd += ["--revision", revision]
    return cmd


# --- Kaggle CLI ------------------------------------------------------------------------------


def kaggle_version() -> list[str]:
    return ["kaggle", "--version"]


def kaggle_auth_login(no_launch_browser: bool = False) -> list[str]:
    cmd = ["kaggle", "auth", "login"]
    if no_launch_browser:
        cmd.append("--no-launch-browser")
    return cmd


def kaggle_datasets_create(path: str, public: bool = False) -> list[str]:
    cmd = ["kaggle", "datasets", "create", "-p", path]
    if public:
        cmd.append("-u")  # default is private; -u is opt-in only
    return cmd


def kaggle_datasets_version(path: str, message: str, delete_old_versions: bool = False) -> list[str]:
    cmd = ["kaggle", "datasets", "version", "-p", path, "-m", message]
    if delete_old_versions:
        cmd.append("-d")
    return cmd


def kaggle_kernels_push(path: str) -> list[str]:
    return ["kaggle", "kernels", "push", "-p", path]


def kaggle_kernels_pull(kernel: str, path: str, with_metadata: bool = True) -> list[str]:
    cmd = ["kaggle", "kernels", "pull", kernel, "-p", path]
    if with_metadata:
        cmd.append("-m")
    return cmd
