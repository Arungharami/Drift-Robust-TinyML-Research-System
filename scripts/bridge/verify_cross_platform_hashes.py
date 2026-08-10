#!/usr/bin/env python3
"""scripts/bridge/verify_cross_platform_hashes.py — compare a local artifact's SHA-256 against
a freshly-downloaded remote copy (Mission 16). A successful upload is never trusted alone;
appends one row to results/reproducibility/bridge/artifact_index.csv either way.

Usage:
  verify_cross_platform_hashes.py <local_path> <downloaded_remote_path> \
      --platform huggingface|kaggle --remote-identifier <repo/dataset id> \
      --remote-revision <rev> [--experiment-id ID]
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.research_bridge.hashing import (  # noqa: E402
    ARTIFACT_INDEX_COLUMNS,
    build_artifact_index_row,
    compare_hashes,
    sha256_file,
)

INDEX_PATH = REPO_ROOT / "results" / "reproducibility" / "bridge" / "artifact_index.csv"


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def append_row(row: dict) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    is_new = not INDEX_PATH.exists()
    with INDEX_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(ARTIFACT_INDEX_COLUMNS))
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("local_path", type=Path)
    parser.add_argument("remote_downloaded_path", type=Path)
    parser.add_argument("--platform", required=True, choices=["huggingface", "kaggle"])
    parser.add_argument("--remote-identifier", required=True)
    parser.add_argument("--remote-revision", required=True)
    parser.add_argument("--experiment-id", default="NOT_EXECUTED")
    args = parser.parse_args()

    if not args.local_path.exists():
        print(f"local artifact not found: {args.local_path}", file=sys.stderr)
        return 2
    if not args.remote_downloaded_path.exists():
        print(f"downloaded remote copy not found: {args.remote_downloaded_path}", file=sys.stderr)
        return 2

    local_sha = sha256_file(args.local_path)
    remote_sha = sha256_file(args.remote_downloaded_path)
    verification_status = compare_hashes(local_sha, remote_sha)

    row = build_artifact_index_row(
        artifact_id=args.local_path.name,
        experiment_id=args.experiment_id,
        local_path=str(args.local_path),
        sha256=local_sha,
        size_bytes=args.local_path.stat().st_size,
        git_sha=_git_head(),
        platform=args.platform,
        remote_identifier=args.remote_identifier,
        remote_revision=args.remote_revision,
        upload_timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        verification_status=verification_status,
    )
    append_row(row)

    print(f"local_sha256={local_sha}")
    print(f"remote_sha256={remote_sha}")
    print(f"status={verification_status}")
    return 0 if verification_status == "MATCH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
