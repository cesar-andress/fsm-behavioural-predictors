#!/usr/bin/env python3
"""Pair-partition AUC diagnostics on the FSM cohort (Family B and prevalence-only)."""

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
    group_definability_table,
    roc_auc_pair_counts,
    roc_auc_safe,
    summarize_values,
)
from model_behavioural_correctness import load_scored_frame  # noqa: E402
from repro_config import STRENGTHEN_CLASSIFIER, STRENGTHEN_SEEDS  # noqa: E402
from strengthen_io import (  # noqa: E402
    TABLES_DIR,
    ensure_output_dirs,
    load_predictions,
    markdown_table,
    write_csv_md,
)

FAMILY_B = "B_basic_structural"
PREDICTORS = [
    ("B_basic_structural", "Family B graph tallies"),
    ("prevalence_only", "prevalence-only baseline"),
]


def mean_oof_by_seed(
    pred_df: pd.DataFrame,
    *,
    predictor_set: str,
    model: str | None,
) -> dict[int, pd.DataFrame]:
    sub = pred_df[pred_df["predictor_set"] == predictor_set]
    if model is not None:
        sub = sub[sub["model"] == model]
    by_seed: dict[int, pd.DataFrame] = {}
    for seed, group in sub.groupby("seed"):
        by_seed[int(seed)] = group.sort_values("row_index").reset_index(drop=True)
    return by_seed


def decomposition_row(
    *,
    predictor_set: str,
    predictor_label: str,
    seed: int | str,
    y: np.ndarray,
    score: np.ndarray,
    groups: np.ndarray,
) -> dict[str, Any]:
    counts = roc_auc_pair_counts(y, score, groups)
    return {
        "predictor_set": predictor_set,
        "predictor_label": predictor_label,
        "seed": seed,
        "auc_pooled": roc_auc_safe(y, score),
        "auc_within_groups": counts["auc_within"],
        "auc_cross_groups": counts["auc_cross"],
        "n_within_pairs": int(counts["n_within_pairs"]),
        "n_cross_pairs": int(counts["n_cross_pairs"]),
        "n_total_pairs": int(counts["n_total_pairs"]),
        "share_within_pairs": counts["share_within_pairs"],
        "share_cross_pairs": counts["share_cross_pairs"],
    }


def write_summary_md(summary_df: pd.DataFrame, *, pair_df: pd.DataFrame, ndc: int, n_groups: int) -> Path:
    md_path = TABLES_DIR / "grouped_auc_decomposition_summary.md"
    lines = [
        "# Pair-partition AUC decomposition summary (FSM cohort)",
        "",
        (
            "Pooled ROC-AUC is reported together with within-group and cross-group "
            "pair-stratum AUCs. These partition eligible positive–negative comparison "
            "pairs; they do not form an additive decomposition of AUC values."
        ),
        "",
        f"Dual-class groups (ndc): {ndc}/{n_groups}.",
        "",
        "## Pair structure (label-only; identical across predictors)",
        "",
        markdown_table(pair_df),
        "",
        "## AUC by predictor (mean across seeds)",
        "",
        markdown_table(summary_df),
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def main() -> None:
    ensure_output_dirs()
    df = load_scored_frame()
    y = df["full_behavioural_pass"].astype(int).to_numpy()
    groups = df["system_id"].to_numpy()

    definability = group_definability_table(df, "system_id", "full_behavioural_pass")
    ndc = int(definability["dual_class"].sum())
    n_groups = len(definability)

    pair_counts = roc_auc_pair_counts(y, np.zeros_like(y, dtype=float), groups)
    pair_df = pd.DataFrame(
        [
            {
                "n_groups": n_groups,
                "ndc": ndc,
                "n_within_pairs": int(pair_counts["n_within_pairs"]),
                "n_cross_pairs": int(pair_counts["n_cross_pairs"]),
                "n_total_pairs": int(pair_counts["n_total_pairs"]),
                "share_within_pairs": pair_counts["share_within_pairs"],
                "share_cross_pairs": pair_counts["share_cross_pairs"],
            }
        ]
    )
    pair_df.to_csv(TABLES_DIR / "group_pair_contribution.csv", index=False)

    oof_df = load_predictions("repeated_seed_oof_predictions")
    prev_df = load_predictions("prevalence_baseline_cv_predictions")

    pred_sources = {
        FAMILY_B: mean_oof_by_seed(oof_df, predictor_set=FAMILY_B, model=STRENGTHEN_CLASSIFIER),
        "prevalence_only": mean_oof_by_seed(prev_df, predictor_set="prevalence_only", model=None),
    }

    rows: list[dict[str, Any]] = []
    for predictor_set, predictor_label in PREDICTORS:
        by_seed = pred_sources[predictor_set]
        for seed in STRENGTHEN_SEEDS:
            if seed not in by_seed:
                continue
            seed_df = by_seed[seed]
            rows.append(
                decomposition_row(
                    predictor_set=predictor_set,
                    predictor_label=predictor_label,
                    seed=seed,
                    y=seed_df["y_true"].to_numpy(),
                    score=seed_df["y_score"].to_numpy(),
                    groups=seed_df["system_id"].to_numpy(),
                )
            )

        seed_frames = [by_seed[s] for s in STRENGTHEN_SEEDS if s in by_seed]
        if seed_frames:
            pooled = (
                pd.concat(seed_frames, ignore_index=True)
                .groupby("row_index", as_index=False)
                .agg(
                    y_true=("y_true", "first"),
                    system_id=("system_id", "first"),
                    y_score=("y_score", "mean"),
                )
            )
            rows.append(
                decomposition_row(
                    predictor_set=predictor_set,
                    predictor_label=predictor_label,
                    seed="mean_oof",
                    y=pooled["y_true"].to_numpy(),
                    score=pooled["y_score"].to_numpy(),
                    groups=pooled["system_id"].to_numpy(),
                )
            )

    decomp_df = pd.DataFrame(rows)
    decomp_df.to_csv(TABLES_DIR / "grouped_auc_decomposition.csv", index=False)

    summary_rows: list[dict[str, Any]] = []
    metric_cols = [
        "auc_pooled",
        "auc_within_groups",
        "auc_cross_groups",
        "share_within_pairs",
        "share_cross_pairs",
    ]
    seed_only = decomp_df[decomp_df["seed"] != "mean_oof"]
    for predictor_set, predictor_label in PREDICTORS:
        sub = seed_only[seed_only["predictor_set"] == predictor_set]
        row: dict[str, Any] = {
            "predictor_set": predictor_set,
            "predictor_label": predictor_label,
            "n_seeds": len(sub),
        }
        for col in metric_cols:
            stats = summarize_values(sub[col])
            row[f"{col}_mean"] = stats["mean"]
            row[f"{col}_p025"] = stats["p025"]
            row[f"{col}_p975"] = stats["p975"]
        row["n_within_pairs"] = int(sub["n_within_pairs"].iloc[0]) if len(sub) else 0
        row["n_cross_pairs"] = int(sub["n_cross_pairs"].iloc[0]) if len(sub) else 0
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    write_csv_md(
        summary_df,
        "grouped_auc_decomposition_by_predictor",
        title="Pair-partition AUC by predictor (seed distribution)",
        intro="Means and 2.5–97.5% percentiles across repeated-seed CV OOF scores.",
    )
    summary_path = write_summary_md(summary_df, pair_df=pair_df, ndc=ndc, n_groups=n_groups)

    print(f"Wrote {TABLES_DIR / 'grouped_auc_decomposition.csv'}")
    print(f"Wrote {TABLES_DIR / 'group_pair_contribution.csv'}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
