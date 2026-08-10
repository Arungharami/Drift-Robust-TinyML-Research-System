#!/usr/bin/env python3
"""scripts/colab/read_config.py — print one value from configs/colab.yaml for shell consumption.

Usage: read_config.py <dotted.key> [default]
Exits 1 if the key is missing and no default was given.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.colab_control.config import load_config, get_value  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: read_config.py <dotted.key> [default]", file=sys.stderr)
        return 2
    key = sys.argv[1]
    default = sys.argv[2] if len(sys.argv) > 2 else None
    config = load_config()
    value = get_value(config, key, default)
    if value is None:
        print(f"missing config key: {key}", file=sys.stderr)
        return 1
    print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
