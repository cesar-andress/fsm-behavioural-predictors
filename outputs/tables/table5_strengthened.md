# Strengthened Table 5 — pooled CV by predictor family (RF)

Repeated-seed pooled CV (100 seeds); intervals are 2.5–97.5 percentiles across seeds.

| predictor_family | classifier | roc_auc_mean | roc_auc_interval | pr_auc_mean | pr_auc_interval | balanced_accuracy_mean | balanced_accuracy_interval | f1_mean | f1_interval | mcc_mean | mcc_interval |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Family A gates | random_forest | 0.614 | 0.614 [0.599, 0.629] | 0.177 | 0.177 [0.172, 0.183] | 0.628 | 0.628 [0.628, 0.628] | 0.311 | 0.311 [0.311, 0.311] | 0.217 | 0.217 [0.217, 0.217] |
| Family B graph tallies | random_forest | 0.981 | 0.981 [0.976, 0.985] | 0.903 | 0.903 [0.886, 0.922] | 0.957 | 0.957 [0.958, 0.958] | 0.799 | 0.799 [0.800, 0.800] | 0.780 | 0.780 [0.782, 0.782] |
| Family C ref-diff | random_forest | 1.000 | 1.000 [1.000, 1.000] | 1.000 | 1.000 [1.000, 1.000] | 1.000 | 1.000 [1.000, 1.000] | 1.000 | 1.000 [1.000, 1.000] | 1.000 | 1.000 [1.000, 1.000] |
| Family D combined | random_forest | 1.000 | 1.000 [1.000, 1.000] | 1.000 | 1.000 [1.000, 1.000] | 1.000 | 1.000 [1.000, 1.000] | 1.000 | 1.000 [1.000, 1.000] | 1.000 | 1.000 [1.000, 1.000] |
| stratified dummy | dummy_stratified | 0.505 | 0.505 [0.430, 0.596] | 0.150 | 0.150 [0.137, 0.191] | 0.505 | 0.505 [0.430, 0.596] | 0.140 | 0.140 [0.000, 0.306] | 0.007 | 0.007 [-0.126, 0.183] |
| prevalence-only baseline | prevalence_only | 0.958 | 0.958 [0.951, 0.964] | 0.840 | 0.840 [0.829, 0.851] | 0.833 | 0.833 [0.833, 0.833] | 0.800 | 0.800 [0.800, 0.800] | 0.795 | 0.795 [0.795, 0.795] |
