"""Run IDs and run_manifest.json schema for real Colab executions (Missions 16-17), plus the
Notebook-01 hard dataset gate checker (Mission 19).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import DEFAULT_CONFIG_PATH, get_value, load_config
from .environments import validate_environment_label

RUN_ID_RE = re.compile(r"^\d{8}T\d{6}Z_[A-Z0-9_]+$")

# Fields required before a run starts (Mission 17, first half).
REQUIRED_PRE_EXECUTION_FIELDS = (
    "run_id",
    "git_sha",
    "branch",
    "dataset_archive_sha256",
    "dataset_manifest_sha256",
    "config_sha256",
    "environment",
    "colab_cli_version",
    "session_name",
    "requested_accelerator",
    "actual_accelerator",
    "python_version",
    "package_versions",
    "start_timestamp",
    "status",
)
# Additional fields required once a run finishes (Mission 17, second half).
REQUIRED_POST_EXECUTION_FIELDS = ("end_timestamp", "notebooks_executed", "result_paths")


def new_run_id(descriptor: str, timestamp: datetime | None = None) -> str:
    """Build a run id like 20260810T153000Z_FIXED_ORIGIN_CPU.

    `timestamp` should be supplied explicitly by callers that need determinism (tests, replay);
    it defaults to the current UTC time for interactive/script use.
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    stamp = timestamp.strftime("%Y%m%dT%H%M%SZ")
    clean_descriptor = re.sub(r"[^A-Za-z0-9_]+", "_", descriptor).upper().strip("_")
    if not clean_descriptor:
        raise ValueError("descriptor must contain at least one alphanumeric character")
    run_id = f"{stamp}_{clean_descriptor}"
    if not RUN_ID_RE.match(run_id):
        raise ValueError(f"generated run_id failed format validation: {run_id}")
    return run_id


def build_run_manifest(**fields: Any) -> dict[str, Any]:
    """Construct the pre-execution run_manifest.json. Raises ValueError if incomplete/invalid."""
    missing = [f for f in REQUIRED_PRE_EXECUTION_FIELDS if f not in fields]
    if missing:
        raise ValueError(f"run manifest missing required fields: {missing}")
    validate_environment_label(fields["environment"])
    if not RUN_ID_RE.match(fields["run_id"]):
        raise ValueError(f"run_id fails format validation: {fields['run_id']}")
    return dict(fields)


def complete_run_manifest(manifest: dict[str, Any], **fields: Any) -> dict[str, Any]:
    """Add post-execution fields to a manifest previously built with build_run_manifest()."""
    missing = [f for f in REQUIRED_POST_EXECUTION_FIELDS if f not in fields]
    if missing:
        raise ValueError(f"run manifest completion missing required fields: {missing}")
    completed = dict(manifest)
    completed.update(fields)
    return completed


def validate_run_manifest(manifest: dict[str, Any], require_complete: bool = False) -> list[str]:
    """Return a list of validation errors (empty list == valid). Never raises."""
    errors = [f"missing: {f}" for f in REQUIRED_PRE_EXECUTION_FIELDS if f not in manifest]
    if require_complete:
        errors += [f"missing: {f}" for f in REQUIRED_POST_EXECUTION_FIELDS if f not in manifest]
    if "environment" in manifest:
        try:
            validate_environment_label(manifest["environment"])
        except ValueError as exc:
            errors.append(str(exc))
    if "run_id" in manifest and not RUN_ID_RE.match(str(manifest["run_id"])):
        errors.append(f"run_id fails format validation: {manifest['run_id']}")
    return errors


# --- Notebook-01 hard dataset gate (Mission 19) -----------------------------------------

_GATE_PATTERNS = {
    "samples": re.compile(r"\bsamples?\D{0,10}(\d{3,7})\b", re.IGNORECASE),
    "features": re.compile(r"\bfeatures?\D{0,10}(\d{1,4})\b", re.IGNORECASE),
    "batches": re.compile(r"\bbatches?\D{0,10}(\d{1,3})\b", re.IGNORECASE),
    "classes": re.compile(r"\bclasses?\D{0,10}(\d{1,3})\b", re.IGNORECASE),
}
_SHA_PATTERN = re.compile(r"\b([a-fA-F0-9]{64})\b")


def extract_notebook_text(notebook_path: Path) -> str:
    """Concatenate all stream/text-plain output text from an executed .ipynb for gate scanning."""
    nb = json.loads(Path(notebook_path).read_text(encoding="utf-8"))
    chunks: list[str] = []
    for cell in nb.get("cells", []):
        for out in cell.get("outputs", []) or []:
            text = out.get("text")
            if isinstance(text, list):
                chunks.append("".join(text))
            elif isinstance(text, str):
                chunks.append(text)
            data = out.get("data", {})
            plain = data.get("text/plain") if isinstance(data, dict) else None
            if isinstance(plain, list):
                chunks.append("".join(plain))
            elif isinstance(plain, str):
                chunks.append(plain)
    return "\n".join(chunks)


def check_dataset_gate(
    notebook_path: Path, config_path: Path = DEFAULT_CONFIG_PATH
) -> tuple[bool, dict[str, Any]]:
    """Scan an executed Notebook-01's outputs for the required dataset dimensions/SHA-256.

    Returns (passed, details). This is a text-scan safety net, not a substitute for the
    notebook's own assertions — it exists so run_core_repro.sh can hard-stop before
    Notebook 02 runs if the executed output doesn't actually contain the expected values.
    """
    config = load_config(config_path)
    gate = get_value(config, "colab.dataset_gate", {}) or {}
    text = extract_notebook_text(notebook_path)

    found_sha = set(_SHA_PATTERN.findall(text))
    expected_sha = str(gate.get("archive_sha256", "")).lower()
    sha_ok = expected_sha in {s.lower() for s in found_sha}

    details: dict[str, Any] = {"sha256_match": sha_ok, "found_sha256": sorted(found_sha)}
    dims_ok = True
    for key in ("samples", "features", "batches", "classes"):
        expected = gate.get(key)
        found = bool(expected is not None and re.search(rf"\b{re.escape(str(expected))}\b", text))
        details[key] = {"expected": expected, "found_in_text": found}
        dims_ok = dims_ok and found

    passed = sha_ok and dims_ok
    details["passed"] = passed
    return passed, details


def _cli() -> int:
    parser = argparse.ArgumentParser(prog="python3 -m src.colab_control.manifest")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run_id = sub.add_parser("new-run-id")
    p_run_id.add_argument("--descriptor", required=True)

    p_gate = sub.add_parser("check-dataset-gate")
    p_gate.add_argument("--notebook", required=True, type=Path)
    p_gate.add_argument("--config", default=DEFAULT_CONFIG_PATH, type=Path)

    args = parser.parse_args()
    if args.cmd == "new-run-id":
        print(new_run_id(args.descriptor))
        return 0
    if args.cmd == "check-dataset-gate":
        passed, details = check_dataset_gate(args.notebook, args.config)
        print(json.dumps(details, indent=2))
        return 0 if passed else 1
    return 2


if __name__ == "__main__":
    sys.exit(_cli())
