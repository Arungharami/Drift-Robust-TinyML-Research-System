"""Seed and execution-environment capture for local and Colab runs."""
from __future__ import annotations
import importlib.metadata
import json
import os
import platform
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import psutil

def set_seed(seed: int) -> None:
    random.seed(seed); np.random.seed(seed); os.environ["PYTHONHASHSEED"] = str(seed)

def capture_environment(output: Path, seed: int = 42) -> dict:
    set_seed(seed)
    def cmd(args: list[str]) -> str | None:
        try: return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.SubprocessError): return None
    packages = {}
    for name in ("numpy", "pandas", "scipy", "scikit-learn", "matplotlib", "PyYAML"):
        try: packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: packages[name] = None
    info = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(), "in_colab": "google.colab" in sys.modules,
        "python": sys.version, "platform": platform.platform(), "cpu": platform.processor() or platform.machine(),
        "logical_cpu_count": os.cpu_count(), "ram_bytes": psutil.virtual_memory().total,
        "gpu": cmd(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]),
        "cuda": cmd(["nvcc", "--version"]), "git_commit": cmd(["git", "rev-parse", "HEAD"]),
        "seed": seed, "packages": packages,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(info, indent=2), encoding="utf-8")
    return info
