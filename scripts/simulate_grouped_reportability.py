#!/usr/bin/env python3
"""Monte Carlo simulation of grouped outcome sparsity and pair-partition AUC reportability."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from figure_style import INK, INK_MID, apply_figure_style, save_figure, style_axes  # noqa: E402
from metrics_utils import group_definability_table, roc_auc_pair_counts  # noqa: E402
from repro_config import RANDOM_STATE  # noqa: E402
from strengthen_io import FIGURES_DIR, TABLES_DIR, ensure_output_dirs, markdown_table, write_csv_md  # noqa: E402

N_GROUPS_GRID = [4, 8, 12, 16]
GROUP_SIZE_GRID = [8, 16]
GLOBAL_PREVALENCE_GRID = [0.05, 0.10, 0.15, 0.20]
PREVALENCE_HETEROGENEITY_GRID = [0.0, 0.5, 1.0, 2.0]
WITHIN_SIGNAL_GRID = [0.0, 0.5, 1.0, 2.0]
N_REPLICATES = 100


def _logit(p: float) -> float:
    p = float(np.clip(p, 1e-6, 1.0 - 1e-6))
    return float(np.log(p / (1.0 - p)))


def _expit(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def simulate_cohort(
    *,
    n_groups: int,
    group_size: int,
    global_prevalence: float,
    prevalence_heterogeneity: float,
    within_signal: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return labels, structural scores, prevalence-only scores, and group ids."""
    y_list: list[int] = []
    score_list: list[float] = []
    prev_list: list[float] = []
    group_list: list[str] = []

    base_logit = _logit(global_prevalence)
    for g in range(n_groups):
        group_logit = base_logit + rng.normal(0.0, prevalence_heterogeneity)
        pi_g = float(np.clip(_expit(np.array([group_logit]))[0], 0.01, 0.99))
        group_id = f"g{g:03d}"

        for _ in range(group_size):
            latent = group_logit + rng.normal(0.0, within_signal)
            prob = float(_expit(np.array([latent]))[0])
            label = int(rng.random() < prob)
            y_list.append(label)
            score_list.append(latent)
            prev_list.append(pi_g)
            group_list.append(group_id)

    return (
        np.asarray(y_list, dtype=int),
        np.asarray(score_list, dtype=float),
        np.asarray(prev_list, dtype=float),
        np.asarray(group_list),
    )


def cohort_metrics(
    y: np.ndarray,
    structural_score: np.ndarray,
    prevalence_score: np.ndarray,
    groups: np.ndarray,
) -> dict[str, float]:
    frame = pd.DataFrame({"group_id": groups, "y": y})
    definability = group_definability_table(frame, "group_id", "y")
    ndc = int(definability["dual_class"].sum())
    n_groups = len(definability)
    p_dual = ndc / n_groups if n_groups else float("nan")

    structural = roc_auc_pair_counts(y, structural_score, groups)
    prevalence = roc_auc_pair_counts(y, prevalence_score, groups)

    return {
        "ndc": float(ndc),
        "n_groups": float(n_groups),
        "p_dual_class_group": p_dual,
        "structural_auc_pooled": structural["auc_pooled"],
        "structural_auc_within": structural["auc_within"],
        "structural_auc_cross": structural["auc_cross"],
        "prevalence_auc_pooled": prevalence["auc_pooled"],
        "prevalence_auc_within": prevalence["auc_within"],
        "prevalence_auc_cross": prevalence["auc_cross"],
        "n_within_pairs": structural["n_within_pairs"],
        "n_cross_pairs": structural["n_cross_pairs"],
        "share_within_pairs": structural["share_within_pairs"],
    }


def run_grid(rng: np.random.Generator) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for n_groups in N_GROUPS_GRID:
        for group_size in GROUP_SIZE_GRID:
            for global_prevalence in GLOBAL_PREVALENCE_GRID:
                for heterogeneity in PREVALENCE_HETEROGENEITY_GRID:
                    for within_signal in WITHIN_SIGNAL_GRID:
                        rep_metrics: list[dict[str, float]] = []
                        for _ in range(N_REPLICATES):
                            y, structural, prevalence, groups = simulate_cohort(
                                n_groups=n_groups,
                                group_size=group_size,
                                global_prevalence=global_prevalence,
                                prevalence_heterogeneity=heterogeneity,
                                within_signal=within_signal,
                                rng=rng,
                            )
                            rep_metrics.append(cohort_metrics(y, structural, prevalence, groups))

                        agg: dict[str, Any] = {
                            "n_groups": n_groups,
                            "group_size": group_size,
                            "global_prevalence": global_prevalence,
                            "prevalence_heterogeneity": heterogeneity,
                            "within_signal": within_signal,
                            "n_replicates": N_REPLICATES,
                        }
                        for key in rep_metrics[0]:
                            values = np.array([m[key] for m in rep_metrics], dtype=float)
                            agg[f"{key}_mean"] = float(np.nanmean(values))
                            agg[f"{key}_sd"] = float(np.nanstd(values, ddof=1))
                        rows.append(agg)
    return pd.DataFrame(rows)


