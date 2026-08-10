#!/usr/bin/env python3
"""scripts/colab/smoke_test.py — ephemeral Colab smoke test (Mission 24).

Intended to run via `colab run scripts/colab/smoke_test.py` as a one-command ephemeral job.
Prints runtime identity, Python version, and a deterministic calculation, then exits.

NOT scientific evidence. It only proves the CLI can execute a one-off remote job end-to-end;
scientific evidence must come from reproducible scripts/notebooks and saved artifacts.
"""
from __future__ import annotations

import hashlib
import platform
import socket
import sys


def deterministic_check() -> str:
    payload = b"drift-tinyml-colab-cli-smoke-test"
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    print("COLAB_SMOKE_TEST_START")
    print(f"hostname={socket.gethostname()}")
    print(f"platform={platform.platform()}")
    print(f"python_version={sys.version.split()[0]}")
    print(f"deterministic_sha256={deterministic_check()}")
    print("COLAB_SMOKE_TEST_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
