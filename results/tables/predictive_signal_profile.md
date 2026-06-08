# Predictive signal profile

First-pass association between candidate structural predictors and behavioural outcomes.
**Analysis set:** behaviourally scored runs only (n=209).

Conservative descriptive associations only — **no hypothesis tests reported** (p-values shown for transparency; not used for confirmatory claims).

## Binary predictors

Point-biserial correlation with `behavioral_pass_rate` and `full_behavioural_pass`; group mean BPR and full-pass rate differences (true − false).

| predictor | n_complete | missingness | mean_bpr_true | mean_bpr_false | mean_bpr_diff | full_pass_rate_true | full_pass_rate_false | full_pass_rate_diff | point_biserial_bpr | point_biserial_full_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| g2_pass | 209 | 0 | 0.489 | 0.469 | 0.021 | 0.159 | 0.000 | 0.159 | 0.022 | 0.133 |
| g3_pass | 209 | 0 | 0.488 | 0.480 | 0.009 | 0.164 | 0.000 | 0.164 | 0.011 | 0.154 |
| g3a_pass | 209 | 0 | 0.499 | 0.386 | 0.113 | 0.160 | 0.000 | 0.160 | 0.125 | 0.137 |

## Numeric predictors

Spearman rank correlation with `behavioral_pass_rate` and `full_behavioural_pass`.

| predictor | n_complete | missingness | mean_bpr | median_bpr | full_pass_rate | spearman_bpr | spearman_full_pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| requirement_coverage | 209 | 0 | 0.487 | 0.353 | 0.144 | 0.102 | 0.186 |
| n_states | 209 | 0 | 0.487 | 0.353 | 0.144 | -0.473 | -0.306 |
| n_events | 209 | 0 | 0.487 | 0.353 | 0.144 | -0.081 | 0.061 |
| n_transitions | 209 | 0 | 0.487 | 0.353 | 0.144 | -0.073 | 0.105 |
| n_unreachable_states | 209 | 0 | 0.487 | 0.353 | 0.144 | nan | nan |
| missing_transitions | 209 | 0 | 0.487 | 0.353 | 0.144 | -0.858 | -0.586 |
| extra_transitions | 209 | 0 | 0.487 | 0.353 | 0.144 | -0.799 | -0.613 |

## Interpretation guardrails

- Associations describe frozen-data patterns only; causality is not implied.
- Several predictors are structurally related (e.g., G2–G3a gates); multicollinearity will be addressed in later modelling stages.
- Non-scored runs are excluded from this profile by design.
