"""Feature-level and aggregate fixed-origin drift tables."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from src.data.loader import batch_number, discover_batches, load_batch
from src.drift.metrics import normalized_wasserstein, standardized_mean_shift

def compute_drift(raw_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    batches = {batch_number(p): load_batch(p) for p in discover_batches(raw_dir)}
    reference = batches[1][0]; records = []
    for batch in sorted(batches)[1:]:
        current = batches[batch][0]
        for feature in range(reference.shape[1]):
            for metric, function in (("normalized_wasserstein", normalized_wasserstein), ("standardized_mean_shift", standardized_mean_shift)):
                records.append({"feature": feature + 1, "sensor": feature // 8 + 1, "reference_batch": 1,
                                "comparison_batch": batch, "metric": metric, "value": function(reference[:, feature], current[:, feature])})
    feature_df = pd.DataFrame(records)
    feature_df["rank"] = feature_df.groupby(["comparison_batch", "metric"])["value"].rank(method="min", ascending=False).astype(int)
    global_df = feature_df.groupby(["reference_batch", "comparison_batch", "metric"], as_index=False)["value"].median().rename(columns={"value": "median_feature_drift"})
    chronology = pd.DataFrame([{"batch": b, "sample_count": len(data[1])} for b, data in sorted(batches.items())])
    return feature_df, global_df, chronology
