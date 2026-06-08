# Pre-oracle feature importance

Importance from models refit on the full scored analysis set (n=209). Tree models report `feature_importances_`; logistic regression reports |coefficient| after standardisation.

Predictor set: `pre_oracle` — `g2_pass`, `g3_pass`, `g3a_pass`, `requirement_coverage`, `n_states`, `n_events`, `n_transitions`, `n_unreachable_states`.

## pre_oracle — logistic_regression

| feature | importance | type |
| --- | --- | --- |
| g3_pass | 1.207 | abs_coefficient |
| g2_pass | 1.194 | abs_coefficient |
| n_states | 1.006 | abs_coefficient |
| requirement_coverage | 0.981 | abs_coefficient |
| g3a_pass | 0.667 | abs_coefficient |
| n_events | 0.409 | abs_coefficient |
| n_transitions | 0.141 | abs_coefficient |
| n_unreachable_states | 0.000 | abs_coefficient |

## pre_oracle — decision_tree

| feature | importance | type |
| --- | --- | --- |
| n_events | 0.390 | feature_importance |
| n_states | 0.371 | feature_importance |
| n_transitions | 0.177 | feature_importance |
| requirement_coverage | 0.062 | feature_importance |
| g3a_pass | 0.000 | feature_importance |
| g3_pass | 0.000 | feature_importance |
| g2_pass | 0.000 | feature_importance |
| n_unreachable_states | 0.000 | feature_importance |

## pre_oracle — random_forest

| feature | importance | type |
| --- | --- | --- |
| n_states | 0.288 | feature_importance |
| n_events | 0.250 | feature_importance |
| requirement_coverage | 0.241 | feature_importance |
| n_transitions | 0.098 | feature_importance |
| g2_pass | 0.050 | feature_importance |
| g3_pass | 0.041 | feature_importance |
| g3a_pass | 0.031 | feature_importance |
| n_unreachable_states | 0.000 | feature_importance |
