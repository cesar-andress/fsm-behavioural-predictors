#!/usr/bin/env python3
"""Cluster bootstrap uncertainty for pair-partition AUC estimators."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from metrics_utils import (  # noqa: E402
    roc_auc_cross_groups,
    roc_auc_safe,
    roc_auc_within_groups,
    summarize_values,
)
from repro_config import N_BOOTSTRAP_ITERATIONS, RANDOM_STATE, STRENGTHEN_CLASSIFIER  # noqa: E402
from strengthen_io import (  # noqa: E402
    TABLES_DIR,
    ensure_output_dirs,
    load_predictions,
    markdown_table,
    write_csv_md,
)

FAMILY_B = "B_basic_structural"
METRICS = [
    ("auc_pooled", "Pooled ROC-AUC"),
    ("auc_within_groups", "Within-group pair-stratum AUC"),
    ("auc_cross_groups", "Cross-group pair-stratum AUC"),
]


def mean_oof_pool(pred_df: pd.DataFrame, *, predictor_set: str, model: str | None) -> pd.DataFrame:
    sub = pred_df[pred_df["predictor_set"] == predictor_set]
    if model is not None:
        sub = sub[sub["model"] == model]
    return (
        sub.groupby(["row_index", "system_id", "y_true"], as_index=False)["y_score"]
        .mean()
        .assign(predictor_set=predictor_set)
    )


def bootstrap_partition_aucs(
    pool_df: pd.DataFrame,
    *,
    predictor_set: str,
    predictor_label: str,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    systems = sorted(pool_df["system_id"].unique())
    y_all = pool_df["y_true"].to_numpy(dtype=int)
    score_all = pool_df["y_score"].to_numpy(dtype=float)
    groups_all = pool_df["system_id"].to_numpy()

    point = {
        "auc_pooled": roc_auc_safe(y_all, score_all),
        "auc_within_groups": roc_auc_within_groups(y_all, score_all, groups_all),
        "auc_cross_groups": roc_auc_cross_groups(y_all, score_all, groups_all),
    }

    boot_rows: list[dict[str, Any]] = []
    for iteration in range(N_BOOTSTRAP_ITERATIONS):
        sampled = rng.choice(systems, size=len(systems), replace=True)
        parts = [pool_df[pool_df["system_id"] == sys] for sys in sampled]
        sample = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
        if sample.empty:
            row = {
                "iteration": iteration,
                "predictor_set": predictor_set,
                "auc_pooled": float("nan"),
                "auc_within_groups": float("nan"),
                "auc_cross_groups": float("nan"),
            }
        else:
            y = sample["y_true"].to_numpy(dtype=int)
            score = sample["y_score"].to_numpy(dtype=float)
            groups = sample["system_id"].to_numpy()
            row = {
                "iteration": iteration,
                "predictor_set": predictor_set,
                "auc_pooled": roc_auc_safe(y, score),
                "auc_within_groups": roc_auc_within_groups(y, score, groups),
                "auc_cross_groups": roc_auc_cross_groups(y, score, groups),
            }
        boot_rows.append(row)

    boot_df = pd.DataFrame(boot_rows)
    summary: dict[str, Any] = {
        "predictor_set": predictor_set,
        "predictor_label": predictor_label,
        "n_systems": len(systems),
        "n_bootstrap_iterations": N_BOOTSTRAP_ITERATIONS,
    }
    for key, label in METRICS:
        stats = summarize_values(boot_df[key])
        n_valid = int(boot_df[key].notna().sum())
        summary[f"{key}_point"] = point[key]
        summary[f"{key}_median"] = stats["median"]
        summary[f"{key}_p025"] = stats["p025"]
        summary[f"{key}_p975"] = stats["p975"]
        summary[f"{key}_n_valid"] = n_valid
        summary[f"{key}_nan_fraction"] = 1.0 - (n_valid / N_BOOTSTRAP_ITERATIONS)

    return boot_df, summary


def write_bootstrap_summary_md(summary_df: pd.DataFrame) -> Path:
    md_path = TABLES_DIR / "grouped_auc_bootstrap_summary.md"
    display_cols = [
        "predictor_label",
        "auc_pooled_point",
        "auc_pooled_median",
        "auc_pooled_p025",
        "auc_pooled_p975",
        "auc_pooled_nan_fraction",
        "auc_within_groups_point",
        "auc_within_groups_median",
        "auc_within_groups_p025",
        "auc_within_groups_p975",
        "auc_within_groups_nan_fraction",
        "auc_cross_groups_point",
        "auc_cross_groups_median",
        "auc_cross_groups_p025",
        "auc_cross_groups_p975",
        "auc_cross_groups_nan_fraction",
    ]
    subset = summary_df[display_cols]
    lines = [
        "# Cluster-bootstrap summary for pair-partition AUC estimators",
        "",
        (
            f"Resampling unit: `system_id`; {N_BOOTSTRAP_ITERATIONS} iterations. "
            "NaN replicates are retained when a metric has no eligible pairs."
        ),
        "",
        markdown_table(subset),
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def main() -> None:
    ensure_output_dirs()
    oof_df = load_predictions("repeated_seed_oof_predictions")
    prev_df = load_predictions("prevalence_baseline_cv_predictions")

    pools = [
        (FAMILY_B, "Family B graph tallies", mean_oof_pool(oof_df, predictor_set=FAMILY_B, model=STRENGTHEN_CLASSIFIER)),
        (
            "prevalence_only",
            "prevalence-only baseline",
            mean_oof_pool(prev_df, predictor_set="prevalence_only", model=None),
        ),
    ]

    rng = np.random.default_rng(RANDOM_STATE)
    all_boot: list[pd.DataFrame] = []
    summaries: list[dict[str, Any]] = []

    for predictor_set, predictor_label, pool_df in pools:
        boot_df, summary = bootstrap_partition_aucs(
            pool_df,
            predictor_set=predictor_set,
            predictor_label=predictor_label,
            rng=rng,
        )
        all_boot.append(boot_df)
        summaries.append(summary)

    boot_all = pd.concat(all_boot, ignore_index=True)
    summary_df = pd.DataFrame(summaries)

    write_csv_md(
        summary_df,
        "grouped_auc_bootstrap",
        title="Cluster bootstrap of pair-partition AUC estimators",
        intro=(
            f"{N_BOOTSTRAP_ITERATIONS} bootstrap iterations; cluster unit = system_id; "
            "scores = mean OOF across repeated-seed CV."
        ),
    )
    boot_all.to_csv(TABLES_DIR / "grouped_auc_bootstrap_iterations.csv", index=False)
    summary_path = write_bootstrap_summary_md(summary_df)

    print(f"Wrote {TABLES_DIR / 'grouped_auc_bootstrap.csv'}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
