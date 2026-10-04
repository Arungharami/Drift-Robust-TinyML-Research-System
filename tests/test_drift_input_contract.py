import unittest

import numpy as np

from src.drift.metrics import normalized_wasserstein, standardized_mean_shift


class TestDriftInputContract(unittest.TestCase):
    def test_invalid_samples_fail_instead_of_emitting_nan(self):
        for metric in (normalized_wasserstein, standardized_mean_shift):
            for sample in ([], [1.0], [1.0, np.nan], [1.0, np.inf], [[1.0, 2.0]]):
                with self.subTest(metric=metric.__name__, sample=sample), self.assertRaises(ValueError):
                    metric(sample, [1.0, 2.0])

    def test_invalid_scale_guard_fails(self):
        for metric in (normalized_wasserstein, standardized_mean_shift):
            for epsilon in (0, -1, np.nan, np.inf):
                with self.subTest(epsilon=epsilon), self.assertRaises(ValueError):
                    metric([1, 2], [2, 3], epsilon=epsilon)

    def test_identical_valid_samples_still_have_zero_drift(self):
        for metric in (normalized_wasserstein, standardized_mean_shift):
            self.assertEqual(metric([1, 2, 3], [1, 2, 3]), 0)
