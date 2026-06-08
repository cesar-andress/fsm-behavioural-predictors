# Model feature importance

Importance from models refit on the full scored analysis set (n=209). Tree models report `feature_importances_`; logistic regression reports |coefficient| after standardisation.

## A_gate_only — logistic_regression

| feature | importance | type |
| --- | --- | --- |
| g2_pass | 1.122 | abs_coefficient |
| g3_pass | 0.996 | abs_coefficient |
| g3a_pass | 0.499 | abs_coefficient |

## A_gate_only — decision_tree

| feature | importance | type |
| --- | --- | --- |
| g3_pass | 0.531 | feature_importance |
| g2_pass | 0.469 | feature_importance |
| g3a_pass | 0.000 | feature_importance |

## A_gate_only — random_forest

| feature | importance | type |
| --- | --- | --- |
| g2_pass | 0.445 | feature_importance |
| g3_pass | 0.332 | feature_importance |
| g3a_pass | 0.223 | feature_importance |

## B_basic_structural — logistic_regression

| feature | importance | type |
| --- | --- | --- |
| n_states | 1.039 | abs_coefficient |
| n_transitions | 0.347 | abs_coefficient |
| n_events | 0.307 | abs_coefficient |
| n_unreachable_states | 0.000 | abs_coefficient |

## B_basic_structural — decision_tree

| feature | importance | type |
| --- | --- | --- |
| n_states | 0.433 | feature_importance |
| n_events | 0.390 | feature_importance |
| n_transitions | 0.177 | feature_importance |
| n_unreachable_states | 0.000 | feature_importance |

## B_basic_structural — random_forest

| feature | importance | type |
| --- | --- | --- |
| n_states | 0.398 | feature_importance |
| n_events | 0.355 | feature_importance |
| n_transitions | 0.246 | feature_importance |
| n_unreachable_states | 0.000 | feature_importance |

## C_reference_difference — logistic_regression

| feature | importance | type |
| --- | --- | --- |
| extra_transitions | 3.591 | abs_coefficient |
| missing_transitions | 2.264 | abs_coefficient |

## C_reference_difference — decision_tree

| feature | importance | type |
| --- | --- | --- |
| extra_transitions | 0.946 | feature_importance |
| missing_transitions | 0.054 | feature_importance |

## C_reference_difference — random_forest

| feature | importance | type |
| --- | --- | --- |
| missing_transitions | 0.519 | feature_importance |
| extra_transitions | 0.481 | feature_importance |

## D_combined — logistic_regression

| feature | importance | type |
| --- | --- | --- |
| extra_transitions | 2.916 | abs_coefficient |
| missing_transitions | 2.148 | abs_coefficient |
| g3_pass | 1.219 | abs_coefficient |
| g2_pass | 1.059 | abs_coefficient |
| requirement_coverage | 0.798 | abs_coefficient |
| n_states | 0.522 | abs_coefficient |
| n_transitions | 0.250 | abs_coefficient |
| n_events | 0.102 | abs_coefficient |
| g3a_pass | 0.053 | abs_coefficient |
| n_unreachable_states | 0.000 | abs_coefficient |

## D_combined — decision_tree

| feature | importance | type |
| --- | --- | --- |
| extra_transitions | 0.946 | feature_importance |
| missing_transitions | 0.054 | feature_importance |
| n_states | 0.000 | feature_importance |
| g2_pass | 0.000 | feature_importance |
| g3_pass | 0.000 | feature_importance |
| g3a_pass | 0.000 | feature_importance |
| n_transitions | 0.000 | feature_importance |
| n_events | 0.000 | feature_importance |
| n_unreachable_states | 0.000 | feature_importance |
| requirement_coverage | 0.000 | feature_importance |

## D_combined — random_forest

| feature | importance | type |
| --- | --- | --- |
| extra_transitions | 0.430 | feature_importance |
| missing_transitions | 0.394 | feature_importance |
| n_states | 0.071 | feature_importance |
| n_events | 0.055 | feature_importance |
| requirement_coverage | 0.024 | feature_importance |
| n_transitions | 0.012 | feature_importance |
| g2_pass | 0.006 | feature_importance |
| g3_pass | 0.006 | feature_importance |
| g3a_pass | 0.001 | feature_importance |
| n_unreachable_states | 0.000 | feature_importance |
