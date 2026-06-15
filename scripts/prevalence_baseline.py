#!/usr/bin/env python3
"""Prevalence-only baseline under repeated-seed CV and LOSO."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from metrics_utils import METRIC_COLUMNS, classification_metrics, summarize_metric_columns  # noqa: E402
from model_behavioural_correctness import load_scored_frame  # noqa: E402
from repro_config import N_SPLITS, RANDOM_STATE, STRENGTHEN_SEEDS  # noqa: E402
from strengthen_io import (  # noqa: E402
    TABLES_DIR,
    ensure_output_dirs,
    save_predictions,
    write_csv_md,
)

PREDICTOR_SET = "prevalence_only"


def score_from_prevalence(
    test_df: pd.DataFrame,
    train_df: pd.DataFrame,
) -> np.ndarray:
    global_prev = float(train_df["full_behavioural_pass"].mean())
    system_prev = train_df.groupby("system_id")["full_behavioural_pass"].mean()
    scores = []
    for sys in test_df["system_id"]:
        scores.append(float(system_prev.get(sys, global_prev)))
    return np.asarray(scores, dtype=float)


def run_cv_seed(df: pd.DataFrame, seed: int) -> tuple[pd.DataFrame, dict[str, float]]:
    y = df["full_behavioural_pass"].astype(int)
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=seed)
    oof_score = np.full(len(df), np.nan)

    for train_idx, test_idx in cv.split(df, y):
        train_df = df.iloc[train_idx]
        test_df = df.iloc[test_idx]
        oof_score[test_idx] = score_from_prevalence(test_df, train_df)

    pred_rows = pd.DataFrame(
        {
            "seed": seed,
            "predictor_set": PREDICTOR_SET,
            "row_index": df.index.to_numpy(),
            "system_id": df["system_id"].to_numpy(),
            "y_true": y.to_numpy(),
            "y_score": oof_score,
        }
    )
    metrics = classification_metrics(y.to_numpy(), oof_score)
    return pred_rows, metrics


def run_loso(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    per_system_rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []

    for held_out in sorted(df["system_id"].unique()):
        test_mask = df["system_id"] == held_out
        train_mask = ~test_mask
        train_df = df.loc[train_mask]
        test_df = df.loc[test_mask]
        y_test = test_df["full_behavioural_pass"].astype(int)
        scores = np.full(len(test_df), float(train_df["full_behavioural_pass"].mean()))

        for row_index, sys, yt, ys in zip(
            test_df.index, test_df["system_id"], y_test, scores
        ):
            pred_rows.append(
                {
                    "predictor_set": PREDICTOR_SET,
                    "held_out_system": held_out,
                    "system_id": sys,
                    "row_index": row_index,
                    "y_true": int(yt),
                    "y_score": float(ys),
                }
            )

        metrics = classification_metrics(y_test.to_numpy(), scores)
        per_system_rows.append(
            {
                "held_out_system": held_out,
                "n_test": len(test_df),
                "n_positive": int(y_test.sum()),
                "n_negative": int((1 - y_test).sum()),
                "global_train_prevalence": float(train_df["full_behavioural_pass"].mean()),
                **metrics,
            }
        )

    return pd.DataFrame(pred_rows), pd.DataFrame(per_system_rows)


def main() -> None:
    ensure_output_dirs()
    df = load_scored_frame()

    cv_pred_frames: list[pd.DataFrame] = []
    cv_metric_rows: list[dict[str, Any]] = []
    for seed in STRENGTHEN_SEEDS:
        pred_rows, metrics = run_cv_seed(df, seed)
        cv_pred_frames.append(pred_rows)
        cv_metric_rows.append({"seed": seed, **metrics})

    cv_pred_df = pd.concat(cv_pred_frames, ignore_index=True)
    cv_pred_path = save_predictions(cv_pred_df, "prevalence_baseline_cv_predictions")

    cv_metrics_df = pd.DataFrame(cv_metric_rows)
    cv_summary = pd.DataFrame(
        [{"predictor_set": PREDICTOR_SET, **summarize_metric_columns(cv_metrics_df)}]
    )
    write_csv_md(
        cv_summary,
        "prevalence_baseline_cv",
        title="Prevalence-only baseline — pooled CV (100 seeds)",
        intro=(
            "Each test row scored by its system's training-fold prevalence; "
            "falls back to global training prevalence when the system is absent."
        ),
    )

    loso_pred_df, loso_system_df = run_loso(df)
    loso_pred_path = save_predictions(loso_pred_df, "prevalence_baseline_loso_predictions")

    definable = loso_system_df[loso_system_df["roc_auc"].notna()]
    loso_summary = pd.DataFrame(
        [
            {
                "predictor_set": PREDICTOR_SET,
                "loso_roc_auc_mean_definable_folds": float(
                    definable["roc_auc"].mean(skipna=True)
                )
                if len(definable)
                else float("nan"),
                "n_definable_folds": int(definable["roc_auc"].notna().sum()),
                "n_systems": len(loso_system_df),
                "pooled_loso_roc_auc": classification_metrics(
                    loso_pred_df["y_true"].to_numpy(),
                    loso_pred_df["y_score"].to_numpy(),
                )["roc_auc"],
            }
        ]
    )

    write_csv_md(
        loso_system_df,
        "prevalence_baseline_loso",
        title="Prevalence-only baseline — LOSO by held-out system",
        intro=(
            "Held-out rows scored with global training prevalence only "
            f"(seed={RANDOM_STATE} not used; deterministic scoring)."
        ),
    )
    loso_summary.to_csv(TABLES_DIR / "prevalence_baseline_loso_summary.csv", index=False)

    print(f"Wrote {cv_pred_path}")
    print(f"Wrote {loso_pred_path}")
    print(f"Wrote {TABLES_DIR / 'prevalence_baseline_cv.csv'}")


if __name__ == "__main__":
    main()
