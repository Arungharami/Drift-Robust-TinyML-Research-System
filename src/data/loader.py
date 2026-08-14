"""Strict parser for UCI LIBSVM-like chronological batch files."""
from __future__ import annotations
import re
from pathlib import Path
import numpy as np

def batch_number(path: Path) -> int:
    match = re.search(r"batch(\d+)", path.name, re.I)
    if not match: raise ValueError(f"Cannot infer batch from {path}")
    return int(match.group(1))

def load_batch(path: Path, n_features: int = 128) -> tuple[np.ndarray, np.ndarray]:
    rows: list[np.ndarray] = []; labels: list[int] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        parts = line.split()
        if not parts: continue
        try: label = int(float(parts[0]))
        except ValueError as exc: raise ValueError(f"Malformed label at {path}:{line_number}") from exc
        row = np.zeros(n_features, dtype=float); seen: set[int] = set()
        for token in parts[1:]:
            try: key, value = token.split(":", 1); index = int(key) - 1; number = float(value)
            except ValueError as exc: raise ValueError(f"Malformed token at {path}:{line_number}: {token}") from exc
            if not 0 <= index < n_features or index in seen: raise ValueError(f"Invalid feature index at {path}:{line_number}")
            row[index] = number; seen.add(index)
        rows.append(row); labels.append(label)
    return np.vstack(rows), np.asarray(labels, dtype=int)

def discover_batches(raw_dir: Path) -> list[Path]:
    paths = sorted(raw_dir.rglob("batch*.dat"), key=batch_number)
    if not paths: raise FileNotFoundError(f"No batch*.dat files below {raw_dir}")
    return paths
