# Leave-one-model-out results

Per held-out `model` evaluation (train on 3 LLM families, test on 1). Behaviourally scored runs only; target `full_behavioural_pass`.

| predictor_set | model | held_out_model | n_train | n_test | n_test_positive | n_test_negative | roc_auc | pr_auc | balanced_accuracy | f1 | recall_full_pass | specificity_non_full_pass | fit_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_gate_only | logistic_regression | gemma2:9b | 154.000 | 55.000 | 10.000 | 45.000 | 0.567 | 0.204 | 0.567 | 0.339 | 1.000 | 0.133 |  |
| A_gate_only | logistic_regression | llama3.1:8b | 165.000 | 44.000 | 5.000 | 39.000 | 0.821 | 0.263 | 0.821 | 0.417 | 1.000 | 0.641 |  |
| A_gate_only | logistic_regression | mistral-nemo:12b | 154.000 | 55.000 | 10.000 | 45.000 | 0.611 | 0.222 | 0.611 | 0.364 | 1.000 | 0.222 |  |
| A_gate_only | logistic_regression | qwen2.5-coder:7b | 154.000 | 55.000 | 5.000 | 50.000 | 0.550 | 0.100 | 0.550 | 0.182 | 1.000 | 0.100 |  |
| A_gate_only | random_forest | gemma2:9b | 154.000 | 55.000 | 10.000 | 45.000 | 0.567 | 0.204 | 0.567 | 0.339 | 1.000 | 0.133 |  |
| A_gate_only | random_forest | llama3.1:8b | 165.000 | 44.000 | 5.000 | 39.000 | 0.821 | 0.263 | 0.821 | 0.417 | 1.000 | 0.641 |  |
| A_gate_only | random_forest | mistral-nemo:12b | 154.000 | 55.000 | 10.000 | 45.000 | 0.611 | 0.222 | 0.611 | 0.364 | 1.000 | 0.222 |  |
| A_gate_only | random_forest | qwen2.5-coder:7b | 154.000 | 55.000 | 5.000 | 50.000 | 0.550 | 0.100 | 0.550 | 0.182 | 1.000 | 0.100 |  |
| B_basic_structural | logistic_regression | gemma2:9b | 154.000 | 55.000 | 10.000 | 45.000 | 0.878 | 0.562 | 0.694 | 0.500 | 0.500 | 0.889 |  |
| B_basic_structural | logistic_regression | llama3.1:8b | 165.000 | 44.000 | 5.000 | 39.000 | 0.744 | 0.333 | 0.744 | 0.333 | 1.000 | 0.487 |  |
| B_basic_structural | logistic_regression | mistral-nemo:12b | 154.000 | 55.000 | 10.000 | 45.000 | 0.556 | 0.361 | 0.483 | 0.256 | 0.500 | 0.467 |  |
| B_basic_structural | logistic_regression | qwen2.5-coder:7b | 154.000 | 55.000 | 5.000 | 50.000 | 0.900 | 0.500 | 0.850 | 0.400 | 1.000 | 0.700 |  |
| B_basic_structural | random_forest | gemma2:9b | 154.000 | 55.000 | 10.000 | 45.000 | 0.633 | 0.591 | 0.694 | 0.500 | 0.500 | 0.889 |  |
| B_basic_structural | random_forest | llama3.1:8b | 165.000 | 44.000 | 5.000 | 39.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| B_basic_structural | random_forest | mistral-nemo:12b | 154.000 | 55.000 | 10.000 | 45.000 | 0.528 | 0.258 | 0.639 | 0.400 | 0.500 | 0.778 |  |
| B_basic_structural | random_forest | qwen2.5-coder:7b | 154.000 | 55.000 | 5.000 | 50.000 | 1.000 | 1.000 | 0.950 | 0.667 | 1.000 | 0.900 |  |
| D_combined | logistic_regression | gemma2:9b | 154.000 | 55.000 | 10.000 | 45.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| D_combined | logistic_regression | llama3.1:8b | 165.000 | 44.000 | 5.000 | 39.000 | 1.000 | 1.000 | 0.936 | 0.667 | 1.000 | 0.872 |  |
| D_combined | logistic_regression | mistral-nemo:12b | 154.000 | 55.000 | 10.000 | 45.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| D_combined | logistic_regression | qwen2.5-coder:7b | 154.000 | 55.000 | 5.000 | 50.000 | 1.000 | 1.000 | 0.900 | 0.500 | 1.000 | 0.800 |  |
| D_combined | random_forest | gemma2:9b | 154.000 | 55.000 | 10.000 | 45.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| D_combined | random_forest | llama3.1:8b | 165.000 | 44.000 | 5.000 | 39.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |  |
| D_combined | random_forest | mistral-nemo:12b | 154.000 | 55.000 | 10.000 | 45.000 | 1.000 | 1.000 | 0.750 | 0.667 | 0.500 | 1.000 |  |
| D_combined | random_forest | qwen2.5-coder:7b | 154.000 | 55.000 | 5.000 | 50.000 | 1.000 | 1.000 | 0.950 | 0.667 | 1.000 | 0.900 |  |

## Notes

- `roc_auc` / `pr_auc` are undefined when the held-out model fold has only one target class.
- Four Ollama models: `gemma2:9b`, `llama3.1:8b`, `mistral-nemo:12b`, `qwen2.5-coder:7b`.
