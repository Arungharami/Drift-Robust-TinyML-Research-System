from __future__ import annotations
import pytest
from src.xai.run_stage12 import benchmark_callable, summarize

def test_benchmark_returns_positive_requested_count():
    rows=benchmark_callable(lambda: sum(range(20)),warmups=2,repeats=4)
    assert len(rows)==4 and all(v>0 for v in rows)

def test_benchmark_rejects_invalid_counts():
    with pytest.raises(ValueError): benchmark_callable(lambda:None,-1,1)
    with pytest.raises(ValueError): benchmark_callable(lambda:None,0,0)

def test_summary_groups_methods_and_converts_to_ms():
    base={"experiment_id":"E","model_id":"M","method":"A","sample_id":"s","batch":2,"row_index_in_batch":0,"repeat":1}
    rows=[{**base,"latency_ns":1_000_000},{**base,"repeat":2,"latency_ns":3_000_000}]
    out=summarize(rows)
    assert len(out)==1
    assert out[0]["median_latency_ms"]==pytest.approx(2.0)
    assert out[0]["mean_latency_ms"]==pytest.approx(2.0)
