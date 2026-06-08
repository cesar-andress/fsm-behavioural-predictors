"""
Shared reproducibility constants for all analysis scripts.

Single source of truth for random seeds and CV protocol parameters cited in the
manuscript (random_state=42; stratified five-fold CV). Bootstrap resampling is
not used; uncertainty is reported via fold-wise standard deviations only.
"""

from __future__ import annotations

RANDOM_STATE: int = 42
N_SPLITS: int = 5

# Single-threaded sklearn fits avoid order-dependent floating-point drift across platforms.
SKLEARN_N_JOBS: int = 1

# Random forest defaults (fixed; no hyperparameter search)
RF_N_ESTIMATORS: int = 50
RF_MAX_DEPTH: int = 5

# Decision tree defaults
DT_MAX_DEPTH: int = 3

# Logistic regression
LR_MAX_ITER: int = 2000


def apply_reproducibility() -> None:
    """Seed NumPy's global RNG before stochastic modelling steps."""
    import numpy as np

    np.random.seed(RANDOM_STATE)
