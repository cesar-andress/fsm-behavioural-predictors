#!/usr/bin/env python3
"""
Leave-one-model-out (LOMO) cross-model generalization study.

Trains on three LLM families, tests on the held-out fourth model.
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

LOMO_PREDICTOR_SETS = ("A_gate_only", "B_basic_structural", "D_combined")

CLASSIFIER_NAMES = [
    "logistic_regression",
    "random_forest",
]


def safe_fold_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray
) -> dict[str, float]:
    base = fold_metrics(y_true, y_pred, y_prob)
    if len(np.unique(y_true)) < 2:
        base["roc_auc"] = float("nan")
        base["pr_auc"] = float("nan")
    return base


def lomo_evaluate(
    df: pd.DataFrame,
    features: list[str],
    classifier_name: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    X_all = prepare_features(df, features)
    y_all = df["full_behavioural_pass"].astype(int)

    for held_out in sorted(df["model"].unique()):
        test_mask = df["model"] == held_out
        train_mask = ~test_mask
        X_train, y_train = X_all.loc[train_mask], y_all.loc[train_mask]
        X_test, y_test = X_all.loc[test_mask], y_all.loc[test_mask]

        row_base = {
            "held_out_model": held_out,
            "n_train": int(train_mask.sum()),
            "n_test": int(test_mask.sum()),
            "n_test_positive": int(y_test.sum()),
            "n_test_negative": int((1 - y_test).sum()),
        }

        if y_train.nunique() < 2:
            metrics = {name: float("nan") for name in METRIC_NAMES}
            rows.append({**row_base, **metrics, "fit_error": "single_class_train"})
            continue

        model = make_model(classifier_name)
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


def summarize_lomo(fold_df: pd.DataFrame) -> dict[str, float]:
    summary: dict[str, float] = {}
    for metric in METRIC_NAMES:
        summary[f"{metric}_mean"] = float(fold_df[metric].mean(skipna=True))
        summary[f"{metric}_std"] = float(fold_df[metric].std(skipna=True, ddof=1))
        summary[f"{metric}_n_valid"] = float(fold_df[metric].notna().sum())
        summary[f"{metric}_min"] = float(fold_df[metric].min(skipna=True))
        summary[f"{metric}_max"] = float(fold_df[metric].max(skipna=True))
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
    df = df[
        df["predictor_set"].isin(LOMO_PREDICTOR_SETS)
        & df["model"].isin(CLASSIFIER_NAMES)
    ].copy()
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


def write_lomo_results(detail_df: pd.DataFrame, path: Path) -> None:
    float_cols = set(METRIC_NAMES) | {
        "n_train",
        "n_test",
        "n_test_positive",
        "n_test_negative",
    }
    lines = [
        "# Leave-one-model-out results",
        "",
        "Per held-out `model` evaluation (train on 3 LLM families, test on 1). "
        "Behaviourally scored runs only; target `full_behavioural_pass`.",
        "",
        markdown_table(detail_df, float_cols),
        "",
        "## Notes",
        "",
        "- `roc_auc` / `pr_auc` are undefined when the held-out model fold has only "
        "one target class.",
        "- Four Ollama models: `gemma2:9b`, `llama3.1:8b`, `mistral-nemo:12b`, "
        "`qwen2.5-coder:7b`.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_lomo_summary(
    summary_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
    path: Path,
) -> None:
    float_cols = {
        c
        for c in summary_df.columns
        if c.endswith("_mean")
        or c.endswith("_std")
        or c.endswith("_min")
        or c.endswith("_max")
        or c.endswith("_n_valid")
    } | {
        c
        for c in comparison_df.columns
        if c.endswith("_mean") or c.startswith("delta_")
    }

    lines = [
        "# Leave-one-model-out summary",
        "",
        "Cross-model generalization: train on runs from three LLM families, test on "
        "the held-out fourth. Compared with stratified 5-fold random CV from "
        "`model_performance.md`.",
        "",
        "## LOMO aggregate performance (mean ± std across 4 held-out models)",
        "",
        markdown_table(summary_df, float_cols),
        "",
        "## Average, worst-case, and best-case ROC-AUC (held-out models)",
        "",
    ]

    roc_extremes = []
    for _, row in summary_df.iterrows():
        roc_extremes.append(
            {
                "predictor_set": row["predictor_set"],
                "classifier": row["model"],
                "roc_auc_mean": row["roc_auc_mean"],
                "roc_auc_worst": row["roc_auc_min"],
                "roc_auc_best": row["roc_auc_max"],
            }
        )
    extremes_df = pd.DataFrame(roc_extremes)
    lines.append(markdown_table(extremes_df, {"roc_auc_mean", "roc_auc_worst", "roc_auc_best"}))
    lines.append("")

    lines.extend(
        [
            "## Random CV vs LOMO and degradation",
            "",
            "Δ = random CV ROC-AUC mean − LOMO ROC-AUC mean (positive ⇒ degradation under LOMO).",
            "",
            markdown_table(comparison_df, float_cols),
            "",
            "## Performance highlights",
            "",
        ]
    )

    if not comparison_df.empty:
        worst_deg = comparison_df.sort_values("delta_roc_auc", ascending=False).iloc[0]
        best_lomo = comparison_df.sort_values("lomo_roc_auc_mean", ascending=False).iloc[0]
        worst_lomo = comparison_df.sort_values("lomo_roc_auc_mean", ascending=True).iloc[0]
        lines.extend(
            [
                f"- Largest ROC-AUC drop vs random CV: **{worst_deg['predictor_set']}** + "
                f"**{worst_deg['model']}** (Δ = {worst_deg['delta_roc_auc']:.3f}).",
                f"- Best LOMO ROC-AUC (mean across held-out models): "
                f"**{best_lomo['predictor_set']}** + **{best_lomo['model']}** "
                f"({best_lomo['lomo_roc_auc_mean']:.3f}).",
                f"- Worst LOMO ROC-AUC (mean across held-out models): "
                f"**{worst_lomo['predictor_set']}** + **{worst_lomo['model']}** "
                f"({worst_lomo['lomo_roc_auc_mean']:.3f}).",
            ]
        )
        set_degradation = (
            comparison_df.groupby("predictor_set")["delta_roc_auc"]
            .mean()
            .sort_values(ascending=False)
        )
        lines.append("- Mean degradation by predictor set (ROC-AUC):")
        for set_name, delta in set_degradation.items():
            lines.append(f"  - `{set_name}`: Δ = {delta:.3f}")

    lines.extend(
        [
            "",
            "## Do structural predictors generalize across LLM families?",
            "",
            "Interpretation is **exploratory** and must not be overstated:",
            "",
            "- LOMO tests whether gate and structural signals learned from three LLM "
            "families rank behavioural risk on a fourth, unseen family.",
            "- If LOMO ROC-AUC remains well above chance while random CV is high, signals "
            "may reflect **FSM properties** rather than LLM-specific artefacts.",
            "- If LOMO degrades sharply (especially for set **B**), structural counts may "
            "encode family-specific generation habits that do not transfer.",
            "- Set **D** includes oracle-adjacent traceability counts; strong LOMO "
            "performance there would not imply deployable pre-oracle screening.",
            "- Small held-out folds (n≈44–55 per model) and class imbalance limit "
            "stability of ROC-AUC and F1.",
            "",
            "## Interpretation guardrails",
            "",
            "- **Exploratory cross-model check** — not confirmatory evidence.",
            "- Does not prove that predictors are model-independent; only reports "
            "out-of-family ranking under this frozen cohort.",
            "- Do **not** equate random-CV performance with cross-LLM robustness.",
            "- No causal claims about LLM families or structural mechanisms.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_heatmap(detail_df: pd.DataFrame, path: Path) -> None:
    """Heatmap: held-out models × predictor sets, ROC-AUC averaged across classifiers."""
    long_df = detail_df[
        ["held_out_model", "predictor_set", "classifier", "roc_auc"]
    ].copy()
    mean_df = (
        long_df.groupby(["held_out_model", "predictor_set"])["roc_auc"]
        .mean()
        .reset_index()
    )
    pivot = mean_df.pivot(
        index="held_out_model", columns="predictor_set", values="roc_auc"
    )
    col_order = [c for c in LOMO_PREDICTOR_SETS if c in pivot.columns]
    pivot = pivot[col_order]

    plot_transfer_heatmap(
        pivot,
        path,
        title="LOMO ROC-AUC by held-out model",
        subtitle="Cross-model transfer degrades less",
        ylabel="Held-out LLM model",
        annotation_note="Cell values: mean across LR and RF; n/a = single-class fold",
        figsize=(9.5, 6.0),
    )


def main() -> None:
    apply_reproducibility()
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_scored_frame()
    n_models = df["model"].nunique()
    if n_models != 4:
        print(
            f"WARNING: expected 4 models, found {n_models}.",
            file=sys.stderr,
        )

    detail_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []

    for set_name in LOMO_PREDICTOR_SETS:
        features = PREDICTOR_SETS[set_name]
        for classifier_name in CLASSIFIER_NAMES:
            fold_df = lomo_evaluate(df, features, classifier_name)
            fold_df.insert(0, "predictor_set", set_name)
            fold_df.insert(1, "classifier", classifier_name)
            detail_frames.append(fold_df)

            agg = summarize_lomo(fold_df)
            summary_rows.append(
                {
                    "predictor_set": set_name,
                    "model": classifier_name,
                    **agg,
                }
            )

    detail_df = pd.concat(detail_frames, ignore_index=True)
    detail_out = detail_df.rename(columns={"classifier": "model"})
    summary_df = pd.DataFrame(summary_rows)

    random_cv = load_random_cv_means()
    comparison_rows = []
    for _, row in summary_df.iterrows():
        cv_row = random_cv[
            (random_cv["predictor_set"] == row["predictor_set"])
            & (random_cv["model"] == row["model"])
        ]
        cv_roc = float(cv_row["roc_auc_mean"].iloc[0]) if len(cv_row) else float("nan")
        lomo_roc = float(row["roc_auc_mean"])
        comparison_rows.append(
            {
                "predictor_set": row["predictor_set"],
                "model": row["model"],
                "random_cv_roc_auc_mean": cv_roc,
                "lomo_roc_auc_mean": lomo_roc,
                "delta_roc_auc": cv_roc - lomo_roc if pd.notna(cv_roc) else float("nan"),
                "random_cv_pr_auc_mean": float(cv_row["pr_auc_mean"].iloc[0])
                if len(cv_row)
                else float("nan"),
                "lomo_pr_auc_mean": float(row["pr_auc_mean"]),
                "delta_pr_auc": (
                    float(cv_row["pr_auc_mean"].iloc[0]) - float(row["pr_auc_mean"])
                    if len(cv_row)
                    else float("nan")
                ),
            }
        )
    comparison_df = pd.DataFrame(comparison_rows)

    write_lomo_results(detail_out, TABLES_DIR / "lomo_results.md")
    write_lomo_summary(summary_df, comparison_df, TABLES_DIR / "lomo_summary.md")
    plot_heatmap(detail_df, FIGURES_DIR / "lomo_heatmap.png")

    print(f"Wrote {TABLES_DIR / 'lomo_results.md'}")
    print(f"Wrote {TABLES_DIR / 'lomo_summary.md'}")
    print(f"Wrote {FIGURES_DIR / 'lomo_heatmap.png'}")

    if not comparison_df.empty:
        worst = comparison_df.sort_values("delta_roc_auc", ascending=False).iloc[0]
        print(
            f"Largest ROC-AUC degradation: {worst['predictor_set']} + {worst['model']} "
            f"(Δ={worst['delta_roc_auc']:.3f})"
        )


if __name__ == "__main__":
    main()
