# Cluster bootstrap of CV − LOSO Δ by system_id

5000 bootstrap iterations; resampling unit = system_id; pooled ROC-AUC on resampled rows; NaN retained when LOSO undefined.

| predictor_set | family_label | cv_roc_auc_mean_across_seeds | loso_roc_auc_mean_definable_folds | ndc | n_systems | delta_point_estimate | delta_median_bootstrap | delta_p025 | delta_p975 | n_valid_bootstrap_iterations | n_bootstrap_iterations | bootstrap_definability_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_gate_only | Family A gates (legacy deposit) | 0.614 | 0.833 | 2 | 12 | -0.220 | 0.056 | -0.193 | 0.276 | 4837 | 5000 | 0.967 |
| B_basic_structural | fixed audit predictor contract | 0.981 | 0.583 | 2 | 12 | 0.397 | 0.288 | -0.026 | 0.772 | 4843 | 5000 | 0.969 |
| C_reference_difference | Family C ref-diff (legacy deposit) | 1.000 | 1.000 | 2 | 12 | 0.000 | 0.000 | 0.000 | 0.000 | 4864 | 5000 | 0.973 |
| D_combined | Family D combined (legacy deposit) | 1.000 | 1.000 | 2 | 12 | 0.000 | 0.007 | -0.000 | 0.036 | 4846 | 5000 | 0.969 |
| prevalence_only | prevalence-only baseline | 0.958 | 0.500 | 2 | 12 | 0.458 | 0.893 | 0.492 | 1.000 | 4851 | 5000 | 0.970 |
