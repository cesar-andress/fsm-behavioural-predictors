"""
Shared reproducibility constants for all analysis scripts.

Single source of truth for random seeds and CV protocol parameters cited in the
manuscript (random_state=42; stratified five-fold CV). Bootstrap resampling is
not used; uncertainty is reported via fold-wise standard deviations only.
"""

from __future__ import annotations

RANDOM_STATE: int = 42
N_SPLITS: int = 5

# Random forest defaults (fixed; no hyperparameter search)
RF_N_ESTIMATORS: int = 50
RF_MAX_DEPTH: int = 5

# Decision tree defaults
DT_MAX_DEPTH: int = 3

# Logistic regression
LR_MAX_ITER: int = 2000
