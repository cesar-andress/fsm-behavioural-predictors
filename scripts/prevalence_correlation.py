#!/usr/bin/env python3
"""Spearman correlation between Family B OOF scores and training-fold system prevalence."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.model_selection import StratifiedKFold

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from metrics_utils import summarize_values  # noqa: E402
from model_behavioural_correctness import load_scored_frame  # noqa: E402
from repro_config import N_SPLITS, STRENGTHEN_SEEDS  # noqa: E402
from strengthen_io import TABLES_DIR, load_predictions, write_csv_md  # noqa: E402

FAMILY_B = "B_basic_structural"


def training_fold_system_prevalence(train_df: pd.DataFrame, test_df: pd.DataFrame) -> np.ndarray:
    global_prev = float(train_df["full_behavioural_pass"].mean())
    system_prev = train_df.groupby("system_id")["full_behavioural_pass"].mean()
    return np.array(
        [float(system_prev.get(sys, global_prev)) for sys in test_df["system_id"]],
        dtype=float,
    )


def compute_seed_correlations(df: pd.DataFrame, oof_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    family_oof = oof_df[oof_df["predictor_set"] == FAMILY_B]

    for seed in STRENGTHEN_SEEDS:
        seed_oof = family_oof[family_oof["seed"] == seed].set_index("row_index")
        y = df["full_behavioural_pass"].astype(int)
        cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=seed)
        prev_signal = np.full(len(df), np.nan)

        for train_idx, test_idx in cv.split(df, y):
            train_df = df.iloc[train_idx]
            test_df = df.iloc[test_idx]
            prev_signal[test_idx] = training_fold_system_prevalence(train_df, test_df)

        aligned = seed_oof.reindex(df.index)
        mask = aligned["y_score"].notna() & ~np.isnan(prev_signal)
        if mask.sum() < 2:
            rho = float("nan")
        else:
            rho, _ = spearmanr(aligned.loc[mask, "y_score"], prev_signal[mask])
            rho = float(rho)

        rows.append({"seed": seed, "spearman_rho": rho})

    return pd.DataFrame(rows)


def main() -> None:
    df = load_scored_frame()
    oof_df = load_predictions("repeated_seed_oof_predictions")
    corr_df = compute_seed_correlations(df, oof_df)
    stats = summarize_values(corr_df["spearman_rho"])
    summary_df = pd.DataFrame(
        [
            {
                "predictor_set": FAMILY_B,
                "comparison": "Family B RF OOF score vs training-fold system prevalence",
                **stats,
            }
        ]
    )
    write_csv_md(
        summary_df,
        "prevalence_correlation",
        title="Family B vs system-prevalence Spearman correlation",
        intro=(
            f"Per-seed Spearman ρ between Family B random-forest out-of-fold scores "
            f"and fold-contained system prevalence signals (seeds {STRENGTHEN_SEEDS[0]}–"
            f"{STRENGTHEN_SEEDS[-1]})."
        ),
    )
    corr_df.to_csv(TABLES_DIR / "prevalence_correlation_by_seed.csv", index=False)
    print(f"Wrote {TABLES_DIR / 'prevalence_correlation.csv'}")


if __name__ == "__main__":
    main()
