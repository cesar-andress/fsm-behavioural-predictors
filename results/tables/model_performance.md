# Model performance

Exploratory stratified 5-fold cross-validation predicting `full_behavioural_pass` from structural signals (behaviourally scored runs only).

**Not confirmatory.** Results indicate out-of-fold discrimination under a fixed, lightly regularised modelling protocol — not causal effects.

| predictor_set | model | roc_auc_mean | roc_auc_std | pr_auc_mean | pr_auc_std | balanced_accuracy_mean | balanced_accuracy_std | f1_mean | f1_std | recall_full_pass_mean | recall_full_pass_std | specificity_non_full_pass_mean | specificity_non_full_pass_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_gate_only | logistic_regression | 0.628 | 0.045 | 0.185 | 0.018 | 0.628 | 0.045 | 0.313 | 0.026 | 1.000 | 0.000 | 0.257 | 0.090 |
| A_gate_only | decision_tree | 0.628 | 0.045 | 0.185 | 0.018 | 0.628 | 0.045 | 0.313 | 0.026 | 1.000 | 0.000 | 0.257 | 0.090 |
| A_gate_only | random_forest | 0.628 | 0.045 | 0.185 | 0.018 | 0.628 | 0.045 | 0.313 | 0.026 | 1.000 | 0.000 | 0.257 | 0.090 |
| A_gate_only | dummy_stratified | 0.508 | 0.082 | 0.165 | 0.036 | 0.508 | 0.082 | 0.145 | 0.152 | 0.133 | 0.139 | 0.883 | 0.024 |
| A_gate_only | dummy_majority | 0.500 | 0.000 | 0.144 | 0.002 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| B_basic_structural | logistic_regression | 0.747 | 0.146 | 0.429 | 0.121 | 0.718 | 0.092 | 0.411 | 0.076 | 0.767 | 0.224 | 0.670 | 0.109 |
| B_basic_structural | decision_tree | 0.958 | 0.021 | 0.693 | 0.103 | 0.880 | 0.077 | 0.665 | 0.066 | 0.900 | 0.224 | 0.860 | 0.092 |
| B_basic_structural | random_forest | 0.982 | 0.010 | 0.894 | 0.035 | 0.958 | 0.014 | 0.803 | 0.054 | 1.000 | 0.000 | 0.916 | 0.028 |
| B_basic_structural | dummy_stratified | 0.508 | 0.082 | 0.165 | 0.036 | 0.508 | 0.082 | 0.145 | 0.152 | 0.133 | 0.139 | 0.883 | 0.024 |
| B_basic_structural | dummy_majority | 0.500 | 0.000 | 0.144 | 0.002 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| C_reference_difference | logistic_regression | 1.000 | 0.000 | 1.000 | 0.000 | 0.958 | 0.017 | 0.804 | 0.062 | 1.000 | 0.000 | 0.916 | 0.034 |
| C_reference_difference | decision_tree | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| C_reference_difference | random_forest | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| C_reference_difference | dummy_stratified | 0.508 | 0.082 | 0.165 | 0.036 | 0.508 | 0.082 | 0.145 | 0.152 | 0.133 | 0.139 | 0.883 | 0.024 |
| C_reference_difference | dummy_majority | 0.500 | 0.000 | 0.144 | 0.002 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| D_combined | logistic_regression | 1.000 | 0.000 | 1.000 | 0.000 | 0.997 | 0.006 | 0.985 | 0.034 | 1.000 | 0.000 | 0.994 | 0.012 |
| D_combined | decision_tree | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| D_combined | random_forest | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| D_combined | dummy_stratified | 0.508 | 0.082 | 0.165 | 0.036 | 0.508 | 0.082 | 0.145 | 0.152 | 0.133 | 0.139 | 0.883 | 0.024 |
| D_combined | dummy_majority | 0.500 | 0.000 | 0.144 | 0.002 | 0.500 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |

## Interpretation guardrails

- Positive class prevalence is low (30/209); metrics can be unstable fold-to-fold.
- Reference-difference predictors (`missing_transitions`, `extra_transitions`) are oracle-adjacent traceability counts and may admit near-separable splits in this frozen cohort — treat set **C** and **D** discrimination as descriptive, not causal.
- Gate-only set **A** shows limited discrimination above stratified baselines.
- Basic structural set **B** shows moderate out-of-fold signal without perfect separation.
