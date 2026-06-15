#!/usr/bin/env python3
"""Cluster bootstrap of CV–LOSO optimism gap (Δ) by system_id."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from metrics_utils import roc_auc_safe, summarize_values  # noqa: E402
from model_behavioural_correctness import PREDICTOR_SETS  # noqa: E402
from repro_config import (  # noqa: E402
    N_BOOTSTRAP_ITERATIONS,
    RANDOM_STATE,
    STRENGTHEN_CLASSIFIER,
    STRENGTHEN_SEEDS,
)
from strengthen_io import (  # noqa: E402
    PREDICTOR_FAMILY_LABELS,
    STATS_DIR,
    TABLES_DIR,
    ensure_output_dirs,
    load_predictions,
    write_csv_md,
)


def per_system_fold_auc(loso_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for held_out, group in loso_df.groupby("held_out_system"):
        y = group["y_true"].to_numpy()
        s = group["y_score"].to_numpy()
        rows.append(
            {
                "held_out_system": held_out,
                "roc_auc": roc_auc_safe(y, s),
                "n_rows": len(group),
            }
        )
    return pd.DataFrame(rows)


def bootstrap_delta_for_family(
    cv_pool_df: pd.DataFrame,
    loso_df: pd.DataFrame,
    predictor_set: str,
    *,
    cv_mean_across_seeds: float,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    systems = sorted(cv_pool_df["system_id"].unique())
    fold_auc = per_system_fold_auc(loso_df)
    loso_mean_definable = float(fold_auc["roc_auc"].mean(skipna=True))
    ndc = int(fold_auc["roc_auc"].notna().sum())

    boot_rows: list[dict[str, Any]] = []
    for iteration in range(N_BOOTSTRAP_ITERATIONS):
        sampled = rng.choice(systems, size=len(systems), replace=True)
        cv_parts = [cv_pool_df[cv_pool_df["system_id"] == sys] for sys in sampled]
        loso_parts = [
            loso_df[(loso_df["held_out_system"] == sys) & (loso_df["system_id"] == sys)]
            for sys in sampled
        ]
        cv_pool = pd.concat(cv_parts, ignore_index=True) if cv_parts else pd.DataFrame()
        loso_pool = pd.concat(loso_parts, ignore_index=True) if loso_parts else pd.DataFrame()

        cv_auc = (
            roc_auc_safe(cv_pool["y_true"].to_numpy(), cv_pool["y_score"].to_numpy())
            if len(cv_pool)
            else float("nan")
        )
        loso_auc = (
            roc_auc_safe(loso_pool["y_true"].to_numpy(), loso_pool["y_score"].to_numpy())
            if len(loso_pool)
            else float("nan")
        )
        delta = cv_auc - loso_auc if pd.notna(cv_auc) and pd.notna(loso_auc) else float("nan")

        boot_rows.append(
            {
                "iteration": iteration,
                "predictor_set": predictor_set,
                "cv_roc_auc": cv_auc,
                "loso_roc_auc": loso_auc,
                "delta": delta,
            }
        )

    boot_df = pd.DataFrame(boot_rows)
    delta_stats = summarize_values(boot_df["delta"])
    n_valid = int(boot_df["delta"].notna().sum())
    meta = {
        "predictor_set": predictor_set,
        "family_label": PREDICTOR_FAMILY_LABELS.get(predictor_set, predictor_set),
        "cv_roc_auc_mean_across_seeds": float(cv_mean_across_seeds),
        "loso_roc_auc_mean_definable_folds": loso_mean_definable,
        "ndc": ndc,
        "n_systems": len(systems),
        "delta_point_estimate": float(cv_mean_across_seeds - loso_mean_definable)
        if pd.notna(cv_mean_across_seeds) and pd.notna(loso_mean_definable)
        else float("nan"),
        "delta_median_bootstrap": delta_stats["median"],
        "delta_p025": delta_stats["p025"],
        "delta_p975": delta_stats["p975"],
        "n_valid_bootstrap_iterations": n_valid,
        "n_bootstrap_iterations": N_BOOTSTRAP_ITERATIONS,
        "bootstrap_definability_rate": n_valid / N_BOOTSTRAP_ITERATIONS,
    }
    return boot_df, meta


def mean_oof_by_row(oof_df: pd.DataFrame, predictor_set: str, model: str) -> pd.DataFrame:
    sub = oof_df[(oof_df["predictor_set"] == predictor_set) & (oof_df["model"] == model)]
    return (
        sub.groupby(["row_index", "system_id", "y_true"], as_index=False)["y_score"]
        .mean()
        .assign(predictor_set=predictor_set, model=model)
    )


def main() -> None:
    ensure_output_dirs()
    oof_df = load_predictions("repeated_seed_oof_predictions")
    loso_df = load_predictions("repeated_seed_loso_predictions")
    prev_cv = load_predictions("prevalence_baseline_cv_predictions")
    prev_loso = load_predictions("prevalence_baseline_loso_predictions")

    rng = np.random.default_rng(RANDOM_STATE)
    families = list(PREDICTOR_SETS.keys()) + ["prevalence_only"]

    all_boot: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []

    cv_summary = pd.read_csv(TABLES_DIR / "repeated_seed_cv_summary.csv")

    for predictor_set in families:
        if predictor_set == "prevalence_only":
            cv_pool = (
                prev_cv.groupby(["row_index", "system_id", "y_true"], as_index=False)["y_score"]
                .mean()
                .assign(predictor_set=predictor_set)
            )
            family_loso = prev_loso.copy()
            cv_mean = float(
                pd.read_csv(TABLES_DIR / "prevalence_baseline_cv.csv").iloc[0]["roc_auc_mean"]
            )
        else:
            cv_pool = mean_oof_by_row(oof_df, predictor_set, STRENGTHEN_CLASSIFIER)
            family_loso = loso_df[
                (loso_df["predictor_set"] == predictor_set)
                & (loso_df["model"] == STRENGTHEN_CLASSIFIER)
            ]
            match = cv_summary[cv_summary["predictor_set"] == predictor_set]
            cv_mean = float(match.iloc[0]["roc_auc_mean"]) if len(match) else float("nan")

        boot_df, meta = bootstrap_delta_for_family(
            cv_pool,
            family_loso,
            predictor_set,
            cv_mean_across_seeds=cv_mean,
            rng=rng,
        )
        all_boot.append(boot_df)
        summary_rows.append(meta)

    boot_all = pd.concat(all_boot, ignore_index=True)
    summary_df = pd.DataFrame(summary_rows)

    write_csv_md(
        summary_df,
        "bootstrap_delta",
        title="Cluster bootstrap of CV − LOSO Δ by system_id",
        intro=(
            f"{N_BOOTSTRAP_ITERATIONS} bootstrap iterations; resampling unit = system_id; "
            "pooled ROC-AUC on resampled rows; NaN retained when LOSO undefined."
        ),
    )
    boot_all.to_csv(TABLES_DIR / "bootstrap_delta_iterations.csv", index=False)

    json_path = STATS_DIR / "bootstrap_delta.json"
    json_path.write_text(
        json.dumps(
            {
                "n_bootstrap_iterations": N_BOOTSTRAP_ITERATIONS,
                "random_state": RANDOM_STATE,
                "classifier": STRENGTHEN_CLASSIFIER,
                "families": summary_rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {TABLES_DIR / 'bootstrap_delta.csv'}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
