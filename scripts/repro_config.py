"""
Shared reproducibility constants for all analysis scripts.

Single source of truth for random seeds and CV protocol parameters cited in the
manuscript (random_state=42; stratified five-fold CV). Bootstrap resampling is
not used in the published replication pipeline; strengthened-stats outputs use
separate seed lists and cluster bootstrap settings below.
"""

from __future__ import annotations

RANDOM_STATE: int = 42
N_SPLITS: int = 5

# Strengthened-stats layer (outputs/ only; does not alter results/)
STRENGTHEN_SEEDS: list[int] = list(range(100))
N_BOOTSTRAP_ITERATIONS: int = 5000
STRENGTHEN_CLASSIFIER: str = "random_forest"
STRENGTHEN_AGGREGATION_RULE: str = (
    "RF-only; CV/LOSO pooled ROC-AUC on resampled rows for bootstrap; "
    "LOSO summary μ = mean of definable per-system fold AUCs (skipna); "
    "CV summary = distribution across 100 seeds of pooled OOF ROC-AUC"
)

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
