# Leave-one-model-out summary

Cross-model generalization: train on runs from three LLM families, test on the held-out fourth. Compared with stratified 5-fold random CV from `model_performance.md`.

## LOMO aggregate performance (mean ± std across 4 held-out models)

| predictor_set | model | roc_auc_mean | roc_auc_std | roc_auc_n_valid | roc_auc_min | roc_auc_max | pr_auc_mean | pr_auc_std | pr_auc_n_valid | pr_auc_min | pr_auc_max | balanced_accuracy_mean | balanced_accuracy_std | balanced_accuracy_n_valid | balanced_accuracy_min | balanced_accuracy_max | f1_mean | f1_std | f1_n_valid | f1_min | f1_max | recall_full_pass_mean | recall_full_pass_std | recall_full_pass_n_valid | recall_full_pass_min | recall_full_pass_max | specificity_non_full_pass_mean | specificity_non_full_pass_std | specificity_non_full_pass_n_valid | specificity_non_full_pass_min | specificity_non_full_pass_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_gate_only | logistic_regression | 0.637 | 0.125 | 4.000 | 0.550 | 0.821 | 0.197 | 0.069 | 4.000 | 0.100 | 0.263 | 0.637 | 0.125 | 4.000 | 0.550 | 0.821 | 0.325 | 0.101 | 4.000 | 0.182 | 0.417 | 1.000 | 0.000 | 4.000 | 1.000 | 1.000 | 0.274 | 0.250 | 4.000 | 0.100 | 0.641 |
| A_gate_only | random_forest | 0.637 | 0.125 | 4.000 | 0.550 | 0.821 | 0.197 | 0.069 | 4.000 | 0.100 | 0.263 | 0.637 | 0.125 | 4.000 | 0.550 | 0.821 | 0.325 | 0.101 | 4.000 | 0.182 | 0.417 | 1.000 | 0.000 | 4.000 | 1.000 | 1.000 | 0.274 | 0.250 | 4.000 | 0.100 | 0.641 |
| B_basic_structural | logistic_regression | 0.769 | 0.158 | 4.000 | 0.556 | 0.900 | 0.439 | 0.110 | 4.000 | 0.333 | 0.562 | 0.693 | 0.154 | 4.000 | 0.483 | 0.850 | 0.372 | 0.103 | 4.000 | 0.256 | 0.500 | 0.750 | 0.289 | 4.000 | 0.500 | 1.000 | 0.636 | 0.199 | 4.000 | 0.467 | 0.889 |
| B_basic_structural | random_forest | 0.790 | 0.246 | 4.000 | 0.528 | 1.000 | 0.712 | 0.359 | 4.000 | 0.258 | 1.000 | 0.821 | 0.181 | 4.000 | 0.639 | 1.000 | 0.642 | 0.263 | 4.000 | 0.400 | 1.000 | 0.750 | 0.289 | 4.000 | 0.500 | 1.000 | 0.892 | 0.091 | 4.000 | 0.778 | 1.000 |
| D_combined | logistic_regression | 1.000 | 0.000 | 4.000 | 1.000 | 1.000 | 1.000 | 0.000 | 4.000 | 1.000 | 1.000 | 0.959 | 0.050 | 4.000 | 0.900 | 1.000 | 0.792 | 0.250 | 4.000 | 0.500 | 1.000 | 1.000 | 0.000 | 4.000 | 1.000 | 1.000 | 0.918 | 0.099 | 4.000 | 0.800 | 1.000 |
| D_combined | random_forest | 1.000 | 0.000 | 4.000 | 1.000 | 1.000 | 1.000 | 0.000 | 4.000 | 1.000 | 1.000 | 0.925 | 0.119 | 4.000 | 0.750 | 1.000 | 0.833 | 0.192 | 4.000 | 0.667 | 1.000 | 0.875 | 0.250 | 4.000 | 0.500 | 1.000 | 0.975 | 0.050 | 4.000 | 0.900 | 1.000 |

## Average, worst-case, and best-case ROC-AUC (held-out models)

| predictor_set | classifier | roc_auc_mean | roc_auc_worst | roc_auc_best |
| --- | --- | --- | --- | --- |
| A_gate_only | logistic_regression | 0.637 | 0.550 | 0.821 |
| A_gate_only | random_forest | 0.637 | 0.550 | 0.821 |
| B_basic_structural | logistic_regression | 0.769 | 0.556 | 0.900 |
| B_basic_structural | random_forest | 0.790 | 0.528 | 1.000 |
| D_combined | logistic_regression | 1.000 | 1.000 | 1.000 |
| D_combined | random_forest | 1.000 | 1.000 | 1.000 |

## Random CV vs LOMO and degradation

Δ = random CV ROC-AUC mean − LOMO ROC-AUC mean (positive ⇒ degradation under LOMO).

| predictor_set | model | random_cv_roc_auc_mean | lomo_roc_auc_mean | delta_roc_auc | random_cv_pr_auc_mean | lomo_pr_auc_mean | delta_pr_auc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_gate_only | logistic_regression | 0.628 | 0.637 | -0.009 | 0.185 | 0.197 | -0.012 |
| A_gate_only | random_forest | 0.628 | 0.637 | -0.009 | 0.185 | 0.197 | -0.012 |
| B_basic_structural | logistic_regression | 0.747 | 0.769 | -0.022 | 0.429 | 0.439 | -0.010 |
| B_basic_structural | random_forest | 0.982 | 0.790 | 0.192 | 0.894 | 0.712 | 0.182 |
| D_combined | logistic_regression | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 |
| D_combined | random_forest | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 |

## Performance highlights

- Largest ROC-AUC drop vs random CV: **B_basic_structural** + **random_forest** (Δ = 0.192).
- Best LOMO ROC-AUC (mean across held-out models): **D_combined** + **logistic_regression** (1.000).
- Worst LOMO ROC-AUC (mean across held-out models): **A_gate_only** + **logistic_regression** (0.637).
- Mean degradation by predictor set (ROC-AUC):
  - `B_basic_structural`: Δ = 0.085
  - `D_combined`: Δ = 0.000
  - `A_gate_only`: Δ = -0.009

## Do structural predictors generalize across LLM families?

Interpretation is **exploratory** and must not be overstated:

- LOMO tests whether gate and structural signals learned from three LLM families rank behavioural risk on a fourth, unseen family.
- If LOMO ROC-AUC remains well above chance while random CV is high, signals may reflect **FSM properties** rather than LLM-specific artefacts.
- If LOMO degrades sharply (especially for set **B**), structural counts may encode family-specific generation habits that do not transfer.
- Set **D** includes oracle-adjacent traceability counts; strong LOMO performance there would not imply deployable pre-oracle screening.
- Small held-out folds (n≈44–55 per model) and class imbalance limit stability of ROC-AUC and F1.

## Interpretation guardrails

- **Exploratory cross-model check** — not confirmatory evidence.
- Does not prove that predictors are model-independent; only reports out-of-family ranking under this frozen cohort.
- Do **not** equate random-CV performance with cross-LLM robustness.
- No causal claims about LLM families or structural mechanisms.
