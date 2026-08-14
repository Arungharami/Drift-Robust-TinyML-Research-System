"""Local-vs-Colab result comparison (Mission 21).

Feeds results/reproducibility/colab_vs_local_baselines.csv. Colab values must come from an
actually executed Colab run — this module never copies a local value into the colab column,
and rows with no matching Colab result are flagged MISSING_COLAB_VALUE rather than silently
dropped or backfilled.
"""
from __future__ import annotations

from typing import Any

DEFAULT_TOLERANCE = 1e-6


def _key(row: dict[str, Any]) -> tuple:
    return (row["model"], row["batch"], row["metric"])


def compare_metrics(
    local_rows: list[dict[str, Any]],
    colab_rows: list[dict[str, Any]],
    tolerance: float = DEFAULT_TOLERANCE,
) -> list[dict[str, Any]]:
    """Each input row: {model, batch, metric, value}.

    Returns rows shaped for the CSV: model, batch, metric, local_value, colab_value,
    absolute_difference, tolerance, status (MATCH / MISMATCH / MISSING_COLAB_VALUE).
    """
    colab_index = {_key(r): r["value"] for r in colab_rows}

    comparisons: list[dict[str, Any]] = []
    for local in local_rows:
        k = _key(local)
        local_value = local["value"]
        if k not in colab_index:
            comparisons.append(
                {
                    "model": local["model"],
                    "batch": local["batch"],
                    "metric": local["metric"],
                    "local_value": local_value,
                    "colab_value": None,
                    "absolute_difference": None,
                    "tolerance": tolerance,
                    "status": "MISSING_COLAB_VALUE",
                }
            )
            continue
        colab_value = colab_index[k]
        diff = abs(local_value - colab_value)
        comparisons.append(
            {
                "model": local["model"],
                "batch": local["batch"],
                "metric": local["metric"],
                "local_value": local_value,
                "colab_value": colab_value,
                "absolute_difference": diff,
                "tolerance": tolerance,
                "status": "MATCH" if diff <= tolerance else "MISMATCH",
            }
        )
    return comparisons
