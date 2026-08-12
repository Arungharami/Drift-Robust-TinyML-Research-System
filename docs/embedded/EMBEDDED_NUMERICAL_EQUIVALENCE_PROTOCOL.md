# Embedded numerical-equivalence protocol

Gate `GATE-EMBED-EXPORT-001` freezes validation criteria before any conversion. The scientific reference is the existing Python chain implemented by `src/embedded/reference_inference.py`:

`128 raw features → frozen Batch-1 StandardScaler → frozen estimator → scores/probabilities → original class label`.

No export or quantization occurred while defining this protocol.

## Golden evidence

`embedded_golden_vectors.csv` deliberately combines B2, B6, and B10, every available true class, correct and misclassified cases, high-confidence cases, and low-margin cases for every model. `embedded_boundary_vectors.csv` contains the two smallest probability-margin samples per model and chronological context. Every row retains all 128 raw and 128 transformed values, score and probability vectors, predicted and competing classes, margin, confidence, source hash, and frozen-model hash.

## Three mandatory levels

1. **Preprocessing equivalence:** FP32 maximum absolute transformed-feature error `2e-5` and maximum relative error `2e-6`. Every feature deviation is retained. Nonfinite inputs must be rejected.
2. **Model numerical equivalence:** model-specific score/probability tolerances in `configs/embedded_equivalence_protocol.yaml`. Linear and MLP scores allow `1e-4` and `2e-4` absolute error respectively; SVC permits `2e-4`; random-forest probability error is limited to `1e-6` and leaf-vote semantics must match.
3. **Decision equivalence:** FP32 requires 100% class agreement on both complete and boundary sets. Every flip is reported; average error cannot hide it.

These tolerances reflect a float64 Python reference compared with an initially proposed FP32 implementation. They are tight enough to detect changed operation order or semantics while allowing ordinary FP32 rounding. Relative errors use a `1e-8` denominator floor.

## Future lossy precision

Quantized criteria are separately frozen but are not executed: transformed-feature absolute error at most `5e-3`, score/probability absolute error at most `2e-2`, overall agreement at least 99%, boundary agreement 100%, and macro-F1 degradation at most 0.01. Traditional estimators require model-appropriate parameter precision evaluation; neural QAT is not authorized automatically.

Any unsupported representation, preprocessing mismatch, FP32 boundary flip, tolerance exceedance, algorithm change, untargetable dependency, or irreproducible license fails the future candidate. A failed candidate may not be silently modified.

