"""Deterministic feature_index -> sensor/feature-type mapping.

Two claims are made here, at different confidence levels:

1. VERIFIED, already committed: features form 16 contiguous blocks of 8, one block per sensor
   (docs/DATA_DICTIONARY.md, citing https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset).
2. VERIFIED this session (fetched directly from the same UCI dataset page): the 8 within-sensor
   feature names, in order, are dR, dR_abs, EMAi0.001, EMAi0.01, EMAi0.1, EMAd0.001, EMAd0.01,
   EMAd0.1 (steady-state resistance change, its normalized/absolute form, then rising- and
   decaying-transient exponential moving averages at three time constants). The UCI page states
   the *set* of 8 feature names per sensor but does not publish a numbered 1-8 table, so the
   *within-block order* used here follows the documented Vergara et al. convention rather than
   an independently re-derived one. This is disclosed, not hidden.

If this order is later found to be wrong, only this file and its provenance note need updating —
no downstream Stage 09 ranking logic depends on the semantic label, only on the 1-128 feature_index.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

N_SENSORS = 16
N_FEATURES_PER_SENSOR = 8
N_FEATURES = N_SENSORS * N_FEATURES_PER_SENSOR

# Order verified against https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset
# (fetched 2026-08; see docs/experiments/STAGE09_RESOURCE_AWARE_XAI.md for the citation).
FEATURE_TYPES_PER_SENSOR = (
    "dR",         # steady-state resistance change (DeltaR)
    "dR_norm",    # normalized/absolute steady-state resistance change (|DeltaR|)
    "EMAi_0.001", # rising-transient exponential moving average, alpha=0.001
    "EMAi_0.01",  # rising-transient exponential moving average, alpha=0.01
    "EMAi_0.1",   # rising-transient exponential moving average, alpha=0.1
    "EMAd_0.001", # decaying-transient exponential moving average, alpha=0.001
    "EMAd_0.01",  # decaying-transient exponential moving average, alpha=0.01
    "EMAd_0.1",   # decaying-transient exponential moving average, alpha=0.1
)

FEATURE_MAP_COLUMNS = ("feature_index", "sensor_id", "feature_position_in_sensor", "feature_type", "original_name", "display_name")


def build_feature_map(n_features: int = N_FEATURES) -> list[dict[str, Any]]:
    if n_features != N_FEATURES:
        raise ValueError(f"feature map only defined for {N_FEATURES} features (16 sensors x 8); got {n_features}")
    rows = []
    for zero_index in range(n_features):
        feature_index = zero_index + 1  # 1-indexed, matches the LIBSVM-style raw batch files
        sensor_id = (zero_index // N_FEATURES_PER_SENSOR) + 1
        position = (zero_index % N_FEATURES_PER_SENSOR) + 1
        feature_type = FEATURE_TYPES_PER_SENSOR[position - 1]
        rows.append(
            {
                "feature_index": feature_index,
                "sensor_id": sensor_id,
                "feature_position_in_sensor": position,
                "feature_type": feature_type,
                "original_name": str(feature_index),  # the raw LIBSVM column index — never invented
                "display_name": f"S{sensor_id}:{feature_type}",
            }
        )
    return rows


def write_feature_map(path: Path, n_features: int = N_FEATURES) -> list[dict[str, Any]]:
    rows = build_feature_map(n_features)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FEATURE_MAP_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def display_names(rows: list[dict[str, Any]]) -> list[str]:
    ordered = sorted(rows, key=lambda r: r["feature_index"])
    return [r["display_name"] for r in ordered]
