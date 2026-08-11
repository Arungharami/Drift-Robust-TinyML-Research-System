# Statistical validation methodology

Seed 42 remains the frozen baseline. A predefined stochastic-model seed family must be registered before execution; seeds may not be selected after observing outcomes. Batch-level summaries report median, mean where meaningful, standard deviation, IQR, worst batch, and best batch.

For paired model/protocol comparisons, the primary resampling unit is the prediction within the same chronological test batch when raw paired predictions exist; a hierarchical bootstrap first samples batches and then observations when estimating a across-batch deployment summary. Batch-only inference with nine future batches is reported cautiously and emphasizes confidence intervals and paired effect sizes. No p-value is produced when assumptions or effective sample size make it misleading.
