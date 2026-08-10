#!/usr/bin/env python3
"""scripts/bridge/write_platform_status.py — turn already-captured CLI output into
results/reproducibility/bridge/<platform>_status.json.

Callers pass already-captured, human-readable CLI text (auth status / whoami / config view) —
this script never receives, stores, or prints a credential value itself.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.research_bridge import status  # noqa: E402

OUT_DIR = REPO_ROOT / "results" / "reproducibility" / "bridge"


def _write(name: str, payload: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_github(args: argparse.Namespace) -> int:
    result = status.parse_gh_auth_status(args.auth_status)
    payload = {
        "authenticated": result.authenticated,
        "account": result.account,
        "repository": args.repository,
        "branch": args.branch,
        "commit": args.commit,
        "remote": args.remote,
        "cli_version": args.cli_version.strip(),
        "timestamp": _now(),
    }
    print(f"wrote {_write('github_status.json', payload)}")
    return 0


def cmd_huggingface(args: argparse.Namespace) -> int:
    result = status.parse_hf_whoami(args.whoami)
    payload = {
        "authenticated": result.authenticated,
        "username": result.username,
        # `hf auth whoami` on the currently-installed CLI does not enumerate orgs separately;
        # left empty rather than guessed.
        "organizations": [],
        "cli_version": args.cli_version.strip(),
        "timestamp": _now(),
    }
    print(f"wrote {_write('huggingface_status.json', payload)}")
    return 0


def cmd_kaggle(args: argparse.Namespace) -> int:
    result = status.parse_kaggle_auth_probe(args.auth_probe)
    payload = {
        "authenticated": result.authenticated,
        # Not discoverable from a pre-auth probe; populate after a real `kaggle auth login`.
        "username": None,
        "cli_version": args.cli_version.strip(),
        "timestamp": _now(),
    }
    print(f"wrote {_write('kaggle_status.json', payload)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="write_platform_status.py")
    sub = parser.add_subparsers(dest="platform", required=True)

    p_gh = sub.add_parser("github")
    p_gh.add_argument("--cli-version", required=True)
    p_gh.add_argument("--auth-status", required=True)
    p_gh.add_argument("--repository", required=True)
    p_gh.add_argument("--branch", required=True)
    p_gh.add_argument("--commit", required=True)
    p_gh.add_argument("--remote", required=True)
    p_gh.set_defaults(func=cmd_github)

    p_hf = sub.add_parser("huggingface")
    p_hf.add_argument("--cli-version", required=True)
    p_hf.add_argument("--whoami", required=True)
    p_hf.set_defaults(func=cmd_huggingface)

    p_kg = sub.add_parser("kaggle")
    p_kg.add_argument("--cli-version", required=True)
    p_kg.add_argument("--auth-probe", required=True)
    p_kg.set_defaults(func=cmd_kaggle)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
