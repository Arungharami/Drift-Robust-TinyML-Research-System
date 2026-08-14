# Figure index

| Figure | Title | Source CSV | Experiment | Generator | Status |
|---|---|---|---|---|---|
| 1 | Dataset chronology | `results/figures/sources/dataset_timeline.csv` | DATA-AUDIT-001 | `scripts/run_drift_analysis.py` | COMPLETED |
| 2 | Feature × batch drift | `results/figures/sources/feature_batch_drift_heatmap.csv` | DRIFT-FIXED-B1-001 | same | COMPLETED |
| 3 | Top drifting features | `results/figures/sources/top20_drifting_features.csv` | DRIFT-FIXED-B1-001 | same | COMPLETED |
| 4 | Top stable features | `results/figures/sources/top20_stable_features.csv` | DRIFT-FIXED-B1-001 | same | COMPLETED |
| 5 | Global drift trajectory | `results/figures/sources/global_drift_trajectory.csv` | DRIFT-FIXED-B1-001 | same | COMPLETED |
| 6 | Chronological accuracy by model | `results/figures/sources/figure_6_accuracy.csv` | BASE-FIXED-C1-001–C4-001 | `run_classical_baselines.py` | COMPLETED |
| 7 | Chronological Macro-F1 | `results/figures/sources/figure_7_macro_f1.csv` | BASE-FIXED-C1-001–C4-001 | same | COMPLETED |
| 8 | Balanced accuracy across drift | `results/figures/sources/figure_8_balanced_accuracy.csv` | BASE-FIXED-C1-001–C4-001 | same | COMPLETED |
| 9 | B2-to-B10 degradation | `results/figures/sources/figure_9_degradation.csv` | BASE-FIXED-C1-001–C4-001 | same | COMPLETED |
| 10 | Class × batch error | `results/figures/sources/figure_10_class_error_heatmap.csv` | BASE-FIXED-C1-001–C4-001 | same | COMPLETED |
| 11 | Fixed-origin vs expanding-window | `results/figures/sources/figure_11_fixed_vs_expanding.csv` | BASE-FIXED/EXPAND-C1-001–C4-001 | same | COMPLETED |
| 12 | IID vs chronological | `results/figures/sources/figure_12_iid_vs_chronological.csv` | BASE-FIXED/IID-C1-001–C4-001 | same | COMPLETED |
| 13 | Drift vs predictive performance | `results/figures/sources/figure_13_drift_vs_performance.csv` | DRIFT-FIXED-B1-001; BASE-FIXED-C1-001–C4-001 | same | COMPLETED |
| 14 | Feature drift vs importance | `results/figures/sources/figure_14_feature_drift_vs_importance.csv` | DRIFT-FIXED-B1-001; BASE-FIXED-C2-001 | same | COMPLETED |
| 15 | Performance–robustness–complexity | `results/figures/sources/figure_15_accuracy_robustness_complexity.csv` | BASE-FIXED-C1-001–C4-001 | `build_baseline_artifacts.py` | COMPLETED |
