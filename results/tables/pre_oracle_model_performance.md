# Pre-oracle model performance

Exploratory stratified 5-fold cross-validation predicting `full_behavioural_pass` using **only pre-oracle signals** (behaviourally scored runs, n=209).

**Not confirmatory.** No causal claims. Target labels come from behavioural evaluation; predictors are restricted to gate outcomes, requirement coverage, and basic FSM counts available before reference-difference analysis.

## Allowed predictors

`g2_pass`, `g3_pass`, `g3a_pass`, `requirement_coverage`, `n_states`, `n_events`, `n_transitions`, `n_unreachable_states`

## Forbidden (excluded)

`missing_transitions`, `extra_transitions`, `behavioral_pass_rate`, and any oracle-derived or outcome-derived variable.

## Cross-validation protocol

- Stratified 5-fold CV (`shuffle=True`, `random_state=42`)
- Threshold: 0.5 on predicted positive-class probability
- Same model configurations as `model_behavioural_correctness.py`

## Pre-oracle results

| predictor_set | model | roc_auc_mean | roc_auc_std | pr_auc_mean | pr_auc_std | balanced_accuracy_mean | balanced_accuracy_std | f1_mean | f1_std | recall_full_pass_mean | recall_full_pass_std | specificity_non_full_pass_mean | specificity_non_full_pass_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pre_oracle | logistic_regression | 0.865 | 0.096 | 0.610 | 0.154 | 0.794 | 0.110 | 0.499 | 0.106 | 0.833 | 0.236 | 0.754 | 0.049 |
| pre_oracle | decision_tree | 0.952 | 0.024 | 0.718 | 0.110 | 0.875 | 0.077 | 0.654 | 0.082 | 0.900 | 0.224 | 0.849 | 0.107 |
| pre_oracle | random_forest | 0.983 | 0.011 | 0.897 | 0.040 | 0.958 | 0.014 | 0.803 | 0.054 | 1.000 | 0.000 | 0.916 | 0.028 |

## Comparison with prior predictor sets (random CV)

Baselines from `model_performance.md` (same CV protocol). Δ = pre-oracle ROC-AUC − baseline ROC-AUC (positive ⇒ pre-oracle higher).

| model | baseline_set | pre_oracle_roc_auc_mean | baseline_roc_auc_mean | delta_roc_auc | pre_oracle_pr_auc_mean | baseline_pr_auc_mean | delta_pr_auc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| logistic_regression | A_gate_only | 0.865 | 0.628 | 0.237 | 0.610 | 0.185 | 0.425 |
| logistic_regression | B_basic_structural | 0.865 | 0.747 | 0.118 | 0.610 | 0.429 | 0.181 |
| decision_tree | A_gate_only | 0.952 | 0.628 | 0.324 | 0.718 | 0.185 | 0.533 |
| decision_tree | B_basic_structural | 0.952 | 0.958 | -0.006 | 0.718 | 0.693 | 0.025 |
| random_forest | A_gate_only | 0.983 | 0.628 | 0.355 | 0.897 | 0.185 | 0.712 |
| random_forest | B_basic_structural | 0.983 | 0.982 | 0.001 | 0.897 | 0.894 | 0.003 |

## Is useful pre-oracle prediction possible?

Interpretation is **exploratory** and must not be overstated:

- Best pre-oracle configuration: **random_forest** (ROC-AUC 0.983 ± 0.011).
- Versus **A_gate_only** (0.628): pre-oracle adds requirement coverage and structural counts; discrimination improves (Δ = +0.355).
- Versus **B_basic_structural** (0.982): without oracle-adjacent traceability counts, out-of-fold discrimination is comparable (Δ = +0.001).
- **Gates alone** (set A) show limited discrimination; adding requirement coverage and FSM size/count features materially improves ranking over gates.
- Pre-oracle performance is **comparable to B_basic_structural** in random CV, indicating that strong out-of-fold signal does not require oracle traceability counts — but see LOSO results for cross-specification limits.
- Pre-oracle models may support **exploratory risk triage** (prioritising runs for behavioural review), not reliable pass/fail certification before oracle execution.
- Low positive-class prevalence (30/209) makes PR-AUC and F1 unstable; reported metrics describe this dataset only.

## Interpretation guardrails

- Exploratory screening study — not evidence of deployable pre-oracle guarantees.
- Structural counts correlate with specification and model identity; random CV mixes systems and is optimistic relative to leave-one-system-out.
- Do not infer that behavioural risk is *caused* by gate or size features.
