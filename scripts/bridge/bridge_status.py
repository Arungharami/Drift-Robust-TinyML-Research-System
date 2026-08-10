#!/usr/bin/env python3
"""scripts/bridge/bridge_status.py — one-command summary of GitHub / Hugging Face / Kaggle /
Colab / Drive status (Mission 18). Statuses are READY / BLOCKED / NOT_CONFIGURED / NOT_EXECUTED
/ FAILED only. Never prints a credential.

Usage: python scripts/bridge/bridge_status.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.research_bridge import status  # noqa: E402


def _run(cmd: list[str], timeout: int = 20) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, (proc.stdout + proc.stderr)
    except FileNotFoundError:
        return 127, ""
    except subprocess.TimeoutExpired:
        return 124, ""


def github_status() -> str:
    if shutil.which("gh") is None:
        return status.NOT_CONFIGURED
    _, text = _run(["gh", "auth", "status"])
    result = status.parse_gh_auth_status(text)
    return status.platform_status(True, result.authenticated)


def huggingface_status() -> str:
    if shutil.which("hf") is None:
        return status.NOT_CONFIGURED
    _, text = _run(["hf", "auth", "whoami"])
    result = status.parse_hf_whoami(text)
    return status.platform_status(True, result.authenticated)


def kaggle_status() -> str:
    if shutil.which("kaggle") is None:
        return status.NOT_CONFIGURED
    _, text = _run(["kaggle", "config", "view"])
    result = status.parse_kaggle_auth_probe(text)
    return status.platform_status(True, result.authenticated)


def colab_status() -> str:
    wsl_bin = shutil.which("wsl.exe") or shutil.which("wsl")
    if wsl_bin is None:
        return status.NOT_CONFIGURED
    rc, text = _run([wsl_bin, "--status"])
    lowered = text.lower()
    if rc != 0 or "not installed" in lowered or "virtualization is not enabled" in lowered:
        return status.BLOCKED
    rc2, text2 = _run([wsl_bin, "-l", "-v"])
    if rc2 != 0 or "no installed distributions" in text2.lower():
        return status.BLOCKED
    # WSL2 + a distribution are usable, but the Colab CLI itself hasn't been verified from here.
    return status.NOT_EXECUTED


def drive_status() -> str:
    # Drive is only mountable from inside an active Colab session; no session exists here.
    return status.NOT_EXECUTED


def main() -> int:
    rows = {
        "GitHub": github_status(),
        "Hugging Face": huggingface_status(),
        "Kaggle": kaggle_status(),
        "Colab": colab_status(),
        "Drive": drive_status(),
    }
    width = max(len(k) for k in rows)
    for platform, s in rows.items():
        print(f"{platform.ljust(width)} : {s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
