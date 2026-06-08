# Leave-one-system-out summary

Aggregated LOSO metrics (mean ± std across 12 held-out systems) compared with stratified 5-fold random CV from `model_performance.md`.

## LOSO aggregate performance

| predictor_set | model | roc_auc_mean | roc_auc_std | roc_auc_n_valid | pr_auc_mean | pr_auc_std | pr_auc_n_valid | balanced_accuracy_mean | balanced_accuracy_std | balanced_accuracy_n_valid | f1_mean | f1_std | f1_n_valid | recall_full_pass_mean | recall_full_pass_std | recall_full_pass_n_valid | specificity_non_full_pass_mean | specificity_non_full_pass_std | specificity_non_full_pass_n_valid |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_gate_only | logistic_regression | 0.833 | 0.236 | 2.000 | 0.667 | 0.471 | 2.000 | 0.331 | 0.384 | 12.000 | 0.208 | 0.396 | 12.000 | 0.250 | 0.452 | 12.000 | 0.219 | 0.305 | 12.000 |
| A_gate_only | decision_tree | 0.833 | 0.236 | 2.000 | 0.667 | 0.471 | 2.000 | 0.331 | 0.384 | 12.000 | 0.208 | 0.396 | 12.000 | 0.250 | 0.452 | 12.000 | 0.219 | 0.305 | 12.000 |
| A_gate_only | random_forest | 0.833 | 0.236 | 2.000 | 0.667 | 0.471 | 2.000 | 0.331 | 0.384 | 12.000 | 0.208 | 0.396 | 12.000 | 0.250 | 0.452 | 12.000 | 0.219 | 0.305 | 12.000 |
| B_basic_structural | logistic_regression | 0.333 | 0.471 | 2.000 | 0.292 | 0.059 | 2.000 | 0.539 | 0.380 | 12.000 | 0.000 | 0.000 | 12.000 | 0.000 | 0.000 | 12.000 | 0.622 | 0.419 | 12.000 |
| B_basic_structural | decision_tree | 0.583 | 0.118 | 2.000 | 0.292 | 0.059 | 2.000 | 0.681 | 0.371 | 12.000 | 0.042 | 0.144 | 12.000 | 0.083 | 0.289 | 12.000 | 0.694 | 0.393 | 12.000 |
| B_basic_structural | random_forest | 0.583 | 0.118 | 2.000 | 0.292 | 0.059 | 2.000 | 0.792 | 0.317 | 12.000 | 0.000 | 0.000 | 12.000 | 0.000 | 0.000 | 12.000 | 0.875 | 0.292 | 12.000 |
| C_reference_difference | logistic_regression | 1.000 | 0.000 | 2.000 | 1.000 | 0.000 | 2.000 | 0.889 | 0.296 | 12.000 | 0.208 | 0.396 | 12.000 | 0.250 | 0.452 | 12.000 | 0.778 | 0.410 | 12.000 |
| C_reference_difference | decision_tree | 0.833 | 0.236 | 2.000 | 0.667 | 0.471 | 2.000 | 0.868 | 0.296 | 12.000 | 0.196 | 0.372 | 12.000 | 0.229 | 0.419 | 12.000 | 0.778 | 0.410 | 12.000 |
| C_reference_difference | random_forest | 1.000 | 0.000 | 2.000 | 1.000 | 0.000 | 2.000 | 0.972 | 0.096 | 12.000 | 0.208 | 0.396 | 12.000 | 0.250 | 0.452 | 12.000 | 0.861 | 0.332 | 12.000 |
| D_combined | logistic_regression | 0.833 | 0.236 | 2.000 | 0.750 | 0.354 | 2.000 | 0.889 | 0.296 | 12.000 | 0.208 | 0.396 | 12.000 | 0.250 | 0.452 | 12.000 | 0.778 | 0.410 | 12.000 |
| D_combined | decision_tree | 0.833 | 0.236 | 2.000 | 0.667 | 0.471 | 2.000 | 0.868 | 0.296 | 12.000 | 0.196 | 0.372 | 12.000 | 0.229 | 0.419 | 12.000 | 0.778 | 0.410 | 12.000 |
| D_combined | random_forest | 1.000 | 0.000 | 2.000 | 1.000 | 0.000 | 2.000 | 0.896 | 0.291 | 12.000 | 0.238 | 0.432 | 12.000 | 0.229 | 0.419 | 12.000 | 0.833 | 0.389 | 12.000 |

## Random CV vs LOSO (ROC-AUC) and degradation

Δ = random CV ROC-AUC mean − LOSO ROC-AUC mean (positive ⇒ degradation under LOSO).

| predictor_set | model | random_cv_roc_auc_mean | loso_roc_auc_mean | delta_roc_auc | random_cv_pr_auc_mean | loso_pr_auc_mean | delta_pr_auc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_gate_only | logistic_regression | 0.628 | 0.833 | -0.205 | 0.185 | 0.667 | -0.482 |
| A_gate_only | decision_tree | 0.628 | 0.833 | -0.205 | 0.185 | 0.667 | -0.482 |
| A_gate_only | random_forest | 0.628 | 0.833 | -0.205 | 0.185 | 0.667 | -0.482 |
| B_basic_structural | logistic_regression | 0.747 | 0.333 | 0.414 | 0.429 | 0.292 | 0.137 |
| B_basic_structural | decision_tree | 0.958 | 0.583 | 0.375 | 0.693 | 0.292 | 0.401 |
| B_basic_structural | random_forest | 0.982 | 0.583 | 0.399 | 0.894 | 0.292 | 0.602 |
| C_reference_difference | logistic_regression | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 |
| C_reference_difference | decision_tree | 1.000 | 0.833 | 0.167 | 1.000 | 0.667 | 0.333 |
| C_reference_difference | random_forest | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 |
| D_combined | logistic_regression | 1.000 | 0.833 | 0.167 | 1.000 | 0.750 | 0.250 |
| D_combined | decision_tree | 1.000 | 0.833 | 0.167 | 1.000 | 0.667 | 0.333 |
| D_combined | random_forest | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 |

## Performance degradation highlights

- Largest ROC-AUC drop: **B_basic_structural** + **logistic_regression** (Δ = 0.414).
- Best LOSO ROC-AUC (mean across systems): **C_reference_difference** + **random_forest** (1.000).
- Mean degradation by predictor set (ROC-AUC):
  - `B_basic_structural`: Δ = 0.396
  - `D_combined`: Δ = 0.111
  - `C_reference_difference`: Δ = 0.056
  - `A_gate_only`: Δ = -0.205

## Interpretation guardrails

- **Exploratory generalization check** — not confirmatory evidence.
- LOSO tests specification-level transfer; it does not prove causal mechanisms.
- Reference-difference predictors may not transfer when traceability profiles differ across systems.
- Small held-out folds (e.g., `bike_rental`, n=5) yield unstable ROC-AUC.
- Do **not** equate in-sample random-CV performance with cross-specification robustness.
