# Research protocol

The primary protocol is fixed-origin future-batch evaluation: batch 1 is the sole training batch and batches 2–10 are evaluated independently. Every fitted transform must see batch 1 only. Expanding-window evaluation uses only batches preceding its test batch. IID random splitting is `DIAGNOSTIC_ONLY` and cannot support the primary temporal claims.

Checkpoint-1 drift metrics are normalized Wasserstein distance (distribution displacement in reference-batch standard-deviation units) and absolute standardized mean shift (interpretable location change). The median across features is used for a robust global summary. These descriptive metrics do not imply causality or significance.
