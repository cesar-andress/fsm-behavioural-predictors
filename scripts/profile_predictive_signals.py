#!/usr/bin/env python3
"""
Descriptive and predictive-signal profiling for SQJ 2026.

Reads data/processed/master_analysis_dataset.csv.
Writes markdown reports and figures under results/.
No hypothesis testing, no ML models, no LLM inference.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import pandas as pd
from scipy.stats import pointbiserialr, spearmanr

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from figure_style import (  # noqa: E402
    FIG_BASE_SIZE,
    FIG_LEGEND_SIZE,
    FIG_TICK_SIZE,
    FIG_TITLE_SIZE,
    GRAY_DASH,
    GRAY_FILL_MID,
    GRAY_STROKE,
    INK,
    INK_MID,
    TEXT_ON_WHITE,
    TICK_ON_WHITE,
    _gray,
    add_panel_label,
    apply_figure_style,
    gate_label,
    heatmap_cmap,
    model_display,
    save_figure,
    style_axes,
)

ROOT = Path(__file__).resolve().parents[1]
MASTER_CSV = ROOT / "data" / "processed" / "master_analysis_dataset.csv"
TABLES_DIR = ROOT / "results" / "tables"
FIGURES_DIR = ROOT / "results" / "figures"

BOOL_COLUMNS = [
    "g1_pass",
    "g2_pass",
    "g3_pass",
    "g3a_pass",
    "full_behavioural_pass",
    "behaviourally_scored",
]

BINARY_PREDICTORS = ["g2_pass", "g3_pass", "g3a_pass"]
NUMERIC_PREDICTORS = [
    "requirement_coverage",
    "n_states",
    "n_events",
    "n_transitions",
    "n_unreachable_states",
    "missing_transitions",
    "extra_transitions",
]
ALL_PREDICTORS = BINARY_PREDICTORS + NUMERIC_PREDICTORS

GROUP_DIMENSIONS = ["model", "system_id", "g2_pass", "g3_pass", "g3a_pass"]

EXPECTED_OUTPUTS = [
    TABLES_DIR / "target_distribution.md",
    TABLES_DIR / "descriptive_profile.md",
    TABLES_DIR / "predictive_signal_profile.md",
    TABLES_DIR / "profile_signals_validation.md",
    FIGURES_DIR / "bpr_by_gate.png",
    FIGURES_DIR / "bpr_by_model.png",
    FIGURES_DIR / "bpr_by_system.png",
]


def load_master() -> pd.DataFrame:
    if not MASTER_CSV.is_file():
        print(f"ERROR: master dataset not found: {MASTER_CSV}", file=sys.stderr)
        print("Run: make build-master", file=sys.stderr)
        raise SystemExit(1)

    df = pd.read_csv(MASTER_CSV)
    for col in BOOL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].map(
                {"true": True, "false": False, True: True, False: False}
            )
    return df


def fmt_rate(num: float | int, den: float | int) -> str:
    if den == 0:
        return "—"
    return f"{100.0 * num / den:.1f}%"


def fmt_float(value: float | None, digits: int = 3) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "—"
    return f"{value:.{digits}f}"


def bpr_summary(series: pd.Series) -> dict[str, float | int | None]:
    valid = series.dropna()
    if valid.empty:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "std": None,
            "min": None,
            "max": None,
        }
    return {
        "n": int(len(valid)),
        "mean": float(valid.mean()),
        "median": float(valid.median()),
        "std": float(valid.std(ddof=1)) if len(valid) > 1 else 0.0,
        "min": float(valid.min()),
        "max": float(valid.max()),
    }


def group_profile(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, group in df.groupby(dimension, dropna=False, sort=True):
        scored = group[group["behaviourally_scored"]]
        label = "missing" if pd.isna(key) else str(key)
        bpr = bpr_summary(scored["behavioral_pass_rate"])
        rows.append(
            {
                "group": label,
                "n_runs": len(group),
                "behaviourally_scored_n": int(group["behaviourally_scored"].sum()),
                "mean_bpr": bpr["mean"],
                "median_bpr": bpr["median"],
                "full_pass_n": int(scored["full_behavioural_pass"].sum(skipna=True)),
                "full_pass_rate_scored": (
                    float(scored["full_behavioural_pass"].mean())
                    if len(scored)
                    else None
                ),
                "mean_requirement_coverage": group["requirement_coverage"].mean(),
                "mean_n_states": group["n_states"].mean(),
                "mean_n_transitions": group["n_transitions"].mean(),
                "mean_missing_transitions": group["missing_transitions"].mean(),
                "mean_extra_transitions": group["extra_transitions"].mean(),
            }
        )
    return pd.DataFrame(rows)


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
            if col in float_cols and val is not None and not pd.isna(val):
                cells.append(fmt_float(float(val)))
            elif isinstance(val, float) and not pd.isna(val):
                cells.append(fmt_float(val))
            else:
                cells.append(str(val))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_target_distribution(df: pd.DataFrame, path: Path) -> None:
    n = len(df)
    scored = df[df["behaviourally_scored"]]
    g2_scored = scored[scored["g2_pass"] == True]  # noqa: E712
    bpr = bpr_summary(scored["behavioral_pass_rate"])
    full_pass_scored = int(scored["full_behavioural_pass"].sum(skipna=True))
    full_pass_g2 = int(g2_scored["full_behavioural_pass"].sum(skipna=True))

    lines = [
        "# Target distribution",
        "",
        "Descriptive summary of behavioural outcomes from `master_analysis_dataset.csv`.",
        "No hypothesis tests; counts and rates only.",
        "",
        "## Cohort counts",
        "",
        "| Metric | Count | Rate |",
        "|--------|------:|-----:|",
        f"| Total runs | {n} | 100.0% |",
        f"| `behaviourally_scored` | {len(scored)} | {fmt_rate(len(scored), n)} |",
        f"| `full_behavioural_pass` (all runs) | {int(df['full_behavioural_pass'].sum(skipna=True))} | {fmt_rate(int(df['full_behavioural_pass'].sum(skipna=True)), n)} |",
        f"| `full_behavioural_pass` (scored runs) | {full_pass_scored} | {fmt_rate(full_pass_scored, len(scored))} |",
        f"| `full_behavioural_pass` (G2-pass, scored) | {full_pass_g2} | {fmt_rate(full_pass_g2, len(g2_scored))} |",
        "",
        "## `behavioral_pass_rate` summary (scored runs only)",
        "",
        "| Statistic | Value |",
        "|-----------|------:|",
        f"| n | {bpr['n']} |",
        f"| mean | {fmt_float(bpr['mean'])} |",
        f"| median | {fmt_float(bpr['median'])} |",
        f"| std | {fmt_float(bpr['std'])} |",
        f"| min | {fmt_float(bpr['min'])} |",
        f"| max | {fmt_float(bpr['max'])} |",
        "",
        "## `full_behavioural_pass` among scored runs",
        "",
        "| Value | Count | Proportion |",
        "|-------|------:|-----------:|",
    ]
    for value, label in [(True, "true"), (False, "false")]:
        count = int((scored["full_behavioural_pass"] == value).sum())
        lines.append(f"| {label} | {count} | {fmt_rate(count, len(scored))} |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Behaviourally non-scored runs (`behaviourally_scored=false`, n="
            f"{n - len(scored)}) have empty BPR; they are excluded from BPR summaries.",
            "- G2-pass scored stratum: runs with `behaviourally_scored=true` and `g2_pass=true` "
            f"(n={len(g2_scored)}).",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_descriptive_profile(df: pd.DataFrame, path: Path) -> None:
    scored = df[df["behaviourally_scored"]]
    lines = [
        "# Descriptive profile",
        "",
        "Grouped descriptive statistics for structural and behavioural variables.",
        "BPR statistics use behaviourally scored runs within each group.",
        "",
        f"**Scored analysis set:** n={len(scored)} of {len(df)} total runs.",
        "",
    ]
    float_cols = {
        "mean_bpr",
        "median_bpr",
        "full_pass_rate_scored",
        "mean_requirement_coverage",
        "mean_n_states",
        "mean_n_transitions",
        "mean_missing_transitions",
        "mean_extra_transitions",
    }
    for dimension in GROUP_DIMENSIONS:
        profile = group_profile(df, dimension)
        lines.append(f"## By `{dimension}`")
        lines.append("")
        lines.append(markdown_table(profile, float_cols))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def association_numeric(
    df: pd.DataFrame, predictor: str, target_continuous: str, target_binary: str
) -> dict[str, Any]:
    subset = df[df[predictor].notna() & df[target_continuous].notna()].copy()
    missingness = len(df) - len(subset)
    out: dict[str, Any] = {
        "predictor": predictor,
        "predictor_type": "numeric",
        "n_complete": len(subset),
        "missingness": missingness,
        "spearman_bpr": None,
        "spearman_bpr_p": None,
        "spearman_full_pass": None,
        "spearman_full_pass_p": None,
        "mean_bpr": bpr_summary(subset[target_continuous])["mean"],
        "median_bpr": bpr_summary(subset[target_continuous])["median"],
        "full_pass_rate": float(subset[target_binary].mean()) if len(subset) else None,
    }
    if len(subset) >= 3 and subset[predictor].nunique() > 1:
        rho_bpr, p_bpr = spearmanr(subset[predictor], subset[target_continuous])
        out["spearman_bpr"] = float(rho_bpr)
        out["spearman_bpr_p"] = float(p_bpr)
        if subset[target_binary].nunique() > 1:
            rho_fp, p_fp = spearmanr(subset[predictor], subset[target_binary].astype(int))
            out["spearman_full_pass"] = float(rho_fp)
            out["spearman_full_pass_p"] = float(p_fp)
    return out


def association_binary(
    df: pd.DataFrame, predictor: str, target_continuous: str, target_binary: str
) -> dict[str, Any]:
    subset = df[df[predictor].notna() & df[target_continuous].notna()].copy()
    missingness = len(df) - len(subset)
    out: dict[str, Any] = {
        "predictor": predictor,
        "predictor_type": "binary",
        "n_complete": len(subset),
        "missingness": missingness,
        "mean_bpr_true": None,
        "mean_bpr_false": None,
        "mean_bpr_diff": None,
        "full_pass_rate_true": None,
        "full_pass_rate_false": None,
        "full_pass_rate_diff": None,
        "point_biserial_bpr": None,
        "point_biserial_bpr_p": None,
        "point_biserial_full_pass": None,
        "point_biserial_full_pass_p": None,
    }
    if subset[predictor].nunique() < 2:
        return out

    true_mask = subset[predictor] == True  # noqa: E712
    false_mask = ~true_mask
    bpr_true = subset.loc[true_mask, target_continuous]
    bpr_false = subset.loc[false_mask, target_continuous]
    fp_true = subset.loc[true_mask, target_binary]
    fp_false = subset.loc[false_mask, target_binary]

    out["mean_bpr_true"] = float(bpr_true.mean()) if len(bpr_true) else None
    out["mean_bpr_false"] = float(bpr_false.mean()) if len(bpr_false) else None
    if out["mean_bpr_true"] is not None and out["mean_bpr_false"] is not None:
        out["mean_bpr_diff"] = out["mean_bpr_true"] - out["mean_bpr_false"]
    out["full_pass_rate_true"] = float(fp_true.mean()) if len(fp_true) else None
    out["full_pass_rate_false"] = float(fp_false.mean()) if len(fp_false) else None
    if out["full_pass_rate_true"] is not None and out["full_pass_rate_false"] is not None:
        out["full_pass_rate_diff"] = out["full_pass_rate_true"] - out["full_pass_rate_false"]

    if len(subset) >= 3:
        r_bpr, p_bpr = pointbiserialr(subset[predictor].astype(int), subset[target_continuous])
        out["point_biserial_bpr"] = float(r_bpr)
        out["point_biserial_bpr_p"] = float(p_bpr)
        if subset[target_binary].nunique() > 1:
            r_fp, p_fp = pointbiserialr(
                subset[predictor].astype(int), subset[target_binary].astype(int)
            )
            out["point_biserial_full_pass"] = float(r_fp)
            out["point_biserial_full_pass_p"] = float(p_fp)
    return out


def write_predictive_signal_profile(df: pd.DataFrame, path: Path) -> None:
    scored = df[df["behaviourally_scored"]].copy()
    records: list[dict[str, Any]] = []
    for predictor in ALL_PREDICTORS:
        if predictor in BINARY_PREDICTORS:
            records.append(
                association_binary(
                    scored, predictor, "behavioral_pass_rate", "full_behavioural_pass"
                )
            )
        else:
            records.append(
                association_numeric(
                    scored, predictor, "behavioral_pass_rate", "full_behavioural_pass"
                )
            )

    binary_df = pd.DataFrame([r for r in records if r["predictor_type"] == "binary"])
    numeric_df = pd.DataFrame([r for r in records if r["predictor_type"] == "numeric"])

    lines = [
        "# Predictive signal profile",
        "",
        "First-pass association between candidate structural predictors and behavioural outcomes.",
        f"**Analysis set:** behaviourally scored runs only (n={len(scored)}).",
        "",
        "Conservative descriptive associations only — **no hypothesis tests reported** "
        "(p-values shown for transparency; not used for confirmatory claims).",
        "",
        "## Binary predictors",
        "",
        "Point-biserial correlation with `behavioral_pass_rate` and `full_behavioural_pass`; "
        "group mean BPR and full-pass rate differences (true − false).",
        "",
    ]
    if not binary_df.empty:
        display = binary_df[
            [
                "predictor",
                "n_complete",
                "missingness",
                "mean_bpr_true",
                "mean_bpr_false",
                "mean_bpr_diff",
                "full_pass_rate_true",
                "full_pass_rate_false",
                "full_pass_rate_diff",
                "point_biserial_bpr",
                "point_biserial_full_pass",
            ]
        ]
        lines.append(markdown_table(display, set(display.columns) - {"predictor", "n_complete", "missingness"}))
    lines.extend(
        [
            "",
            "## Numeric predictors",
            "",
            "Spearman rank correlation with `behavioral_pass_rate` and `full_behavioural_pass`.",
            "",
        ]
    )
    if not numeric_df.empty:
        display = numeric_df[
            [
                "predictor",
                "n_complete",
                "missingness",
                "mean_bpr",
                "median_bpr",
                "full_pass_rate",
                "spearman_bpr",
                "spearman_full_pass",
            ]
        ]
        lines.append(markdown_table(display, set(display.columns) - {"predictor", "n_complete", "missingness"}))
    lines.extend(
        [
            "",
            "## Interpretation guardrails",
            "",
            "- Associations describe frozen-data patterns only; causality is not implied.",
            "- Several predictors are structurally related (e.g., G2–G3a gates); multicollinearity "
            "will be addressed in later modelling stages.",
            "- Non-scored runs are excluded from this profile by design.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_bpr_by_gate(scored: pd.DataFrame, path: Path) -> None:
    apply_figure_style()
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2), sharey=True)
    gates = ["g2_pass", "g3_pass", "g3a_pass"]
    panel_labels = ["A", "B", "C"]
    box_face = ["white", "#777777"]
    box_hatch = ["///", ""]
    for ax, gate, panel in zip(axes, gates, panel_labels):
        subset = scored[scored[gate].notna()]
        data = [
            subset.loc[subset[gate] == False, "behavioral_pass_rate"].dropna(),  # noqa: E712
            subset.loc[subset[gate] == True, "behavioral_pass_rate"].dropna(),  # noqa: E712
        ]
        bp = ax.boxplot(
            data,
            tick_labels=["fail", "pass"],
            showfliers=True,
            patch_artist=True,
            widths=0.55,
            medianprops={"color": INK, "linewidth": 1.8},
            whiskerprops={"color": INK_MID, "linewidth": 1.0},
            capprops={"color": INK_MID, "linewidth": 1.0},
            flierprops={
                "marker": "o",
                "markersize": 4,
                "markerfacecolor": "white",
                "markeredgecolor": INK,
                "alpha": 0.85,
            },
        )
        for patch, face, hatch in zip(bp["boxes"], box_face, box_hatch):
            patch.set_facecolor(face)
            patch.set_hatch(hatch)
            patch.set_alpha(1.0)
            patch.set_edgecolor(INK)
            patch.set_linewidth(1.1)
        for idx, median in enumerate(bp["medians"]):
            median.set_color("#ffffff" if idx % 2 else INK)
            median.set_linewidth(1.8)
        ax.set_title(gate_label(gate), fontsize=FIG_TITLE_SIZE, fontweight="bold", pad=8)
        ax.set_xlabel("Gate outcome (categorical: fail / pass)", fontsize=FIG_BASE_SIZE)
        ax.set_ylim(0, 1.05)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        style_axes(ax, ink=True)
        ax.tick_params(labelsize=FIG_TICK_SIZE)
        add_panel_label(ax, panel)
    axes[0].set_ylabel("Behavioral pass rate (BPR)", fontsize=FIG_BASE_SIZE)
    legend_handles = [
        Patch(
            facecolor="white",
            edgecolor=INK,
            hatch="///",
            linewidth=1.1,
            label="Gate fail",
        ),
        Patch(
            facecolor="#777777",
            edgecolor=INK,
            linewidth=1.1,
            label="Gate pass",
        ),
    ]
    leg = fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=2,
        bbox_to_anchor=(0.5, -0.01),
        frameon=True,
        fancybox=False,
        edgecolor=INK_MID,
        fontsize=FIG_LEGEND_SIZE,
    )
    for text in leg.get_texts():
        text.set_color(INK)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save_figure(fig, path)


def plot_bpr_by_model(scored: pd.DataFrame, path: Path) -> None:
    apply_figure_style()
    models = sorted(scored["model"].unique())
    labels = [model_display(m) for m in models]
    data = [scored.loc[scored["model"] == m, "behavioral_pass_rate"].dropna() for m in models]
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    bp = ax.boxplot(
        data,
        tick_labels=labels,
        showfliers=True,
        patch_artist=True,
        widths=0.55,
        medianprops={"color": INK, "linewidth": 1.8},
        whiskerprops={"color": INK_MID, "linewidth": 1.0},
        capprops={"color": INK_MID, "linewidth": 1.0},
        flierprops={
            "marker": "o",
            "markersize": 4,
            "markerfacecolor": "white",
            "markeredgecolor": INK,
            "alpha": 0.85,
        },
    )
    for patch in bp["boxes"]:
        patch.set_facecolor("#777777")
        patch.set_alpha(1.0)
        patch.set_edgecolor(INK)
        patch.set_linewidth(1.1)
    ax.set_ylabel("Behavioral pass rate (BPR)", fontsize=FIG_BASE_SIZE)
    ax.set_xlabel("Synthesis source (model)", fontsize=FIG_BASE_SIZE)
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    style_axes(ax, ink=True)
    ax.tick_params(labelsize=FIG_TICK_SIZE)
    plt.setp(ax.get_xticklabels(), rotation=22, ha="right")
    fig.tight_layout()
    save_figure(fig, path)


def plot_bpr_by_system(scored: pd.DataFrame, path: Path) -> None:
    """Horizontal median-BPR chart: bar length + numeric labels (uniform fill, black ink)."""
    apply_figure_style()
    summary = (
        scored.groupby("system_id")["behavioral_pass_rate"]
        .median()
        .sort_values(ascending=True)
    )
    n_systems = len(summary)
    fig_h = max(8.2, 0.52 * n_systems + 2.0)
    fig, ax = plt.subplots(figsize=(10.0, fig_h))
    y_pos = np.arange(n_systems)
    bars = ax.barh(
        y_pos,
        summary.values,
        color=INK,
        edgecolor=INK,
        linewidth=1.0,
        height=0.50,
    )
    ax.set_yticks(y_pos)
    ax.set_yticklabels(
        summary.index,
        fontsize=FIG_TICK_SIZE + 0.5,
        color=INK,
        fontweight="semibold",
    )
    for bar, val in zip(bars, summary.values):
        val_f = float(val)
        inside = val_f >= 0.18
        label_x = val_f - 0.04 if inside else min(val_f + 0.03, 1.04)
        ax.text(
            label_x,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.2f}",
            va="center",
            ha="right" if inside else "left",
            fontsize=FIG_TICK_SIZE + 0.5,
            fontweight="bold",
            color="#ffffff" if inside else INK,
            clip_on=False,
        )
    ax.set_xlabel(
        "Median behavioral pass rate, BPR (oracle-suite pass fraction; 0 = none, 1 = all checks pass)",
        fontsize=FIG_BASE_SIZE + 0.5,
        color=INK,
        fontweight="semibold",
    )
    ax.set_ylabel(
        "Requirement system (system_id; one bar per specification)",
        fontsize=FIG_BASE_SIZE + 0.5,
        color=INK,
        fontweight="semibold",
    )
    ax.text(
        0.01,
        0.01,
        "Descriptive profiling only — observed BPR from oracle suites; not a predictive model input.",
        transform=ax.transAxes,
        fontsize=FIG_TICK_SIZE - 0.5,
        color=INK_MID,
        ha="left",
        va="bottom",
        fontstyle="italic",
    )
    ax.set_xlim(0, 1.12)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    style_axes(ax, ink=True)
    ax.tick_params(axis="x", labelsize=FIG_TICK_SIZE + 0.5, colors=INK, pad=6)
    ax.tick_params(axis="y", length=0, pad=10)
    ax.grid(axis="x", linestyle="-", linewidth=0.6, color="#888888", alpha=0.55)
    ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.31, right=0.97, top=0.98, bottom=0.10)
    save_figure(fig, path)


def write_validation_note(paths: list[Path]) -> None:
    out = TABLES_DIR / "profile_signals_validation.md"
    check_paths = [path for path in paths if path != out]

    lines = [
        "# Predictive signal profiling — validation",
        "",
        "All outputs from `scripts/profile_predictive_signals.py` were checked after generation.",
        "",
        "| Output | Status | Size (bytes) |",
        "|--------|--------|-------------:|",
    ]
    all_ok = True
    for path in check_paths:
        if path.is_file():
            size = path.stat().st_size
            status = "OK" if size > 0 else "EMPTY"
            if size == 0:
                all_ok = False
        else:
            size = 0
            status = "MISSING"
            all_ok = False
        rel = path.relative_to(ROOT)
        lines.append(f"| `{rel}` | {status} | {size} |")

    lines.append(f"| `{out.relative_to(ROOT)}` | OK | — |")
    lines.extend(
        [
            "",
            f"**Overall:** {'all outputs generated' if all_ok else 'one or more outputs missing or empty'}.",
            "",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_master()
    scored = df[df["behaviourally_scored"]]

    write_target_distribution(df, TABLES_DIR / "target_distribution.md")
    write_descriptive_profile(df, TABLES_DIR / "descriptive_profile.md")
    write_predictive_signal_profile(df, TABLES_DIR / "predictive_signal_profile.md")

    plot_bpr_by_gate(scored, FIGURES_DIR / "bpr_by_gate.png")
    plot_bpr_by_model(scored, FIGURES_DIR / "bpr_by_model.png")
    plot_bpr_by_system(scored, FIGURES_DIR / "bpr_by_system.png")

    write_validation_note(EXPECTED_OUTPUTS)

    for path in EXPECTED_OUTPUTS:
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
