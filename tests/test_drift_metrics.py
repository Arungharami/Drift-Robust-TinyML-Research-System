import numpy as np
from src.drift.metrics import normalized_wasserstein, standardized_mean_shift
def test_identical_samples_have_zero_drift():
    x=np.array([1.,2.,3.]); assert normalized_wasserstein(x,x)==0; assert standardized_mean_shift(x,x)==0
def test_shift_is_detected(): assert standardized_mean_shift(np.arange(10), np.arange(10)+2) > 0
