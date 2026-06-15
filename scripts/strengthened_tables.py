#!/usr/bin/env python3
"""Strengthened summary tables (Table 5 / Table 6 equivalents)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from metrics_utils import format_interval, roc_auc_safe  # noqa: E402
from model_behavioural_correctness import PREDICTOR_SETS  # noqa: E402
from repro_config import STRENGTHEN_CLASSIFIER  # noqa: E402
from strengthen_io import (  # noqa: E402
    PREDICTOR_FAMILY_LABELS,
    TABLES_DIR,
    load_predictions,
    write_csv_md,
)

METRICS = ["roc_auc", "pr_auc", "balanced_accuracy", "f1", "mcc"]


def load_cv_summary() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "repeated_seed_cv_summary.csv")


def load_bootstrap_summary() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "bootstrap_delta.csv")


def load_prevalence_cv() -> pd.DataFrame:
    return pd.read_csv(TABLES_DIR / "prevalence_baseline_cv.csv")


def loso_stats_for_family(loso_df: pd.DataFrame, predictor_set: str) -> dict:
    if predictor_set == "prevalence_only":
        sub = loso_df
        fold_df = (
            sub.groupby("held_out_system")
            .apply(
                lambda g: roc_auc_safe(g["y_true"].to_numpy(), g["y_score"].to_numpy()),
                include_groups=False,
            )
            .reset_index(name="roc_auc")
        )
    else:
        sub = loso_df[
            (loso_df["predictor_set"] == predictor_set)
            & (loso_df["model"] == STRENGTHEN_CLASSIFIER)
        ]
        fold_df = (
            sub.groupby("held_out_system")
            .apply(
                lambda g: roc_auc_safe(g["y_true"].to_numpy(), g["y_score"].to_numpy()),
                include_groups=False,
            )
            .reset_index(name="roc_auc")
        )

    definable = fold_df["roc_auc"].notna()
    return {
        "loso_roc_auc": float(fold_df.loc[definable, "roc_auc"].mean(skipna=True))
        if definable.any()
        else float("nan"),
        "ndc": f"{int(definable.sum())}/{len(fold_df)}",
    }


def build_table5(cv_summary: pd.DataFrame, prev_cv: pd.DataFrame) -> pd.DataFrame:
    order = list(PREDICTOR_SETS.keys()) + ["dummy_stratified", "prevalence_only"]
    rows: list[dict] = []

    for predictor_set in order:
        if predictor_set == "prevalence_only":
            src = prev_cv.iloc[0]
            label = PREDICTOR_FAMILY_LABELS["prevalence_only"]
        else:
            match = cv_summary[cv_summary["predictor_set"] == predictor_set]
            if match.empty:
                continue
            src = match.iloc[0]
            label = PREDICTOR_FAMILY_LABELS.get(predictor_set, predictor_set)

        row: dict = {
            "predictor_family": label,
            "classifier": "dummy_stratified"
            if predictor_set == "dummy_stratified"
            else ("prevalence_only" if predictor_set == "prevalence_only" else STRENGTHEN_CLASSIFIER),
        }
        for metric in METRICS:
            mean = src.get(f"{metric}_mean", np.nan)
            p025 = src.get(f"{metric}_p025", np.nan)
            p975 = src.get(f"{metric}_p975", np.nan)
            row[f"{metric}_mean"] = mean
            row[f"{metric}_interval"] = format_interval(mean, p025, p975)
        rows.append(row)

    return pd.DataFrame(rows)


def build_table6(
    cv_summary: pd.DataFrame,
    bootstrap: pd.DataFrame,
    loso_df: pd.DataFrame,
    prev_loso_summary: pd.DataFrame | None,
) -> pd.DataFrame:
    families = list(PREDICTOR_SETS.keys()) + ["prevalence_only"]
    rows: list[dict] = []

    for predictor_set in families:
        label = PREDICTOR_FAMILY_LABELS.get(predictor_set, predictor_set)
        if predictor_set == "prevalence_only":
            cv_row = pd.read_csv(TABLES_DIR / "prevalence_baseline_cv.csv").iloc[0]
            cv_mean = cv_row.get("roc_auc_mean", np.nan)
            cv_interval = format_interval(
                cv_row.get("roc_auc_mean", np.nan),
                cv_row.get("roc_auc_p025", np.nan),
                cv_row.get("roc_auc_p975", np.nan),
            )
            loso_info = loso_stats_for_family(
                load_predictions("prevalence_baseline_loso_predictions"),
                "prevalence_only",
            )
            boot_row = bootstrap[bootstrap["predictor_set"] == "prevalence_only"]
        else:
            cv_match = cv_summary[cv_summary["predictor_set"] == predictor_set]
            if cv_match.empty:
                continue
            cv_row = cv_match.iloc[0]
            cv_mean = cv_row.get("roc_auc_mean", np.nan)
            cv_interval = format_interval(
                cv_row.get("roc_auc_mean", np.nan),
                cv_row.get("roc_auc_p025", np.nan),
                cv_row.get("roc_auc_p975", np.nan),
            )
            loso_info = loso_stats_for_family(loso_df, predictor_set)
            boot_row = bootstrap[bootstrap["predictor_set"] == predictor_set]

        loso_auc = loso_info["loso_roc_auc"]
        delta = cv_mean - loso_auc if pd.notna(cv_mean) and pd.notna(loso_auc) else np.nan

        if not boot_row.empty:
            br = boot_row.iloc[0]
            delta_interval = format_interval(
                br.get("delta_median_bootstrap", np.nan),
                br.get("delta_p025", np.nan),
                br.get("delta_p975", np.nan),
            )
            definability_rate = br.get("bootstrap_definability_rate", np.nan)
        else:
            delta_interval = "n/a"
            definability_rate = np.nan

        rows.append(
            {
                "predictor_family": label,
                "classifier": STRENGTHEN_CLASSIFIER
                if predictor_set != "prevalence_only"
                else "prevalence_only",
                "cv_roc_auc_mean": cv_mean,
                "cv_roc_auc_interval": cv_interval,
                "loso_roc_auc": loso_auc,
                "ndc": loso_info["ndc"],
                "delta": delta,
                "delta_bootstrap_interval": delta_interval,
                "delta_bootstrap_definability_rate": definability_rate,
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    cv_summary = load_cv_summary()
    bootstrap = load_bootstrap_summary()
    prev_cv = load_prevalence_cv()
    loso_df = load_predictions("repeated_seed_loso_predictions")

    table5 = build_table5(cv_summary, prev_cv)
    write_csv_md(
        table5,
        "table5_strengthened",
        title="Strengthened Table 5 — pooled CV by predictor family (RF)",
        intro="Repeated-seed pooled CV (100 seeds); intervals are 2.5–97.5 percentiles across seeds.",
    )

    table6 = build_table6(cv_summary, bootstrap, loso_df, None)
    write_csv_md(
        table6,
        "table6_strengthened",
        title="Strengthened Table 6 — CV vs LOSO and bootstrap Δ",
        intro=(
            "LOSO μ = mean of definable per-system fold ROC-AUC (RF-only). "
            "Δ bootstrap uses cluster resampling by system_id."
        ),
    )
    print(f"Wrote {TABLES_DIR / 'table5_strengthened.csv'}")
    print(f"Wrote {TABLES_DIR / 'table6_strengthened.csv'}")


if __name__ == "__main__":
    main()
