# Model validation notes

## Analysis set

- Rows: **209** (behaviourally scored runs only)
- Target: `full_behavioural_pass`
- Positive class (full pass): **30** (14.4%)
- Negative class: **179** (85.6%)

## Cross-validation

- Method: stratified 5-fold CV (`shuffle=True`, `random_state=42`)
- Threshold: 0.5 on predicted positive-class probability
- No model or system identifiers used as predictors
- Preprocessing fit inside each training fold only (pipelines)

## Missingness before imputation (scored runs)

### Predictor set `A_gate_only` — total missing cells: 0

| feature | missing_count | missing_rate |
| --- | --- | --- |
| g2_pass | 0 | 0.000 |
| g3_pass | 0 | 0.000 |
| g3a_pass | 0 | 0.000 |

### Predictor set `B_basic_structural` — total missing cells: 0

| feature | missing_count | missing_rate |
| --- | --- | --- |
| n_states | 0 | 0.000 |
| n_events | 0 | 0.000 |
| n_transitions | 0 | 0.000 |
| n_unreachable_states | 0 | 0.000 |

### Predictor set `C_reference_difference` — total missing cells: 0

| feature | missing_count | missing_rate |
| --- | --- | --- |
| missing_transitions | 0 | 0.000 |
| extra_transitions | 0 | 0.000 |

### Predictor set `D_combined` — total missing cells: 0

| feature | missing_count | missing_rate |
| --- | --- | --- |
| g2_pass | 0 | 0.000 |
| g3_pass | 0 | 0.000 |
| g3a_pass | 0 | 0.000 |
| n_states | 0 | 0.000 |
| n_events | 0 | 0.000 |
| n_transitions | 0 | 0.000 |
| n_unreachable_states | 0 | 0.000 |
| missing_transitions | 0 | 0.000 |
| extra_transitions | 0 | 0.000 |
| requirement_coverage | 0 | 0.000 |

## Leakage controls

- Target derived from `behavioral_pass_rate` but predictors are structural only.
- Median imputation and scaling applied within CV training folds when used.
- No test-fold information used for feature selection.
