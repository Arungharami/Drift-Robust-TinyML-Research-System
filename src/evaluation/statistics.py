"""Small-sample drift/performance association summaries."""
from __future__ import annotations
import numpy as np
from scipy.stats import spearmanr

def spearman_summary(x: np.ndarray, y: np.ndarray) -> dict[str, float | int | str]:
    result=spearmanr(x,y)
    return {"n":len(x),"coefficient":float(result.statistic),"p_value":float(result.pvalue),"ci":"NOT_CALCULATED_N_EQ_9","limitation":"Nine batches; exploratory association, non-causal."}
