#!/usr/bin/env python3
"""
Leave-one-system-out (LOSO) generalization study.

Trains on 11 specifications, tests on the held-out system_id.
Exploratory; no causal claims; no LLM inference.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

from figure_style import plot_transfer_heatmap
import pandas as pd
from sklearn.base import clone

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from model_behavioural_correctness import (  # noqa: E402
    METRIC_NAMES,
    PREDICTOR_SETS,
    fold_metrics,
    load_scored_frame,
    make_model,
    prepare_features,
)
from repro_config import apply_reproducibility  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = ROOT / "results" / "tables"
FIGURES_DIR = ROOT / "results" / "figures"
RANDOM_CV_MD = TABLES_DIR / "model_performance.md"

MODEL_NAMES = [
    "logistic_regression",
    "decision_tree",
    "random_forest",
]

METRIC_LABELS = {
    "roc_auc": "ROC-AUC",
    "pr_auc": "PR-AUC",
    "balanced_accuracy": "Balanced accuracy",
    "f1": "F1",
    "recall_full_pass": "Recall (full pass)",
    "specificity_non_full_pass": "Specificity (non-full pass)",
}


def safe_fold_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray
) -> dict[str, float]:
    unique = np.unique(y_true)
    base = fold_metrics(y_true, y_pred, y_prob)
    if len(unique) < 2:
        base["roc_auc"] = float("nan")
        base["pr_auc"] = float("nan")
    return base


def loso_evaluate(
    df: pd.DataFrame,
    features: list[str],
    model_name: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    X_all = prepare_features(df, features)
    y_all = df["full_behavioural_pass"].astype(int)

    for held_out in sorted(df["system_id"].unique()):
        test_mask = df["system_id"] == held_out
        train_mask = ~test_mask
        X_train, y_train = X_all.loc[train_mask], y_all.loc[train_mask]
        X_test, y_test = X_all.loc[test_mask], y_all.loc[test_mask]

        row_base = {
            "held_out_system": held_out,
            "n_train": int(train_mask.sum()),
            "n_test": int(test_mask.sum()),
            "n_test_positive": int(y_test.sum()),
            "n_test_negative": int((1 - y_test).sum()),
        }

        if y_train.nunique() < 2:
            metrics = {name: float("nan") for name in METRIC_NAMES}
            rows.append({**row_base, **metrics, "fit_error": "single_class_train"})
            continue

        model = make_model(model_name)
        try:
            fitted = clone(model)
            fitted.fit(X_train, y_train)
            prob = fitted.predict_proba(X_test)[:, 1]
            pred = (prob >= 0.5).astype(int)
            metrics = safe_fold_metrics(y_test.to_numpy(), pred, prob)
            rows.append({**row_base, **metrics, "fit_error": ""})
        except Exception as exc:  # pragma: no cover
            metrics = {name: float("nan") for name in METRIC_NAMES}
            rows.append({**row_base, **metrics, "fit_error": str(exc)})

    return pd.DataFrame(rows)


def summarize_loso(fold_df: pd.DataFrame) -> dict[str, float]:
    summary: dict[str, float] = {}
    for metric in METRIC_NAMES:
        summary[f"{metric}_mean"] = float(fold_df[metric].mean(skipna=True))
        summary[f"{metric}_std"] = float(fold_df[metric].std(skipna=True, ddof=1))
        summary[f"{metric}_n_valid"] = float(fold_df[metric].notna().sum())
    return summary


def load_random_cv_means() -> pd.DataFrame:
    if not RANDOM_CV_MD.is_file():
        return pd.DataFrame()

    lines = RANDOM_CV_MD.read_text(encoding="utf-8").splitlines()
    table_lines = [line for line in lines if line.startswith("|") and "---" not in line]
    if len(table_lines) < 2:
        return pd.DataFrame()

    headers = [h.strip() for h in table_lines[0].strip("|").split("|")]
    rows = []
    for line in table_lines[1:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(dict(zip(headers, cells)))

    df = pd.DataFrame(rows)
    df = df[df["model"].isin(MODEL_NAMES)].copy()
    for col in df.columns:
        if col.endswith("_mean") or col.endswith("_std"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def markdown_table(df: pd.DataFrame, float_cols: set[str] | None = None) -> str:
    float_cols = float_cols or set()
    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        cells = []
        for col in headers:
            val = row[col]
            if col in float_cols and pd.notna(val):
                cells.append(f"{float(val):.3f}")
            elif isinstance(val, float) and pd.notna(val):
                cells.append(f"{float(val):.3f}")
            else:
                cells.append(str(val))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_loso_results(detail_df: pd.DataFrame, path: Path) -> None:
    float_cols = set(METRIC_NAMES) | {
        "n_train",
        "n_test",
        "n_test_positive",
        "n_test_negative",
    }
    lines = [
        "# Leave-one-system-out results",
        "",
        "Per held-out `system_id` evaluation (train on 11 systems, test on 1). "
        "Behaviourally scored runs only; target `full_behavioural_pass`.",
        "",
        markdown_table(detail_df, float_cols),
        "",
        "## Notes",
        "",
        "- `roc_auc` / `pr_auc` are undefined (empty) when the held-out system has "
        "only one target class.",
        "- `atm` and `bike_rental` have fewer scored runs due to campaign tiering.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_loso_summary(
    summary_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
    path: Path,
) -> None:
    float_cols = {
        c
        for c in comparison_df.columns
        if c.endswith("_mean") or c.endswith("_std") or c.startswith("delta_")
    }
    lines = [
        "# Leave-one-system-out summary",
        "",
        "Aggregated LOSO metrics (mean ± std across 12 held-out systems) compared "
        "with stratified 5-fold random CV from `model_performance.md`.",
        "",
        "## LOSO aggregate performance",
        "",
        markdown_table(summary_df, float_cols),
        "",
        "## Random CV vs LOSO (ROC-AUC) and degradation",
        "",
        "Δ = random CV ROC-AUC mean − LOSO ROC-AUC mean (positive ⇒ degradation under LOSO).",
        "",
        markdown_table(comparison_df, float_cols),
        "",
        "## Performance degradation highlights",
        "",
    ]

    if not comparison_df.empty:
        worst = comparison_df.sort_values("delta_roc_auc", ascending=False).iloc[0]
        best_loso = comparison_df.sort_values("loso_roc_auc_mean", ascending=False).iloc[0]
        lines.extend(
            [
                f"- Largest ROC-AUC drop: **{worst['predictor_set']}** + **{worst['model']}** "
                f"(Δ = {worst['delta_roc_auc']:.3f}).",
                f"- Best LOSO ROC-AUC (mean across systems): **{best_loso['predictor_set']}** + "
                f"**{best_loso['model']}** ({best_loso['loso_roc_auc_mean']:.3f}).",
            ]
        )
        set_degradation = (
            comparison_df.groupby("predictor_set")["delta_roc_auc"].mean().sort_values(ascending=False)
        )
        lines.append("- Mean degradation by predictor set (ROC-AUC):")
        for set_name, delta in set_degradation.items():
            lines.append(f"  - `{set_name}`: Δ = {delta:.3f}")
    lines.extend(
        [
            "",
            "## Interpretation guardrails",
            "",
            "- **Exploratory generalization check** — not confirmatory evidence.",
            "- LOSO tests specification-level transfer; it does not prove causal mechanisms.",
            "- Reference-difference predictors may not transfer when traceability profiles "
            "differ across systems.",
            "- Small held-out folds (e.g., `bike_rental`, n=5) yield unstable ROC-AUC.",
            "- Do **not** equate in-sample random-CV performance with cross-specification robustness.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_heatmap(detail_df: pd.DataFrame, path: Path) -> None:
    """Heatmap: systems × predictor sets, ROC-AUC averaged across models."""
    pivot_rows = []
    for (set_name, model), group in detail_df.groupby(["predictor_set", "model"]):
        for _, row in group.iterrows():
            pivot_rows.append(
                {
                    "held_out_system": row["held_out_system"],
                    "predictor_set": set_name,
                    "model": model,
                    "roc_auc": row["roc_auc"],
                }
            )
    long_df = pd.DataFrame(pivot_rows)
    mean_df = (
        long_df.groupby(["held_out_system", "predictor_set"])["roc_auc"]
        .mean()
        .reset_index()
    )
    pivot = mean_df.pivot(
        index="held_out_system", columns="predictor_set", values="roc_auc"
    )
    col_order = list(PREDICTOR_SETS.keys())
    pivot = pivot[[c for c in col_order if c in pivot.columns]]

    plot_transfer_heatmap(
        pivot,
        path,
        title="LOSO ROC-AUC by held-out system",
        subtitle="Cross-system transfer is weak",
        ylabel="Held-out requirement system",
        imbalance_note="Many held-out systems contain a single outcome class.",
        show_transfer_legend=True,
        annotation_note="Cell values: mean held-out ROC-AUC across LR, DT, and RF",
        figsize=(11.0, 10.5),
    )


def main() -> None:
    apply_reproducibility()
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_scored_frame()
    detail_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []

    for set_name, features in PREDICTOR_SETS.items():
        for model_name in MODEL_NAMES:
            fold_df = loso_evaluate(df, features, model_name)
            fold_df.insert(0, "predictor_set", set_name)
            fold_df.insert(1, "model", model_name)
            detail_frames.append(fold_df)

            agg = summarize_loso(fold_df)
            summary_rows.append(
                {
                    "predictor_set": set_name,
                    "model": model_name,
                    **agg,
                }
            )

    detail_df = pd.concat(detail_frames, ignore_index=True)
    summary_df = pd.DataFrame(summary_rows)

    random_cv = load_random_cv_means()
    comparison_rows = []
    for _, row in summary_df.iterrows():
        cv_row = random_cv[
            (random_cv["predictor_set"] == row["predictor_set"])
            & (random_cv["model"] == row["model"])
        ]
        cv_roc = float(cv_row["roc_auc_mean"].iloc[0]) if len(cv_row) else float("nan")
        loso_roc = float(row["roc_auc_mean"])
        comparison_rows.append(
            {
                "predictor_set": row["predictor_set"],
                "model": row["model"],
                "random_cv_roc_auc_mean": cv_roc,
                "loso_roc_auc_mean": loso_roc,
                "delta_roc_auc": cv_roc - loso_roc if pd.notna(cv_roc) else float("nan"),
                "random_cv_pr_auc_mean": float(cv_row["pr_auc_mean"].iloc[0])
                if len(cv_row)
                else float("nan"),
                "loso_pr_auc_mean": float(row["pr_auc_mean"]),
                "delta_pr_auc": (
                    float(cv_row["pr_auc_mean"].iloc[0]) - float(row["pr_auc_mean"])
                    if len(cv_row)
                    else float("nan")
                ),
            }
        )
    comparison_df = pd.DataFrame(comparison_rows)

    write_loso_results(detail_df, TABLES_DIR / "loso_system_results.md")
    write_loso_summary(summary_df, comparison_df, TABLES_DIR / "loso_system_summary.md")
    plot_heatmap(detail_df, FIGURES_DIR / "loso_system_heatmap.png")

    print(f"Wrote {TABLES_DIR / 'loso_system_results.md'}")
    print(f"Wrote {TABLES_DIR / 'loso_system_summary.md'}")
    print(f"Wrote {FIGURES_DIR / 'loso_system_heatmap.png'}")

    if not comparison_df.empty:
        worst = comparison_df.sort_values("delta_roc_auc", ascending=False).iloc[0]
        print(
            f"Largest ROC-AUC degradation: {worst['predictor_set']} + {worst['model']} "
            f"(Δ={worst['delta_roc_auc']:.3f})"
        )


if __name__ == "__main__":
    main()
