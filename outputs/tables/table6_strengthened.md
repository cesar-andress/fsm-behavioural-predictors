# Strengthened Table 6 — CV vs LOSO and bootstrap Δ

LOSO μ = mean of definable per-system fold ROC-AUC (RF-only). Δ bootstrap uses cluster resampling by system_id.

| predictor_family | classifier | cv_roc_auc_mean | cv_roc_auc_interval | loso_roc_auc | ndc | delta | delta_bootstrap_interval | delta_bootstrap_definability_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Family A gates (legacy deposit) | random_forest | 0.614 | 0.614 [0.599, 0.629] | 0.833 | 2/12 | -0.220 | 0.056 [-0.193, 0.276] | 0.967 |
| fixed audit predictor contract | random_forest | 0.981 | 0.981 [0.976, 0.985] | 0.583 | 2/12 | 0.397 | 0.288 [-0.026, 0.772] | 0.969 |
| Family C ref-diff (legacy deposit) | random_forest | 1.000 | 1.000 [1.000, 1.000] | 1.000 | 2/12 | 0.000 | 0.000 [0.000, 0.000] | 0.973 |
| Family D combined (legacy deposit) | random_forest | 1.000 | 1.000 [1.000, 1.000] | 1.000 | 2/12 | 0.000 | 0.007 [-0.000, 0.036] | 0.969 |
| prevalence-only baseline | prevalence_only | 0.958 | 0.958 [0.951, 0.964] | 0.500 | 2/12 | 0.458 | 0.893 [0.492, 1.000] | 0.970 |
