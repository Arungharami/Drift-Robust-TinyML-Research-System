"""Leakage-resistant chronological split definitions."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ChronologicalSplit:
    protocol: str
    train_batches: tuple[int, ...]
    test_batches: tuple[int, ...]
    def __post_init__(self) -> None:
        if set(self.train_batches) & set(self.test_batches): raise ValueError("Train/test batches overlap")
        if self.test_batches and max(self.train_batches) >= min(self.test_batches): raise ValueError("Future leakage detected")

def fixed_origin(test_batch: int) -> ChronologicalSplit:
    return ChronologicalSplit("FIXED_ORIGIN", (1,), (test_batch,))

def expanding_window(test_batch: int) -> ChronologicalSplit:
    if test_batch < 2: raise ValueError("Test batch must be >= 2")
    return ChronologicalSplit("EXPANDING_WINDOW", tuple(range(1, test_batch)), (test_batch,))
