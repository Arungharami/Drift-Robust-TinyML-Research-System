import pytest
from src.data.chronology import ChronologicalSplit, expanding_window, fixed_origin
def test_fixed_origin(): assert fixed_origin(10).train_batches == (1,)
def test_expanding_window(): assert expanding_window(4).train_batches == (1,2,3)
def test_future_leakage_rejected():
    with pytest.raises(ValueError): ChronologicalSplit("bad", (1,4), (3,))
