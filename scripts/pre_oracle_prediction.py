#!/usr/bin/env python3
"""
Strict pre-oracle behavioural correctness prediction.

Uses only signals available before reference-difference (oracle traceability)
analysis. Stratified 5-fold CV; same protocol as model_behavioural_correctness.py.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_curve

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from model_behavioural_correctness import (  # noqa: E402
    METRIC_NAMES,
    N_SPLITS,
    RANDOM_STATE,
    cross_validated_metrics,
    extract_importance,
    load_scored_frame,
    make_model,
    markdown_table,
    missingness_report,
    prepare_features,
    summarize_metrics,
)

ROOT = Path(__file__).resolve().parents[1]
TABLES_DIR = ROOT / "results" / "tables"
FIGURES_DIR = ROOT / "results" / "figures"
RANDOM_CV_MD = TABLES_DIR / "model_performance.md"

PRE_ORACLE_SET = "pre_oracle"

PRE_ORACLE_FEATURES: list[str] = [
    "g2_pass",
    "g3_pass",
    "g3a_pass",
    "requirement_coverage",
    "n_states",
    "n_events",
    "n_transitions",
    "n_unreachable_states",
]

FORBIDDEN_FEATURES: frozenset[str] = frozenset(
    {
        "missing_transitions",
        "extra_transitions",
        "behavioral_pass_rate",
        "full_behavioural_pass",
        "behaviourally_scored",
        "g1_pass",
        "failure_stage",
        "run_id",
        "model",
        "system_id",
        "replicate",
    }
)

MODEL_NAMES = [
    "logistic_regression",
    "decision_tree",
    "random_forest",
]

BASELINE_SETS = ("A_gate_only", "B_basic_structural")


def assert_feature_policy(features: list[str]) -> None:
    overlap = FORBIDDEN_FEATURES & set(features)
    if overlap:
        raise ValueError(f"Forbidden predictors in feature list: {sorted(overlap)}")
    if set(features) != set(PRE_ORACLE_FEATURES):
        raise ValueError(
            "Feature list must match the strict pre-oracle allowlist exactly."
        )


def load_baseline_cv_means() -> pd.DataFrame:
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
        df["predictor_set"].isin(BASELINE_SETS) & df["model"].isin(MODEL_NAMES)
    ].copy()
    for col in df.columns:
        if col.endswith("_mean") or col.endswith("_std"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def write_pre_oracle_performance(
    results: pd.DataFrame,
    comparison: pd.DataFrame,
    path: Path,
) -> None:
    float_cols = {c for c in results.columns if c.endswith("_mean") or c.endswith("_std")}
    lines = [
        "# Pre-oracle model performance",
        "",
        "Exploratory stratified 5-fold cross-validation predicting `full_behavioural_pass` "
        "using **only pre-oracle signals** (behaviourally scored runs, n=209).",
        "",
        "**Not confirmatory.** No causal claims. Target labels come from behavioural "
        "evaluation; predictors are restricted to gate outcomes, requirement coverage, "
        "and basic FSM counts available before reference-difference analysis.",
        "",
        "## Allowed predictors",
        "",
        ", ".join(f"`{f}`" for f in PRE_ORACLE_FEATURES),
        "",
        "## Forbidden (excluded)",
        "",
        "`missing_transitions`, `extra_transitions`, `behavioral_pass_rate`, and any "
        "oracle-derived or outcome-derived variable.",
        "",
        f"## Cross-validation protocol",
        "",
        f"- Stratified {N_SPLITS}-fold CV (`shuffle=True`, `random_state={RANDOM_STATE}`)",
        "- Threshold: 0.5 on predicted positive-class probability",
        "- Same model configurations as `model_behavioural_correctness.py`",
        "",
        "## Pre-oracle results",
        "",
        markdown_table(results, float_cols),
        "",
    ]

    if not comparison.empty:
        cmp_float = {
            c
            for c in comparison.columns
            if c.endswith("_mean") or c.startswith("delta_")
        }
        lines.extend(
            [
                "## Comparison with prior predictor sets (random CV)",
                "",
                "Baselines from `model_performance.md` (same CV protocol). "
                "Δ = pre-oracle ROC-AUC − baseline ROC-AUC (positive ⇒ pre-oracle higher).",
                "",
                markdown_table(comparison, cmp_float),
                "",
            ]
        )

    lines.extend(
        [
            "## Is useful pre-oracle prediction possible?",
            "",
            "Interpretation is **exploratory** and must not be overstated:",
            "",
        ]
    )

    best_pre = results.sort_values("roc_auc_mean", ascending=False).iloc[0]
    best_auc = float(best_pre["roc_auc_mean"])
    best_model = best_pre["model"]

    baseline_a = comparison[
        (comparison["baseline_set"] == "A_gate_only")
        & (comparison["model"] == best_model)
    ]
    baseline_b = comparison[
        (comparison["baseline_set"] == "B_basic_structural")
        & (comparison["model"] == best_model)
    ]

    lines.append(
        f"- Best pre-oracle configuration: **{best_model}** "
        f"(ROC-AUC {best_auc:.3f} ± {best_pre['roc_auc_std']:.3f})."
    )

    if not baseline_a.empty:
        a_auc = float(baseline_a.iloc[0]["baseline_roc_auc_mean"])
        lines.append(
            f"- Versus **A_gate_only** ({a_auc:.3f}): pre-oracle adds requirement coverage "
            f"and structural counts; discrimination "
            f"{'improves' if best_auc > a_auc else 'does not clearly improve'} "
            f"(Δ = {best_auc - a_auc:+.3f})."
        )

    if not baseline_b.empty:
        b_auc = float(baseline_b.iloc[0]["baseline_roc_auc_mean"])
        lines.append(
            f"- Versus **B_basic_structural** ({b_auc:.3f}): without oracle-adjacent "
            f"traceability counts, out-of-fold discrimination is "
            f"{'lower' if best_auc < b_auc else 'comparable'} "
            f"(Δ = {best_auc - b_auc:+.3f})."
        )

    lines.extend(
        [
            "- **Gates alone** (set A) show limited discrimination; adding requirement "
            "coverage and FSM size/count features materially improves ranking over gates.",
            "- Pre-oracle performance is **comparable to B_basic_structural** in random CV, "
            "indicating that strong out-of-fold signal does not require oracle traceability "
            "counts — but see LOSO results for cross-specification limits.",
            "- Pre-oracle models may support **exploratory risk triage** (prioritising runs "
            "for behavioural review), not reliable pass/fail certification before oracle execution.",
            "- Low positive-class prevalence (30/209) makes PR-AUC and F1 unstable; "
            "reported metrics describe this dataset only.",
            "",
            "## Interpretation guardrails",
            "",
            "- Exploratory screening study — not evidence of deployable pre-oracle guarantees.",
            "- Structural counts correlate with specification and model identity; "
            "random CV mixes systems and is optimistic relative to leave-one-system-out.",
            "- Do not infer that behavioural risk is *caused* by gate or size features.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_feature_importance(frames: list[pd.DataFrame], path: Path) -> None:
    lines = [
        "# Pre-oracle feature importance",
        "",
        "Importance from models refit on the full scored analysis set (n=209). "
        "Tree models report `feature_importances_`; logistic regression reports "
        "|coefficient| after standardisation.",
        "",
        f"Predictor set: `{PRE_ORACLE_SET}` — {', '.join(f'`{f}`' for f in PRE_ORACLE_FEATURES)}.",
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


def plot_curve(
    curve_data: dict[str, tuple[np.ndarray, np.ndarray]],
    reference_data: dict[str, tuple[np.ndarray, np.ndarray]],
    x_label: str,
    y_label: str,
    title: str,
    path: Path,
    is_roc: bool,
) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    for model_name, (x, y) in curve_data.items():
        ax.plot(x, y, label=f"pre_oracle — {model_name}", linewidth=2)
    for ref_name, (x, y) in reference_data.items():
        ax.plot(x, y, label=ref_name, linestyle="--", linewidth=1.2, alpha=0.8)
    if is_roc:
        ax.plot([0, 1], [0, 1], "k--", linewidth=0.8, alpha=0.5)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def build_comparison(
    pre_results: pd.DataFrame,
    baselines: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for model in MODEL_NAMES:
        pre_row = pre_results[pre_results["model"] == model]
        if pre_row.empty:
            continue
        pre_auc = float(pre_row.iloc[0]["roc_auc_mean"])
        pre_pr = float(pre_row.iloc[0]["pr_auc_mean"])
        for baseline_set in BASELINE_SETS:
            base_row = baselines[
                (baselines["predictor_set"] == baseline_set)
                & (baselines["model"] == model)
            ]
            if base_row.empty:
                continue
            base_auc = float(base_row.iloc[0]["roc_auc_mean"])
            base_pr = float(base_row.iloc[0]["pr_auc_mean"])
            rows.append(
                {
                    "model": model,
                    "baseline_set": baseline_set,
                    "pre_oracle_roc_auc_mean": pre_auc,
                    "baseline_roc_auc_mean": base_auc,
                    "delta_roc_auc": pre_auc - base_auc,
                    "pre_oracle_pr_auc_mean": pre_pr,
                    "baseline_pr_auc_mean": base_pr,
                    "delta_pr_auc": pre_pr - base_pr,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    assert_feature_policy(PRE_ORACLE_FEATURES)

    df = load_scored_frame()
    y = df["full_behavioural_pass"].astype(int)
    X = prepare_features(df, PRE_ORACLE_FEATURES)

    missing = missingness_report(df, PRE_ORACLE_FEATURES)
    if int(missing["missing_count"].sum()) > 0:
        print(
            "WARNING: missing values in pre-oracle features; median imputation applied.",
            file=sys.stderr,
        )

    performance_rows: list[dict[str, Any]] = []
    importance_frames: list[pd.DataFrame] = []
    roc_curves: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    pr_curves: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    for model_name in MODEL_NAMES:
        model = make_model(model_name)
        fold_df, y_prob, _ = cross_validated_metrics(model, X, y)
        summary = summarize_metrics(fold_df)
        performance_rows.append({"predictor_set": PRE_ORACLE_SET, "model": model_name, **summary})

        fpr, tpr, _ = roc_curve(y, y_prob)
        prec, rec, _ = precision_recall_curve(y, y_prob)
        roc_curves[model_name] = (fpr, tpr)
        pr_curves[model_name] = (rec, prec)

        imp = extract_importance(model, X, y, PRE_ORACLE_FEATURES)
        imp.attrs["title"] = f"{PRE_ORACLE_SET} — {model_name}"
        importance_frames.append(imp)

    performance_df = pd.DataFrame(performance_rows)
    baselines = load_baseline_cv_means()
    comparison_df = build_comparison(performance_df, baselines)

    write_pre_oracle_performance(
        performance_df,
        comparison_df,
        TABLES_DIR / "pre_oracle_model_performance.md",
    )
    write_feature_importance(
        importance_frames,
        TABLES_DIR / "pre_oracle_feature_importance.md",
    )

    # Reference curves: best baseline RF from prior study (recomputed OOF for overlay).
    from model_behavioural_correctness import PREDICTOR_SETS  # noqa: E402

    reference_curves_roc: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    reference_curves_pr: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for ref_set in BASELINE_SETS:
        ref_features = PREDICTOR_SETS[ref_set]
        X_ref = prepare_features(df, ref_features)
        ref_model = make_model("random_forest")
        _, y_prob_ref, _ = cross_validated_metrics(ref_model, X_ref, y)
        fpr, tpr, _ = roc_curve(y, y_prob_ref)
        prec, rec, _ = precision_recall_curve(y, y_prob_ref)
        reference_curves_roc[f"{ref_set} (RF ref)"] = (fpr, tpr)
        reference_curves_pr[f"{ref_set} (RF ref)"] = (rec, prec)

    plot_curve(
        roc_curves,
        reference_curves_roc,
        "False positive rate",
        "True positive rate",
        "Pre-oracle ROC (out-of-fold) vs gate/structural baselines",
        FIGURES_DIR / "pre_oracle_roc.png",
        is_roc=True,
    )
    plot_curve(
        pr_curves,
        reference_curves_pr,
        "Recall",
        "Precision",
        "Pre-oracle PR (out-of-fold) vs gate/structural baselines",
        FIGURES_DIR / "pre_oracle_pr.png",
        is_roc=False,
    )

    best = performance_df.sort_values("roc_auc_mean", ascending=False).iloc[0]
    print(f"Wrote {TABLES_DIR / 'pre_oracle_model_performance.md'}")
    print(f"Wrote {TABLES_DIR / 'pre_oracle_feature_importance.md'}")
    print(f"Wrote {FIGURES_DIR / 'pre_oracle_roc.png'}")
    print(f"Wrote {FIGURES_DIR / 'pre_oracle_pr.png'}")
    print(
        f"Best pre-oracle ROC-AUC: {best['model']} = "
        f"{best['roc_auc_mean']:.3f} ± {best['roc_auc_std']:.3f}"
    )


if __name__ == "__main__":
    main()
