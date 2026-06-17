# Cluster bootstrap of pair-partition AUC estimators

5000 bootstrap iterations; cluster unit = system_id; scores = mean OOF across repeated-seed CV.

| predictor_set | predictor_label | n_systems | n_bootstrap_iterations | auc_pooled_point | auc_pooled_median | auc_pooled_p025 | auc_pooled_p975 | auc_pooled_n_valid | auc_pooled_nan_fraction | auc_within_groups_point | auc_within_groups_median | auc_within_groups_p025 | auc_within_groups_p975 | auc_within_groups_n_valid | auc_within_groups_nan_fraction | auc_cross_groups_point | auc_cross_groups_median | auc_cross_groups_p025 | auc_cross_groups_p975 | auc_cross_groups_n_valid | auc_cross_groups_nan_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_basic_structural | Family B graph tallies | 12 | 5000 | 0.981 | 0.978 | 0.851 | 1.000 | 4837 | 0.033 | 0.667 | 0.667 | 0.333 | 1.000 | 4451 | 0.110 | 0.990 | 0.994 | 0.923 | 1.000 | 4837 | 0.033 |
| prevalence_only | prevalence-only baseline | 12 | 5000 | 0.944 | 0.934 | 0.661 | 1.000 | 4843 | 0.031 | 0.000 | 0.000 | 0.000 | 0.000 | 4436 | 0.113 | 0.971 | 1.000 | 0.820 | 1.000 | 4843 | 0.031 |