def plot_ndc_vs_heterogeneity(grid_df: pd.DataFrame) -> Path:
    apply_figure_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5), sharey=True)

    for ax, group_size in zip(axes, GROUP_SIZE_GRID):
        sub = grid_df[
            (grid_df["group_size"] == group_size)
            & (grid_df["global_prevalence"] == 0.10)
            & (grid_df["within_signal"] == 1.0)
            & (grid_df["n_groups"] == 12)
        ].sort_values("prevalence_heterogeneity")
        ax.plot(
            sub["prevalence_heterogeneity"],
            sub["ndc_mean"],
            marker="o",
            color="#333333",
            linewidth=1.2,
        )
        ax.set_title(f"group_size={group_size}", loc="left", fontweight="bold")
        ax.set_xlabel("Prevalence heterogeneity (logit SD)")
        ax.set_ylabel("Expected ndc (dual-class groups)")
        style_axes(ax, ink=True)

    fig.suptitle(
        "Simulated ndc vs prevalence heterogeneity (π=0.10, 12 groups, within_signal=1.0)",
        fontsize=10.5,
        fontweight="bold",
        x=0.02,
        ha="left",
    )
    fig.tight_layout()
    path = FIGURES_DIR / "sim_ndc_vs_prevalence_heterogeneity.png"
    save_figure(fig, path)
    return path


def plot_auc_components(grid_df: pd.DataFrame) -> Path:
    apply_figure_style()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5))

    panel_specs = [
        ("structural", "Structural score (within-group signal)"),
        ("prevalence", "Prevalence-only score"),
    ]
    subset = grid_df[
        (grid_df["n_groups"] == 12)
        & (grid_df["group_size"] == 16)
        & (grid_df["global_prevalence"] == 0.10)
        & (grid_df["within_signal"] == 1.0)
    ].sort_values("prevalence_heterogeneity")

    for ax, (prefix, title) in zip(axes, panel_specs):
        ax.plot(
            subset["prevalence_heterogeneity"],
            subset[f"{prefix}_auc_pooled_mean"],
            marker="o",
            label="pooled",
            color="#111111",
        )
        ax.plot(
            subset["prevalence_heterogeneity"],
            subset[f"{prefix}_auc_within_mean"],
            marker="s",
            linestyle="--",
            label="within-group pairs",
            color="#555555",
        )
        ax.plot(
            subset["prevalence_heterogeneity"],
            subset[f"{prefix}_auc_cross_mean"],
            marker="^",
            linestyle=":",
            label="cross-group pairs",
            color="#888888",
        )
        ax.set_xlabel("Prevalence heterogeneity (logit SD)")
        ax.set_ylabel("Mean AUC")
        ax.set_ylim(0.45, 1.02)
        ax.set_title(title, loc="left", fontweight="bold")
        ax.legend(frameon=True, fontsize=8.0)
        style_axes(ax, ink=True)

    fig.text(
        0.02,
        0.01,
        "Pair-stratum AUCs partition comparison pairs; values are not additive.",
        fontsize=8.0,
        color=INK_MID,
    )
    fig.tight_layout()
    path = FIGURES_DIR / "sim_auc_components.png"
    save_figure(fig, path)
    return path


def write_simulation_summary_md(grid_df: pd.DataFrame) -> Path:
    md_path = TABLES_DIR / "simulation_grouped_reportability_summary.md"
    illustrative = grid_df[
        (grid_df["n_groups"] == 12)
        & (grid_df["group_size"] == 16)
        & (grid_df["global_prevalence"] == 0.10)
    ].sort_values(["prevalence_heterogeneity", "within_signal"])

    display = illustrative[
        [
            "prevalence_heterogeneity",
            "within_signal",
            "ndc_mean",
            "p_dual_class_group_mean",
            "structural_auc_pooled_mean",
            "structural_auc_within_mean",
            "structural_auc_cross_mean",
            "prevalence_auc_pooled_mean",
            "share_within_pairs_mean",
        ]
    ].head(12)

    lines = [
        "# Simulation of grouped ranking reportability",
        "",
        (
            f"Grid: {len(N_GROUPS_GRID)} group counts × {len(GROUP_SIZE_GRID)} sizes × "
            f"{len(GLOBAL_PREVALENCE_GRID)} prevalence levels × "
            f"{len(PREVALENCE_HETEROGENEITY_GRID)} heterogeneity levels × "
            f"{len(WITHIN_SIGNAL_GRID)} within-signal levels; "
            f"{N_REPLICATES} replicates per cell."
        ),
        "",
        "## Illustrative slice (12 groups, size 16, π=0.10)",
        "",
        markdown_table(display),
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def main() -> None:
    ensure_output_dirs()
    rng = np.random.default_rng(RANDOM_STATE)
    grid_df = run_grid(rng)

    write_csv_md(
        grid_df,
        "simulation_grouped_reportability",
        title="Simulated grouped reportability and pair-partition AUC",
        intro=(
            "Synthetic grouped binary cohorts under varying sparsity and prevalence structure. "
            "Metrics averaged over Monte Carlo replicates per grid cell."
        ),
    )
    summary_path = write_simulation_summary_md(grid_df)
    ndc_path = plot_ndc_vs_heterogeneity(grid_df)
    auc_path = plot_auc_components(grid_df)

    print(f"Wrote {TABLES_DIR / 'simulation_grouped_reportability.csv'}")
    print(f"Wrote {summary_path}")
    print(f"Wrote {ndc_path}")
    print(f"Wrote {auc_path}")


if __name__ == "__main__":
    main()
