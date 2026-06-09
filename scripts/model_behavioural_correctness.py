#!/usr/bin/env python3
"""
Exploratory predictive modelling: structural signals → full behavioural correctness.

Reads data/processed/master_analysis_dataset.csv (behaviourally scored runs only).
Stratified 5-fold CV; no hyperparameter tuning; no LLM inference.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from figure_style import (
    FIG_BASE_SIZE,
    FIG_CHANCE_LINEWIDTH,
    FIG_LEGEND_SIZE,
    FIG_TICK_SIZE,
    GRAY_DASH,
    MODEL_LEGEND_ORDER,
    MODEL_PLOT_ORDER,
    MODEL_STYLES,
    PREDICTOR_SET_ORDER,
    _gray,
    add_panel_label,
    apply_figure_style,
    model_label,
    predictor_set_label,
    save_figure,
    style_axes,
)
from matplotlib.lines import Line2D
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from repro_config import (
    DT_MAX_DEPTH,
    LR_MAX_ITER,
    N_SPLITS,
    RANDOM_STATE,
    RF_MAX_DEPTH,
    RF_N_ESTIMATORS,
    SKLEARN_N_JOBS,
    apply_reproducibility,
)

ROOT = Path(__file__).resolve().parents[1]
MASTER_CSV = ROOT / "data" / "processed" / "master_analysis_dataset.csv"
TABLES_DIR = ROOT / "results" / "tables"
FIGURES_DIR = ROOT / "results" / "figures"

PREDICTOR_SETS: dict[str, list[str]] = {
    "A_gate_only": ["g2_pass", "g3_pass", "g3a_pass"],
    "B_basic_structural": [
        "n_states",
        "n_events",
        "n_transitions",
        "n_unreachable_states",
    ],
    "C_reference_difference": ["missing_transitions", "extra_transitions"],
    "D_combined": [
        "g2_pass",
        "g3_pass",
        "g3a_pass",
        "n_states",
        "n_events",
        "n_transitions",
        "n_unreachable_states",
        "missing_transitions",
        "extra_transitions",
        "requirement_coverage",
    ],
}

BOOL_COLUMNS = [
    "g1_pass",
    "g2_pass",
    "g3_pass",
    "g3a_pass",
    "full_behavioural_pass",
    "behaviourally_scored",
]

METRIC_NAMES = [
    "roc_auc",
    "pr_auc",
    "balanced_accuracy",
    "f1",
    "recall_full_pass",
    "specificity_non_full_pass",
]


def load_scored_frame() -> pd.DataFrame:
    if not MASTER_CSV.is_file():
        print(f"ERROR: {MASTER_CSV} not found. Run: make build-master", file=sys.stderr)
        raise SystemExit(1)

    df = pd.read_csv(MASTER_CSV)
    for col in BOOL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].map(
                {"true": True, "false": False, True: True, False: False}
            )
    scored = df[df["behaviourally_scored"] == True].copy()  # noqa: E712
    return scored


def prepare_features(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    out = df[features].copy()
    for col in features:
        if out[col].dtype == bool or set(out[col].dropna().unique()).issubset({True, False}):
            out[col] = out[col].astype(int)
    return out


def missingness_report(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    rows = []
    for feature in features:
        missing = int(df[feature].isna().sum())
        rows.append(
            {
                "feature": feature,
                "missing_count": missing,
                "missing_rate": missing / len(df) if len(df) else 0.0,
            }
        )
    return pd.DataFrame(rows)


def make_model(name: str) -> Pipeline | DummyClassifier:
    if name == "logistic_regression":
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=LR_MAX_ITER,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        )
    if name == "decision_tree":
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "clf",
                    DecisionTreeClassifier(
                        max_depth=DT_MAX_DEPTH,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        )
    if name == "random_forest":
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=RF_N_ESTIMATORS,
                        max_depth=RF_MAX_DEPTH,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        )
    if name == "dummy_stratified":
        return DummyClassifier(strategy="stratified", random_state=RANDOM_STATE)
    if name == "dummy_majority":
        return DummyClassifier(strategy="most_frequent")
    raise ValueError(f"Unknown model: {name}")


def fold_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> dict[str, float]:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    return {
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "pr_auc": float(average_precision_score(y_true, y_prob)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "recall_full_pass": float(recall_score(y_true, y_pred, zero_division=0)),
        "specificity_non_full_pass": float(specificity),
    }


def cross_validated_metrics(
    model: Pipeline | DummyClassifier,
    X: pd.DataFrame,
    y: pd.Series,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    fold_rows: list[dict[str, Any]] = []
    y_prob = cross_val_predict(
        model, X, y, cv=cv, method="predict_proba", n_jobs=SKLEARN_N_JOBS
    )[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    for fold_idx, (train_idx, test_idx) in enumerate(cv.split(X, y), start=1):
        estimator = clone(model)
        estimator.fit(X.iloc[train_idx], y.iloc[train_idx])
        prob = estimator.predict_proba(X.iloc[test_idx])[:, 1]
        pred = (prob >= 0.5).astype(int)
        metrics = fold_metrics(y.iloc[test_idx].to_numpy(), pred, prob)
        metrics["fold"] = fold_idx
        fold_rows.append(metrics)

    return pd.DataFrame(fold_rows), y_prob, y_pred


def summarize_metrics(fold_df: pd.DataFrame) -> dict[str, float]:
    summary: dict[str, float] = {}
    for metric in METRIC_NAMES:
        summary[f"{metric}_mean"] = float(fold_df[metric].mean())
        summary[f"{metric}_std"] = float(fold_df[metric].std(ddof=1))
    return summary


def extract_importance(
    model: Pipeline | DummyClassifier,
    X: pd.DataFrame,
    y: pd.Series,
    feature_names: list[str],
) -> pd.DataFrame:
    fitted = clone(model)
    fitted.fit(X, y)
    clf = fitted.named_steps["clf"] if isinstance(fitted, Pipeline) else fitted

    if hasattr(clf, "feature_importances_"):
        values = clf.feature_importances_
        kind = "feature_importance"
    elif hasattr(clf, "coef_"):
        values = np.abs(clf.coef_.ravel())
        kind = "abs_coefficient"
    else:
        return pd.DataFrame(
            {"feature": feature_names, "importance": [np.nan] * len(feature_names), "type": kind}
        )

    return pd.DataFrame(
        {
            "feature": feature_names,
            "importance": values,
            "type": kind,
        }
    ).sort_values("importance", ascending=False)


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


def write_model_performance(results: pd.DataFrame, path: Path) -> None:
    float_cols = {c for c in results.columns if c.endswith("_mean") or c.endswith("_std")}
    lines = [
        "# Model performance",
        "",
        "Exploratory stratified 5-fold cross-validation predicting `full_behavioural_pass` "
        "from structural signals (behaviourally scored runs only).",
        "",
        "**Not confirmatory.** Results indicate out-of-fold discrimination under a fixed, "
        "lightly regularised modelling protocol — not causal effects.",
        "",
        markdown_table(results, float_cols),
        "",
        "## Interpretation guardrails",
        "",
        "- Positive class prevalence is low (30/209); metrics can be unstable fold-to-fold.",
        "- Reference-difference predictors (`missing_transitions`, `extra_transitions`) are "
        "oracle-adjacent traceability counts and may admit near-separable splits in this "
        "frozen cohort — treat set **C** and **D** discrimination as descriptive, not causal.",
        "- Gate-only set **A** shows limited discrimination above stratified baselines.",
        "- Basic structural set **B** shows moderate out-of-fold signal without perfect separation.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_feature_importance(frames: list[pd.DataFrame], path: Path) -> None:
    lines = [
        "# Model feature importance",
        "",
        "Importance from models refit on the full scored analysis set (n=209). "
        "Tree models report `feature_importances_`; logistic regression reports "
        "|coefficient| after standardisation.",
        "",
    ]
    for frame in frames:
        if frame.empty:
            continue
        key = frame.attrs.get("title", "model")
        lines.append(f"## {key}")
        lines.append("")
        lines.append(markdown_table(frame, {"importance"}))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_model_validation(
    df: pd.DataFrame,
    missing_frames: dict[str, pd.DataFrame],
    path: Path,
) -> None:
    y = df["full_behavioural_pass"].astype(int)
    lines = [
        "# Model validation notes",
        "",
        "## Analysis set",
        "",
        f"- Rows: **{len(df)}** (behaviourally scored runs only)",
        f"- Target: `full_behavioural_pass`",
        f"- Positive class (full pass): **{int(y.sum())}** ({100 * y.mean():.1f}%)",
        f"- Negative class: **{int((1 - y).sum())}** ({100 * (1 - y.mean()):.1f}%)",
        "",
        "## Cross-validation",
        "",
        f"- Method: stratified {N_SPLITS}-fold CV (`shuffle=True`, `random_state={RANDOM_STATE}`)",
        "- Threshold: 0.5 on predicted positive-class probability",
        "- No model or system identifiers used as predictors",
        "- Preprocessing fit inside each training fold only (pipelines)",
        "",
        "## Missingness before imputation (scored runs)",
        "",
    ]
    for set_name, miss in missing_frames.items():
        total_missing = int(miss["missing_count"].sum())
        lines.append(f"### Predictor set `{set_name}` — total missing cells: {total_missing}")
        lines.append("")
        lines.append(markdown_table(miss, {"missing_rate"}))
        lines.append("")
    lines.extend(
        [
            "## Leakage controls",
            "",
            "- Target derived from `behavioral_pass_rate` but predictors are structural only.",
            "- Median imputation and scaling applied within CV training folds when used.",
            "- No test-fold information used for feature selection.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_curves(
    df: pd.DataFrame,
    curve_data: dict[str, dict[str, tuple[np.ndarray, np.ndarray]]],
    curve_fn,
    y_label: str,
    title: str,
    path: Path,
) -> None:
    apply_figure_style()
    panel_letters = ["A", "B", "C", "D"]
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 10.5))
    for ax, set_name, panel in zip(axes.ravel(), PREDICTOR_SET_ORDER, panel_letters):
        for model_name in MODEL_PLOT_ORDER:
            curves = curve_data[set_name]
            if model_name not in curves:
                continue
            x, y = curves[model_name]
            style = MODEL_STYLES.get(model_name, {})
            ax.plot(x, y, **style)
        add_panel_label(ax, panel)
        ax.set_title(
            predictor_set_label(set_name),
            fontsize=FIG_TICK_SIZE,
            fontweight="bold",
            pad=6,
            loc="center",
            color=_gray(0.08),
        )
        if curve_fn is roc_curve:
            ax.set_xlabel("False positive rate (proportion; 0--1)", fontsize=FIG_BASE_SIZE)
            ax.set_ylabel("True positive rate (proportion; 0--1)", fontsize=FIG_BASE_SIZE)
        else:
            ax.set_xlabel("Recall (proportion of full passes; 0--1)", fontsize=FIG_BASE_SIZE)
            ax.set_ylabel("Precision (proportion flagged full-pass; 0--1)", fontsize=FIG_BASE_SIZE)
        style_axes(ax)
        ax.tick_params(labelsize=FIG_TICK_SIZE)
        ax.grid(True, linestyle=":", linewidth=0.6, alpha=0.22)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    if curve_fn is roc_curve:
        for ax in axes.ravel():
            ax.plot(
                [0, 1],
                [0, 1],
                linestyle="--",
                color=_gray(GRAY_DASH),
                linewidth=FIG_CHANCE_LINEWIDTH,
                alpha=0.75,
                zorder=0,
            )
    _legend_names = {
        "logistic_regression": "LR (black solid)",
        "decision_tree": "DT (gray dashed)",
        "random_forest": "RF (gray dash-dot)",
        "dummy_stratified": "Dummy strat. (gray dotted)",
    }
    legend_handles = [
        Line2D(
            [0],
            [0],
            label=_legend_names.get(model_name, model_label(model_name)),
            **MODEL_STYLES[model_name],
        )
        for model_name in MODEL_LEGEND_ORDER
    ]
    if curve_fn is roc_curve:
        legend_handles.append(
            Line2D(
                [0],
                [0],
                color=_gray(GRAY_DASH),
                linestyle="--",
                linewidth=FIG_CHANCE_LINEWIDTH,
                label="Chance diagonal (AUC = 0.5)",
            )
        )
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=min(3, len(legend_handles)),
        bbox_to_anchor=(0.5, 0.01),
        frameon=True,
        fancybox=False,
        edgecolor=_gray(GRAY_DASH),
        fontsize=FIG_LEGEND_SIZE,
        columnspacing=1.2,
    )
    fig.subplots_adjust(left=0.10, right=0.98, top=0.97, bottom=0.16, hspace=0.38, wspace=0.30)
    save_figure(fig, path)


def main() -> None:
    apply_reproducibility()
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_scored_frame()
    y = df["full_behavioural_pass"].astype(int)

    model_names = [
        "logistic_regression",
        "decision_tree",
        "random_forest",
        "dummy_stratified",
        "dummy_majority",
    ]

    performance_rows: list[dict[str, Any]] = []
    importance_frames: list[pd.DataFrame] = []
    missing_frames: dict[str, pd.DataFrame] = {}
    roc_plot_data: dict[str, dict[str, tuple[np.ndarray, np.ndarray]]] = {
        k: {} for k in PREDICTOR_SETS
    }
    pr_plot_data: dict[str, dict[str, tuple[np.ndarray, np.ndarray]]] = {
        k: {} for k in PREDICTOR_SETS
    }

    for set_name, features in PREDICTOR_SETS.items():
        missing_frames[set_name] = missingness_report(df, features)
        X = prepare_features(df, features)

        for model_name in model_names:
            model = make_model(model_name)
            fold_df, y_prob, _ = cross_validated_metrics(model, X, y)
            summary = summarize_metrics(fold_df)
            row = {
                "predictor_set": set_name,
                "model": model_name,
                **summary,
            }
            performance_rows.append(row)

            fpr, tpr, _ = roc_curve(y, y_prob)
            prec, rec, _ = precision_recall_curve(y, y_prob)
            roc_plot_data[set_name][model_name] = (fpr, tpr)
            pr_plot_data[set_name][model_name] = (rec, prec)

            if model_name in {"decision_tree", "random_forest", "logistic_regression"}:
                imp = extract_importance(model, X, y, features)
                imp.attrs["title"] = f"{set_name} — {model_name}"
                importance_frames.append(imp)

    performance_df = pd.DataFrame(performance_rows)
    write_model_performance(performance_df, TABLES_DIR / "model_performance.md")
    write_feature_importance(importance_frames, TABLES_DIR / "model_feature_importance.md")
    write_model_validation(df, missing_frames, TABLES_DIR / "model_validation.md")

    plot_curves(
        df,
        roc_plot_data,
        roc_curve,
        "True positive rate",
        "ROC curves (out-of-fold predictions)",
        FIGURES_DIR / "roc_curves.png",
    )
    plot_curves(
        df,
        pr_plot_data,
        precision_recall_curve,
        "Precision",
        "Precision–recall curves (out-of-fold predictions)",
        FIGURES_DIR / "precision_recall_curves.png",
    )

    best = performance_df.sort_values("roc_auc_mean", ascending=False).iloc[0]
    print(f"Wrote {TABLES_DIR / 'model_performance.md'}")
    print(f"Wrote {TABLES_DIR / 'model_feature_importance.md'}")
    print(f"Wrote {TABLES_DIR / 'model_validation.md'}")
    print(f"Wrote {FIGURES_DIR / 'roc_curves.png'}")
    print(f"Wrote {FIGURES_DIR / 'precision_recall_curves.png'}")
    print(
        f"Best ROC-AUC (exploratory): {best['predictor_set']} + {best['model']} "
        f"= {best['roc_auc_mean']:.3f} ± {best['roc_auc_std']:.3f}"
    )


if __name__ == "__main__":
    main()
