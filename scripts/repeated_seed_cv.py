#!/usr/bin/env python3
"""Repeated-seed stratified CV with random forest (and stratified dummy)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from metrics_utils import METRIC_COLUMNS, classification_metrics, summarize_metric_columns  # noqa: E402
from model_behavioural_correctness import (  # noqa: E402
    PREDICTOR_SETS,
    load_scored_frame,
    make_model,
    prepare_features,
)
from repro_config import N_SPLITS, RANDOM_STATE, STRENGTHEN_CLASSIFIER, STRENGTHEN_SEEDS  # noqa: E402
from strengthen_io import (  # noqa: E402
    PREDICTOR_FAMILY_LABELS,
    TABLES_DIR,
    ensure_output_dirs,
    save_predictions,
    write_csv_md,
)


def make_model_for_seed(model_name: str, seed: int):
    model = make_model(model_name)
    if hasattr(model, "named_steps"):
        clf = model.named_steps.get("clf")
        if clf is not None and hasattr(clf, "random_state"):
            clf.set_params(random_state=seed)
    elif hasattr(model, "random_state"):
        model.set_params(random_state=seed)
    return model


def run_oof_for_seed(
    df: pd.DataFrame,
    features: list[str],
    *,
    seed: int,
    predictor_set: str,
    model_name: str,
) -> tuple[pd.DataFrame, dict[str, float]]:
    X = prepare_features(df, features)
    y = df["full_behavioural_pass"].astype(int)
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=seed)
    model = make_model_for_seed(model_name, seed)

    oof_score = np.full(len(df), np.nan)
    for train_idx, test_idx in cv.split(X, y):
        estimator = clone(model)
        estimator.fit(X.iloc[train_idx], y.iloc[train_idx])
        prob = estimator.predict_proba(X.iloc[test_idx])[:, 1]
        oof_score[test_idx] = prob

    pred_rows = pd.DataFrame(
        {
            "seed": seed,
            "predictor_set": predictor_set,
            "model": model_name,
            "row_index": df.index.to_numpy(),
            "system_id": df["system_id"].to_numpy(),
            "y_true": y.to_numpy(),
            "y_score": oof_score,
        }
    )
    metrics = classification_metrics(y.to_numpy(), oof_score)
    return pred_rows, metrics


def run_oof_dummy_for_seed(df: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, dict[str, float]]:
    X_dummy = pd.DataFrame({"_dummy": np.zeros(len(df))})
    y = df["full_behavioural_pass"].astype(int)
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=seed)
    model = make_model_for_seed("dummy_stratified", seed)
    oof_score = np.full(len(df), np.nan)
    for train_idx, test_idx in cv.split(X_dummy, y):
        estimator = clone(model)
        estimator.fit(X_dummy.iloc[train_idx], y.iloc[train_idx])
        prob = estimator.predict_proba(X_dummy.iloc[test_idx])[:, 1]
        oof_score[test_idx] = prob
    pred_rows = pd.DataFrame(
        {
            "seed": seed,
            "predictor_set": "dummy_stratified",
            "model": "dummy_stratified",
            "row_index": df.index.to_numpy(),
            "system_id": df["system_id"].to_numpy(),
            "y_true": y.to_numpy(),
            "y_score": oof_score,
        }
    )
    metrics = classification_metrics(y.to_numpy(), oof_score)
    return pred_rows, metrics


def run_loso_predictions(
    df: pd.DataFrame,
    features: list[str],
    *,
    predictor_set: str,
    model_name: str,
    seed: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    X_all = prepare_features(df, features)
    y_all = df["full_behavioural_pass"].astype(int)
    model = make_model_for_seed(model_name, seed)

    for held_out in sorted(df["system_id"].unique()):
        test_mask = df["system_id"] == held_out
        train_mask = ~test_mask
        X_train, y_train = X_all.loc[train_mask], y_all.loc[train_mask]
        X_test, y_test = X_all.loc[test_mask], y_all.loc[test_mask]

        if y_train.nunique() < 2:
            score = np.full(len(y_test), np.nan)
        else:
            fitted = clone(model)
            fitted.fit(X_train, y_train)
            score = fitted.predict_proba(X_test)[:, 1]

        test_df = df.loc[test_mask]
        for row_index, sys, yt, ys in zip(
            test_df.index, test_df["system_id"], y_test, score
        ):
            rows.append(
                {
                    "seed": seed,
                    "predictor_set": predictor_set,
                    "model": model_name,
                    "held_out_system": held_out,
                    "system_id": sys,
                    "row_index": row_index,
                    "y_true": int(yt),
                    "y_score": float(ys) if pd.notna(ys) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    ensure_output_dirs()
    df = load_scored_frame()

    predictor_configs: list[tuple[str, list[str], str]] = [
        (name, feats, STRENGTHEN_CLASSIFIER) for name, feats in PREDICTOR_SETS.items()
    ]

    oof_frames: list[pd.DataFrame] = []
    loso_frames: list[pd.DataFrame] = []
    seed_metric_rows: list[dict[str, Any]] = []

    for seed in STRENGTHEN_SEEDS:
        for predictor_set, features, model_name in predictor_configs:
            pred_rows, metrics = run_oof_for_seed(
                df,
                features,
                seed=seed,
                predictor_set=predictor_set,
                model_name=model_name,
            )
            oof_frames.append(pred_rows)
            seed_metric_rows.append(
                {
                    "seed": seed,
                    "predictor_set": predictor_set,
                    "model": model_name,
                    **metrics,
                }
            )

        dummy_rows, dummy_metrics = run_oof_dummy_for_seed(df, seed=seed)
        oof_frames.append(dummy_rows)
        seed_metric_rows.append(
            {
                "seed": seed,
                "predictor_set": "dummy_stratified",
                "model": "dummy_stratified",
                **dummy_metrics,
            }
        )

    oof_df = pd.concat(oof_frames, ignore_index=True)
    oof_path = save_predictions(oof_df, "repeated_seed_oof_predictions")

    for predictor_set, features, model_name in predictor_configs:
        loso_frames.append(
            run_loso_predictions(
                df,
                features,
                predictor_set=predictor_set,
                model_name=model_name,
                seed=RANDOM_STATE,
            )
        )

    loso_df = pd.concat(loso_frames, ignore_index=True)
    loso_path = save_predictions(loso_df, "repeated_seed_loso_predictions")

    seed_metrics_df = pd.DataFrame(seed_metric_rows)
    summary_rows: list[dict[str, Any]] = []
    for predictor_set, group in seed_metrics_df.groupby("predictor_set"):
        stats = summarize_metric_columns(group, METRIC_COLUMNS)
        summary_rows.append(
            {
                "predictor_set": predictor_set,
                "family_label": PREDICTOR_FAMILY_LABELS.get(predictor_set, predictor_set),
                "model": STRENGTHEN_CLASSIFIER
                if predictor_set != "dummy_stratified"
                else "dummy_stratified",
                **stats,
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    write_csv_md(
        summary_df,
        "repeated_seed_cv_summary",
        title="Repeated-seed pooled CV summary",
        intro=(
            f"Stratified {N_SPLITS}-fold CV over seeds "
            f"{STRENGTHEN_SEEDS[0]}–{STRENGTHEN_SEEDS[-1]}; "
            f"primary classifier `{STRENGTHEN_CLASSIFIER}`. "
            "Per-seed metrics computed on pooled out-of-fold predictions."
        ),
    )

    print(f"Wrote {oof_path}")
    print(f"Wrote {loso_path}")
    print(f"Wrote {TABLES_DIR / 'repeated_seed_cv_summary.csv'}")


if __name__ == "__main__":
    main()
