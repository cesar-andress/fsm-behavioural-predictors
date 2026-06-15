#!/usr/bin/env python3
"""Publication-style figures for strengthened-stats outputs."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from figure_style import INK, INK_MID, apply_figure_style, save_figure, style_axes  # noqa: E402
from strengthen_io import FIGURES_DIR, TABLES_DIR, ensure_output_dirs, load_predictions  # noqa: E402

FAMILY_B = "B_basic_structural"


def plot_definability_map() -> Path:
    audit = pd.read_csv(TABLES_DIR / "definability_audit.csv")
    apply_figure_style()
    fig, ax = plt.subplots(figsize=(8.0, 5.5))
    colors = [
        "#444444" if definable else "#cccccc"
        for definable in audit["loso_roc_auc_definable"]
    ]
    ax.barh(audit["system_id"], audit["prevalence"], color=colors, edgecolor=INK, linewidth=0.6)
    ax.set_xlabel("Positive-class prevalence (full_behavioural_pass)")
    ax.set_ylabel("system_id")
    ax.set_title("LOSO ROC-AUC definability by system", loc="left", fontweight="bold")
    style_axes(ax, ink=True)
    ax.text(
        0.99,
        0.02,
        "Dark = dual-class (ROC-AUC definable); light = single-class",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8.5,
        color=INK_MID,
    )
    fig.tight_layout()
    path = FIGURES_DIR / "definability_map.png"
    save_figure(fig, path)
    return path


def plot_bootstrap_delta_distribution() -> Path:
    boot = pd.read_csv(TABLES_DIR / "bootstrap_delta_iterations.csv")
    summary = pd.read_csv(TABLES_DIR / "bootstrap_delta.csv")
    family_b = boot[boot["predictor_set"] == FAMILY_B]["delta"].dropna()
    apply_figure_style()
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.hist(family_b, bins=40, color="#666666", edgecolor=INK, linewidth=0.5)
    row = summary[summary["predictor_set"] == FAMILY_B].iloc[0]
    ax.axvline(row["delta_median_bootstrap"], color=INK, linestyle="-", linewidth=1.2, label="median Δ")
    ax.axvline(row["delta_p025"], color=INK, linestyle="--", linewidth=1.0, label="2.5–97.5%")
    ax.axvline(row["delta_p975"], color=INK, linestyle="--", linewidth=1.0)
    ax.set_xlabel("Bootstrap Δ = CV ROC-AUC − LOSO ROC-AUC")
    ax.set_ylabel("Count")
    ax.set_title("Family B / RF cluster-bootstrap Δ", loc="left", fontweight="bold")
    ax.legend(frameon=True, fontsize=8.5)
    style_axes(ax, ink=True)
    fig.tight_layout()
    path = FIGURES_DIR / "bootstrap_delta_distribution.png"
    save_figure(fig, path)
    return path


def plot_cv_seed_distribution_family_b() -> Path:
    oof = load_predictions("repeated_seed_oof_predictions")
    from metrics_utils import roc_auc_safe

    sub = oof[
        (oof["predictor_set"] == FAMILY_B) & (oof["model"] == "random_forest")
    ]
    seed_aucs = (
        sub.groupby("seed")
        .apply(
            lambda g: roc_auc_safe(g["y_true"].to_numpy(), g["y_score"].to_numpy()),
            include_groups=False,
        )
        .dropna()
    )
    apply_figure_style()
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.hist(seed_aucs, bins=20, color="#555555", edgecolor=INK, linewidth=0.5)
    ax.axvline(seed_aucs.median(), color=INK, linestyle="-", linewidth=1.2, label=f"median={seed_aucs.median():.3f}")
    ax.set_xlabel("Pooled OOF ROC-AUC")
    ax.set_ylabel("Seed count")
    ax.set_title("Family B / RF repeated-seed CV distribution", loc="left", fontweight="bold")
    ax.legend(frameon=True, fontsize=8.5)
    style_axes(ax, ink=True)
    fig.tight_layout()
    path = FIGURES_DIR / "cv_seed_distribution_family_b.png"
    save_figure(fig, path)
    return path


def plot_prevalence_baseline_comparison() -> Path:
    table6 = pd.read_csv(TABLES_DIR / "table6_strengthened.csv")
    subset = table6[
        table6["predictor_family"].isin(
            ["Family B graph tallies", "prevalence-only baseline"]
        )
    ]
    apply_figure_style()
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    x = np.arange(len(subset))
    width = 0.35
    cv_vals = subset["cv_roc_auc_mean"].astype(float)
    loso_vals = subset["loso_roc_auc"].astype(float)
    ax.bar(x - width / 2, cv_vals, width, label="CV mean", color="#333333", edgecolor=INK)
    ax.bar(x + width / 2, loso_vals, width, label="LOSO μ", color="#999999", edgecolor=INK)
    ax.set_xticks(x)
    ax.set_xticklabels(subset["predictor_family"], rotation=15, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("ROC-AUC")
    ax.set_title("Family B vs prevalence-only baseline", loc="left", fontweight="bold")
    ax.legend(frameon=True, fontsize=8.5)
    style_axes(ax, ink=True)
    fig.tight_layout()
    path = FIGURES_DIR / "prevalence_baseline_comparison.png"
    save_figure(fig, path)
    return path


def main() -> None:
    ensure_output_dirs()
    paths = [
        plot_definability_map(),
        plot_bootstrap_delta_distribution(),
        plot_cv_seed_distribution_family_b(),
        plot_prevalence_baseline_comparison(),
    ]
    for path in paths:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
