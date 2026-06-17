# Pair-partition AUC decomposition summary (FSM cohort)

Pooled ROC-AUC is reported together with within-group and cross-group pair-stratum AUCs. These partition eligible positive–negative comparison pairs; they do not form an additive decomposition of AUC values.

Dual-class groups (ndc): 2/12.

## Pair structure (label-only; identical across predictors)

| n_groups | ndc | n_within_pairs | n_cross_pairs | n_total_pairs | share_within_pairs | share_cross_pairs |
| --- | --- | --- | --- | --- | --- | --- |
| 12.000 | 2.000 | 150.000 | 5220.000 | 5370.000 | 0.028 | 0.972 |

## AUC by predictor (mean across seeds)

| predictor_set | predictor_label | n_seeds | auc_pooled_mean | auc_pooled_p025 | auc_pooled_p975 | auc_within_groups_mean | auc_within_groups_p025 | auc_within_groups_p975 | auc_cross_groups_mean | auc_cross_groups_p025 | auc_cross_groups_p975 | share_within_pairs_mean | share_within_pairs_p025 | share_within_pairs_p975 | share_cross_pairs_mean | share_cross_pairs_p025 | share_cross_pairs_p975 | n_within_pairs | n_cross_pairs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_basic_structural | Family B graph tallies | 100 | 0.981 | 0.976 | 0.985 | 0.751 | 0.698 | 0.797 | 0.987 | 0.983 | 0.991 | 0.028 | 0.028 | 0.028 | 0.972 | 0.972 | 0.972 | 150 | 5220 |
| prevalence_only | prevalence-only baseline | 100 | 0.958 | 0.951 | 0.964 | 0.259 | 0.130 | 0.368 | 0.978 | 0.974 | 0.981 | 0.028 | 0.028 | 0.028 | 0.972 | 0.972 | 0.972 | 150 | 5220 |
