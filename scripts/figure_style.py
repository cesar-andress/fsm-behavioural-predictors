"""Shared matplotlib style for SQJ replication-package figures.

Mirrors paper/figures/FIGURE_STYLE_GUIDE.md (grayscale palette, typography).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch, Rectangle

# Grayscale tokens (match fig_styles.tex)
GRAY_STROKE = 0.72
GRAY_DASH = 0.48
GRAY_FILL = 0.05
GRAY_FILL_MID = 0.14
GRAY_FILL_DARK = 0.22
GRAY_FAIL = 0.30
# Pale fills (LaTeX ``black!5`` … ``black!10``): low ink level → light RGB.
FILL_PALE = 0.06
FILL_LIGHT = GRAY_FILL
# Readable text on white: high ink level → dark RGB (LaTeX ``black!88`` … ``black!90``).
TEXT_ON_WHITE = 0.90
TEXT_ON_WHITE_MID = 0.82
TICK_ON_WHITE = 0.85
INK = "#000000"
INK_MID = "#222222"
INK_LIGHT = "#444444"

FIG_DPI = 300
FIG_BASE_SIZE = 12
FIG_TITLE_SIZE = 12
FIG_TICK_SIZE = 11
FIG_LEGEND_SIZE = 11
FIG_PANEL_LABEL_SIZE = 13
FIG_HEATMAP_CELL_SIZE = 12
FIG_HEATMAP_NA_SIZE = 11
FIG_HEATMAP_SUBTITLE_SIZE = 11
FIG_HEATMAP_CBAR_SIZE = 11
FIG_LINEWIDTH = 2.6
FIG_CHANCE_LINEWIDTH = 1.0
FIG_CHANCE_COLOR = "#999999"
FIG_AXES_LINEWIDTH = 1.0
FIG_GRID_ALPHA = 0.22

GATE_LABELS: dict[str, str] = {
    "g2_pass": "G2 (schema)",
    "g3_pass": "G3 (determinism)",
    "g3a_pass": "G3a (guards)",
}

MODEL_DISPLAY: dict[str, str] = {
    "gemma2:9b": "gemma2:9b",
    "llama3.1:8b": "llama3.1:8b",
    "mistral-nemo:12b": "mistral-nemo:12b",
    "qwen2.5-coder:7b": "qwen2.5-coder:7b",
}

PREDICTOR_SET_ORDER = [
    "A_gate_only",
    "B_basic_structural",
    "C_reference_difference",
    "D_combined",
]

PREDICTOR_SET_LABELS: dict[str, str] = {
    "A_gate_only": "A: Gates",
    "B_basic_structural": "B: Graph tallies",
    "C_reference_difference": "C: Ref.-diff.",
    "D_combined": "D: Combined",
}

HEATMAP_FAMILY_LABELS: dict[str, str] = {
    "A_gate_only": "A: gates",
    "B_basic_structural": "B: graph tallies",
    "C_reference_difference": "C: ref.-diff.",
    "D_combined": "D: combined",
}

MODEL_LABELS: dict[str, str] = {
    "logistic_regression": "LR",
    "decision_tree": "DT",
    "random_forest": "RF",
    "dummy_stratified": "Dummy (strat.)",
    "dummy_majority": "Dummy (maj.)",
}


def _gray(level: float) -> str:
    """Map ink level in [0, 1]: 0 = white, 1 = black (matches LaTeX ``black!N``)."""
    v = int(round((1.0 - level) * 255))
    return f"#{v:02x}{v:02x}{v:02x}"


def _fill(level: float | None = None) -> str:
    """Shorthand for pale figure fills (defaults to ``FILL_PALE``)."""
    return _gray(FILL_PALE if level is None else level)


# All series use black ink; linestyle + width encode the classifier (print-safe, no hue).
MODEL_STYLES: dict[str, dict] = {
    "logistic_regression": {
        "color": INK,
        "linestyle": "-",
        "linewidth": FIG_LINEWIDTH,
    },
    "decision_tree": {
        "color": INK,
        "linestyle": (0, (6, 3)),
        "linewidth": FIG_LINEWIDTH - 0.3,
    },
    "random_forest": {
        "color": INK,
        "linestyle": (0, (3, 1, 1, 1)),
        "linewidth": FIG_LINEWIDTH - 0.3,
    },
    "dummy_stratified": {
        "color": INK,
        "linestyle": (0, (1, 2.5)),
        "linewidth": FIG_LINEWIDTH - 0.6,
    },
    "dummy_majority": {
        "color": INK,
        "linestyle": (0, (5, 1, 1, 1, 1, 1)),
        "linewidth": FIG_LINEWIDTH - 0.8,
    },
}

# Curves plotted back-to-front; legend lists primary classifiers only.
MODEL_PLOT_ORDER = [
    "dummy_stratified",
    "logistic_regression",
    "decision_tree",
    "random_forest",
]
MODEL_LEGEND_ORDER = [
    "logistic_regression",
    "decision_tree",
    "random_forest",
    "dummy_stratified",
]


def apply_figure_style() -> None:
    """Apply rcParams shared across all artefact figures."""
    gray_scale = [
        _gray(GRAY_STROKE),
        _gray(GRAY_DASH),
        _gray(GRAY_FAIL),
        _gray(GRAY_FILL_DARK),
        _gray(GRAY_FILL_MID),
    ]
    mpl.rcParams.update(
        {
            "figure.dpi": FIG_DPI,
            "savefig.dpi": FIG_DPI,
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial", "Liberation Sans"],
            "font.size": FIG_BASE_SIZE,
            "axes.titlesize": FIG_TITLE_SIZE,
            "axes.titleweight": "bold",
            "axes.labelsize": FIG_BASE_SIZE,
            "axes.labelweight": "medium",
            "xtick.labelsize": FIG_TICK_SIZE,
            "ytick.labelsize": FIG_TICK_SIZE,
            "legend.fontsize": FIG_LEGEND_SIZE,
            "lines.linewidth": FIG_LINEWIDTH,
            "lines.antialiased": True,
            "axes.linewidth": FIG_AXES_LINEWIDTH,
            "axes.edgecolor": INK_MID,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "text.color": INK,
            "axes.prop_cycle": mpl.cycler(color=gray_scale),
            "grid.alpha": FIG_GRID_ALPHA,
            "grid.color": _gray(GRAY_DASH),
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.08,
        }
    )


def gate_label(column: str) -> str:
    return GATE_LABELS.get(column, column)


def model_display(name: str) -> str:
    return MODEL_DISPLAY.get(name, name.replace("_", " "))


def add_panel_label(ax: plt.Axes, label: str) -> None:
    """Publication-style panel tag, e.g. (A), matching manuscript captions."""
    ax.text(
        0.03,
        0.97,
        f"({label})",
        transform=ax.transAxes,
        fontsize=FIG_PANEL_LABEL_SIZE,
        fontweight="bold",
        va="top",
        ha="left",
        color=INK,
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "white",
            "edgecolor": INK_MID,
            "linewidth": 0.6,
            "alpha": 0.92,
        },
        zorder=10,
    )


def heatmap_cmap() -> LinearSegmentedColormap:
    """Grayscale colormap: near-white (0) → dark grey (1), print-safe."""
    return LinearSegmentedColormap.from_list(
        "fig_gray",
        [_gray(0.06), _gray(GRAY_FILL_DARK), _gray(0.88)],
    )


def style_axes(ax: plt.Axes, *, ink: bool = True) -> None:
    """Style spines/ticks; ``ink=True`` forces near-black text (print-safe)."""
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_linewidth(FIG_AXES_LINEWIDTH)
        spine.set_color(INK_MID)
    tick_c = INK if ink else _gray(TICK_ON_WHITE)
    label_c = INK if ink else _gray(TEXT_ON_WHITE)
    ax.tick_params(axis="both", colors=tick_c, labelsize=FIG_TICK_SIZE)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(label_c)
        label.set_fontweight("medium")
    xlabel = ax.xaxis.get_label()
    ylabel = ax.yaxis.get_label()
    xlabel.set_color(label_c)
    ylabel.set_color(label_c)


def heatmap_text_color(value: float) -> str:
    """Light text on dark cells; black text on pale cells."""
    return "#ffffff" if value >= 0.62 else INK


def heatmap_family_label(name: str) -> str:
    return HEATMAP_FAMILY_LABELS.get(name, name.replace("_", " "))


def predictor_set_label(name: str) -> str:
    return PREDICTOR_SET_LABELS.get(name, name.replace("_", " "))


def model_label(name: str) -> str:
    return MODEL_LABELS.get(name, name.replace("_", " "))


def annotate_heatmap(
    ax: plt.Axes,
    data,
    *,
    nan_label: str = "n/a",
    fmt: str = "{:.2f}",
    cmap: LinearSegmentedColormap | None = None,
    poor_threshold: float = 0.6,
    strong_threshold: float = 0.75,
    mark_transfer_tiers: bool = False,
    na_hatch: str = "///",
) -> None:
    """Write per-cell values; undefined folds use ``nan_label`` on a distinct hatch."""
    cmap = cmap or heatmap_cmap()
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            if np.isnan(val):
                ax.add_patch(
                    Rectangle(
                        (j - 0.5, i - 0.5),
                        1,
                        1,
                        fill=True,
                        facecolor="white",
                        edgecolor=INK,
                        hatch=na_hatch,
                        linewidth=1.0,
                        zorder=2,
                    )
                )
                ax.text(
                    j,
                    i,
                    nan_label,
                    ha="center",
                    va="center",
                    color=INK,
                    fontsize=FIG_HEATMAP_NA_SIZE,
                    fontstyle="italic",
                    fontweight="bold",
                    zorder=3,
                )
            else:
                fval = float(val)
                if mark_transfer_tiers and fval < poor_threshold:
                    ax.add_patch(
                        Rectangle(
                            (j - 0.5, i - 0.5),
                            1,
                            1,
                            fill=False,
                            edgecolor=INK,
                            linewidth=1.6,
                            linestyle=(0, (4, 3)),
                            zorder=2,
                        )
                    )
                elif mark_transfer_tiers and fval >= strong_threshold:
                    ax.add_patch(
                        Rectangle(
                            (j - 0.5, i - 0.5),
                            1,
                            1,
                            fill=False,
                            edgecolor=INK,
                            linewidth=1.2,
                            linestyle="-",
                            zorder=2,
                        )
                    )
                ax.text(
                    j,
                    i,
                    fmt.format(fval),
                    ha="center",
                    va="center",
                    color=heatmap_text_color(fval),
                    fontsize=FIG_HEATMAP_CELL_SIZE,
                    fontweight="medium",
                    zorder=3,
                )


def _add_transfer_tier_legend(
    ax: plt.Axes,
    cmap: LinearSegmentedColormap,
    *,
    poor_threshold: float,
    strong_threshold: float,
) -> None:
    """In-figure key: undefined vs poor vs strong held-out transfer."""
    poor_color = cmap(poor_threshold * 0.5)
    strong_color = cmap(strong_threshold + 0.12)
    handles = [
        Patch(
            facecolor="white",
            edgecolor=INK,
            hatch="///",
            linewidth=1.0,
            label="Undefined (single-class hold-out)",
        ),
        Patch(
            facecolor=poor_color,
            edgecolor=INK,
            linewidth=1.0,
            linestyle=(0, (4, 3)),
            label=f"Poor transfer (ROC-AUC $<$ {poor_threshold:.1f})",
        ),
        Patch(
            facecolor=strong_color,
            edgecolor=INK,
            linewidth=1.2,
            label=f"Strong transfer (ROC-AUC $\\geq$ {strong_threshold:.2f})",
        ),
    ]
    leg = ax.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(0.0, -0.11),
        ncol=1,
        frameon=True,
        fancybox=False,
        edgecolor=INK_MID,
        facecolor="white",
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
        handlelength=1.6,
        handleheight=1.2,
        borderpad=0.6,
        labelspacing=0.45,
    )
    for text in leg.get_texts():
        text.set_color(INK)


def plot_transfer_heatmap(
    pivot,
    path,
    *,
    title: str = "",
    subtitle: str = "",
    ylabel: str,
    xlabel: str = "Predictor family",
    annotation_note: str = "",
    imbalance_note: str = "",
    show_transfer_legend: bool = False,
    poor_threshold: float = 0.6,
    strong_threshold: float = 0.75,
    figsize: tuple[float, float] = (11.0, 9.5),
) -> None:
    """Shared LOSO/LOMO heatmap layout for manuscript figures."""
    apply_figure_style()
    bottom_margin = 0.26 if show_transfer_legend else 0.14
    top_margin = 0.90 if imbalance_note else 0.94
    fig, ax = plt.subplots(figsize=figsize)
    data = pivot.to_numpy(dtype=float)
    cmap = heatmap_cmap()
    cmap.set_bad(color="white")
    masked_data = np.ma.masked_invalid(data)
    im = ax.imshow(masked_data, aspect="auto", vmin=0, vmax=1, cmap=cmap)
    n_rows, n_cols = data.shape
    ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.8)
    ax.tick_params(which="minor", size=0)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(
        [heatmap_family_label(c) for c in pivot.columns],
        rotation=25,
        ha="right",
        fontsize=FIG_TICK_SIZE,
    )
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=FIG_TICK_SIZE)
    ax.set_xlabel(xlabel, fontsize=FIG_BASE_SIZE, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=FIG_BASE_SIZE, labelpad=8)
    if title:
        ax.set_title(
            title,
            fontsize=FIG_TITLE_SIZE,
            fontweight="bold",
            loc="left",
            pad=22,
            color=INK,
        )
    if subtitle:
        ax.text(
            0.0,
            1.02,
            subtitle,
            transform=ax.transAxes,
            fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
            fontstyle="italic",
            color=INK_MID,
            ha="left",
            va="bottom",
        )
    if imbalance_note:
        ax.text(
            0.5,
            1.085,
            imbalance_note,
            transform=ax.transAxes,
            fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
            color=INK,
            ha="center",
            va="bottom",
            bbox={
                "boxstyle": "round,pad=0.35",
                "facecolor": _fill(),
                "edgecolor": INK_MID,
                "linewidth": 0.9,
            },
        )
    if annotation_note:
        ax.text(
            0.0,
            -0.08 if show_transfer_legend else -0.14,
            annotation_note,
            transform=ax.transAxes,
            fontsize=FIG_HEATMAP_SUBTITLE_SIZE - 0.5,
            color=INK,
            ha="left",
            va="top",
        )
    style_axes(ax, ink=True)
    annotate_heatmap(
        ax,
        data,
        cmap=cmap,
        poor_threshold=poor_threshold,
        strong_threshold=strong_threshold,
        mark_transfer_tiers=show_transfer_legend,
    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cbar.set_label(
        "Held-out ROC-AUC (0 = chance, 1 = perfect)",
        fontsize=FIG_HEATMAP_CBAR_SIZE,
        labelpad=10,
        color=INK,
        fontweight="medium",
    )
    cbar.set_ticks([0.0, 0.5, 1.0])
    cbar.set_ticklabels(["0", "0.5\n(chance)", "1"])
    cbar.ax.tick_params(labelsize=FIG_TICK_SIZE, colors=INK)
    cbar.outline.set_edgecolor(INK_MID)
    if show_transfer_legend:
        _add_transfer_tier_legend(
            ax,
            cmap,
            poor_threshold=poor_threshold,
            strong_threshold=strong_threshold,
        )
    fig.subplots_adjust(left=0.24, right=0.90, top=top_margin, bottom=bottom_margin)
    save_figure(fig, path)


def _dual_class_row_mask(data: np.ndarray) -> np.ndarray:
    """True for held-out systems with at least one defined ROC-AUC cell."""
    return np.any(~np.isnan(data), axis=1)


def _draw_cv_loso_bars(
    ax: plt.Axes,
    *,
    cv_auc: float,
    loso_auc: float,
    label: str,
) -> None:
    """Mini horizontal bars for CV versus LOSO in the annotation panel."""
    ax.set_xlim(0, 1.05)
    ax.set_ylim(-0.5, 2.2)
    ax.axis("off")
    bar_h = 0.42
    y_cv, y_loso = 1.55, 0.55
    ax.barh(y_cv, cv_auc, height=bar_h, color=_gray(GRAY_FILL_DARK), edgecolor=INK, linewidth=0.8)
    ax.barh(y_loso, loso_auc, height=bar_h, color=_gray(GRAY_FILL_MID), edgecolor=INK, linewidth=0.8)
    ax.text(-0.02, y_cv, "CV", ha="right", va="center", fontsize=FIG_HEATMAP_SUBTITLE_SIZE, color=INK)
    ax.text(-0.02, y_loso, "LOSO", ha="right", va="center", fontsize=FIG_HEATMAP_SUBTITLE_SIZE, color=INK)
    ax.text(cv_auc + 0.02, y_cv, f"{cv_auc:.2f}", ha="left", va="center", fontsize=FIG_HEATMAP_SUBTITLE_SIZE, fontweight="bold", color=INK)
    ax.text(loso_auc + 0.02, y_loso, f"{loso_auc:.2f}", ha="left", va="center", fontsize=FIG_HEATMAP_SUBTITLE_SIZE, fontweight="bold", color=INK)
    ax.text(0.0, 2.05, label, ha="left", va="bottom", fontsize=FIG_HEATMAP_SUBTITLE_SIZE, fontweight="bold", color=INK)
    ax.annotate(
        "",
        xy=(loso_auc, y_loso + 0.22),
        xytext=(cv_auc, y_cv - 0.22),
        arrowprops=dict(arrowstyle="->", color=INK, lw=1.1, shrinkA=2, shrinkB=2),
    )


def _reorder_loso_pivot(pivot):
    """Place dual-class held-out systems first for readable narrative flow."""
    data = pivot.to_numpy(dtype=float)
    dual_mask = _dual_class_row_mask(data)
    order = [i for i, ok in enumerate(dual_mask) if ok]
    order.extend(i for i, ok in enumerate(dual_mask) if not ok)
    return pivot.iloc[order]


def plot_loso_system_heatmap(
    pivot,
    path,
    *,
    family_b_cv: float,
    family_b_loso: float,
    ylabel: str = "Held-out requirement system (system_id)",
    xlabel: str = "Predictor family (A--D)",
) -> None:
    """Communication-first LOSO heatmap for SQJ Figure 9 (fig:loso-heatmap)."""
    from matplotlib import gridspec

    apply_figure_style()
    pivot = _reorder_loso_pivot(pivot)
    data = pivot.to_numpy(dtype=float)
    n_rows, n_cols = data.shape
    dual_mask = _dual_class_row_mask(data)
    dual_systems = [str(s) for s, ok in zip(pivot.index, dual_mask) if ok]
    dual_list = ", ".join(dual_systems) if dual_systems else "—"
    n_dual = int(dual_mask.sum())
    n_single = n_rows - n_dual

    fig = plt.figure(figsize=(12.6, 9.6))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.0, 0.32], wspace=0.05)
    ax = fig.add_subplot(gs[0])
    ax_ann = fig.add_subplot(gs[1])
    ax_ann.axis("off")

    cmap = heatmap_cmap()
    cmap.set_bad(color="white")
    masked_data = np.ma.masked_invalid(data)

    for i in range(n_rows):
        if dual_mask[i]:
            ax.add_patch(
                Rectangle(
                    (-0.5, i - 0.5),
                    n_cols,
                    1,
                    facecolor=_gray(GRAY_FILL_MID),
                    edgecolor="none",
                    alpha=0.38,
                    zorder=0,
                )
            )
            ax.add_patch(
                Rectangle(
                    (-0.62, i - 0.5),
                    0.12,
                    1,
                    facecolor=_gray(GRAY_FILL_DARK),
                    edgecolor=INK,
                    linewidth=0.8,
                    zorder=4,
                )
            )

    im = ax.imshow(masked_data, aspect="auto", vmin=0, vmax=1, cmap=cmap, zorder=1)

    if n_dual and n_dual < n_rows:
        divider_y = n_dual - 0.5
        ax.axhline(divider_y, color=INK, linewidth=2.4, zorder=6)
        ax.text(
            n_cols - 0.42,
            divider_y + 0.18,
            f"{n_dual} dual-class",
            ha="right",
            va="bottom",
            fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
            fontweight="bold",
            color=INK,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=INK, linewidth=0.8),
            zorder=7,
        )
        ax.text(
            n_cols - 0.42,
            divider_y - 0.18,
            f"{n_single} single-class (n/a)",
            ha="right",
            va="top",
            fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
            fontweight="bold",
            color=INK_MID,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=INK_MID, linewidth=0.7),
            zorder=7,
        )

    ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.8)
    ax.tick_params(which="minor", size=0)
    ax.set_xticks(range(n_cols))
    family_labels = [heatmap_family_label(c) for c in pivot.columns]
    ax.set_xticklabels(family_labels, rotation=22, ha="right", fontsize=FIG_TICK_SIZE)
    ax.set_yticks(range(n_rows))
    ylabels = ax.set_yticklabels(pivot.index, fontsize=FIG_TICK_SIZE)
    for i, label in enumerate(ylabels):
        if dual_mask[i]:
            label.set_fontweight("bold")
            label.set_color(INK)
    ax.set_xlabel(xlabel, fontsize=FIG_BASE_SIZE, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=FIG_BASE_SIZE, labelpad=8)

    if "B_basic_structural" in pivot.columns:
        b_j = list(pivot.columns).index("B_basic_structural")
        ax.add_patch(
            Rectangle(
                (b_j - 0.5, -0.5),
                1,
                n_rows,
                fill=False,
                edgecolor=INK,
                linewidth=2.2,
                zorder=5,
            )
        )
        ax.text(
            b_j,
            -0.88,
            "Family B\n(CV→LOSO collapse)",
            ha="center",
            va="top",
            fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
            fontweight="bold",
            color=INK,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor=INK, linewidth=0.9),
        )

    annotate_heatmap(ax, data, na_hatch="//", mark_transfer_tiers=False)
    style_axes(ax, ink=True)

    if n_dual:
        mid_dual = (n_dual - 1) / 2.0
        ax.text(
            -0.72,
            mid_dual,
            "dual-class\nfolds",
            ha="center",
            va="center",
            rotation=90,
            fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
            fontweight="bold",
            color=INK,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=INK, linewidth=0.8),
        )

    cbar = fig.colorbar(im, ax=ax, fraction=0.028, pad=0.02)
    cbar.set_label(
        "Held-out ROC-AUC",
        fontsize=FIG_HEATMAP_CBAR_SIZE,
        labelpad=8,
        color=INK,
        fontweight="medium",
    )
    cbar.set_ticks([0.0, 0.5, 1.0])
    cbar.set_ticklabels(["0", "0.5", "1"])
    cbar.ax.tick_params(labelsize=FIG_TICK_SIZE - 1, colors=INK)
    cbar.outline.set_edgecolor(INK_MID)

    ax.text(
        0.0,
        1.03,
        f"Only {n_dual}/12 held-out systems are dual-class; {n_single}/12 are single-class (hatched n/a).",
        transform=ax.transAxes,
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
        fontweight="bold",
        color=INK,
        ha="left",
        va="bottom",
    )

    # --- Annotation panel ---
    ann_box = dict(boxstyle="round,pad=0.55", facecolor=_fill(), edgecolor=INK, linewidth=1.0)
    ax_ann.text(
        0.0,
        0.98,
        "Key reading",
        transform=ax_ann.transAxes,
        fontsize=FIG_TITLE_SIZE,
        fontweight="bold",
        color=INK,
        ha="left",
        va="top",
        bbox=ann_box,
    )
    summary_lines = [
        f"Dual-class folds: {n_dual}/12",
        dual_list,
        "Only these rows support",
        "stable ROC-AUC under LOSO.",
        "",
        f"Single-class: {n_single}/12 systems",
        "(undefined ranking; hatched n/a)",
        "",
        "Family B (graph tallies), RF:",
        f"CV {family_b_cv:.3f}  →  LOSO μ {family_b_loso:.3f}",
        f"Δ ≈ {family_b_cv - family_b_loso:.2f}",
    ]
    ax_ann.text(
        0.04,
        0.86,
        "\n".join(summary_lines),
        transform=ax_ann.transAxes,
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
        color=INK,
        ha="left",
        va="top",
        linespacing=1.25,
    )

    bar_ax = ax_ann.inset_axes([0.06, 0.34, 0.88, 0.22])
    _draw_cv_loso_bars(
        bar_ax,
        cv_auc=family_b_cv,
        loso_auc=family_b_loso,
        label="Family B / RF",
    )

    ax_ann.text(
        0.04,
        0.28,
        "Cell value = mean held-out ROC-AUC\nacross LR, DT, and RF.",
        transform=ax_ann.transAxes,
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE - 0.5,
        color=INK_MID,
        ha="left",
        va="top",
        fontstyle="italic",
    )

    na_patch = Patch(facecolor="white", edgecolor=INK, hatch="//", linewidth=0.9, label="n/a (single-class)")
    leg = ax_ann.legend(
        handles=[na_patch],
        loc="lower left",
        bbox_to_anchor=(0.0, 0.0),
        frameon=True,
        fancybox=False,
        edgecolor=INK_MID,
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE - 0.5,
        handlelength=1.4,
        handleheight=1.0,
    )
    for text in leg.get_texts():
        text.set_color(INK)

    if "B_basic_structural" in pivot.columns and n_dual:
        b_j = list(pivot.columns).index("B_basic_structural")
        dual_rows = list(range(n_dual))
        loso_vals = [data[i, b_j] for i in dual_rows if not np.isnan(data[i, b_j])]
        if loso_vals:
            spread_txt = f"Family B spread: {min(loso_vals):.2f}–{max(loso_vals):.2f}"
            ax.text(
                0.0,
                -0.12,
                spread_txt,
                transform=ax.transAxes,
                fontsize=FIG_HEATMAP_SUBTITLE_SIZE - 0.5,
                color=INK_MID,
                ha="left",
                va="top",
                fontstyle="italic",
            )

    fig.subplots_adjust(left=0.20, right=0.92, top=0.90, bottom=0.12)
    save_figure(fig, path)


def _draw_lomo_spread_panel(
    ax: plt.Axes,
    *,
    model_labels: list[str],
    rf_values: list[float],
    spread_lo: float,
    spread_hi: float,
    mean_values: list[float],
) -> None:
    """Per-model strip chart for Family B held-out spread (LOMO Figure 10)."""
    n = len(model_labels)
    ax.set_xlim(0.48, 1.02)
    ax.set_ylim(-0.65, n - 0.35)
    ax.axvspan(
        spread_lo,
        spread_hi,
        ymin=0,
        ymax=1,
        facecolor=_gray(GRAY_FILL_MID),
        edgecolor=INK,
        linewidth=0.9,
        alpha=0.55,
        zorder=0,
    )
    ax.axvline(spread_lo, color=INK, linewidth=1.2, linestyle=(0, (4, 3)), zorder=1)
    ax.axvline(spread_hi, color=INK, linewidth=1.2, linestyle=(0, (4, 3)), zorder=1)
    ax.text(
        spread_lo,
        n - 0.05,
        f"{spread_lo:.2f}",
        ha="center",
        va="bottom",
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
        fontweight="bold",
        color=INK,
    )
    ax.text(
        spread_hi,
        n - 0.05,
        f"{spread_hi:.2f}",
        ha="center",
        va="bottom",
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
        fontweight="bold",
        color=INK,
    )
    ax.text(
        (spread_lo + spread_hi) / 2,
        n - 0.05,
        "Family B RF spread",
        ha="center",
        va="bottom",
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
        fontweight="bold",
        color=INK,
    )

    for i, (label, rf, mean) in enumerate(zip(model_labels, rf_values, mean_values)):
        y = n - 1 - i
        ax.hlines(y, 0.5, 1.0, colors=_gray(GRAY_DASH), linewidth=0.6, zorder=1)
        ax.plot(rf, y, "o", color=INK, markersize=9, zorder=3, label="RF" if i == 0 else None)
        ax.plot(
            mean,
            y,
            "s",
            color=_gray(GRAY_FILL_DARK),
            markersize=6,
            zorder=3,
            label="mean LR+RF" if i == 0 else None,
        )
        ax.text(0.47, y, label, ha="right", va="center", fontsize=FIG_HEATMAP_SUBTITLE_SIZE - 0.5, color=INK)
        if not np.isnan(rf):
            ax.text(
                rf + 0.025,
                y,
                f"{rf:.2f}",
                ha="left",
                va="center",
                fontsize=FIG_HEATMAP_SUBTITLE_SIZE - 0.5,
                fontweight="bold",
                color=INK,
                zorder=4,
            )

    worst_i = int(np.nanargmin(rf_values))
    best_i = int(np.nanargmax(rf_values))
    y_worst = n - 1 - worst_i
    y_best = n - 1 - best_i
    ax.annotate(
        "worst held-out",
        xy=(rf_values[worst_i], y_worst),
        xytext=(max(rf_values[worst_i] + 0.14, 0.62), y_worst + 0.55),
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE - 0.5,
        fontweight="bold",
        color=INK,
        ha="center",
        arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9),
        bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor=INK, linewidth=0.7),
    )
    best_x = rf_values[best_i]
    ax.annotate(
        "best held-out",
        xy=(best_x, y_best),
        xytext=(min(best_x - 0.18, 0.82), y_best + 0.55),
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE - 0.5,
        fontweight="bold",
        color=INK,
        ha="center",
        arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.9),
        bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor=INK, linewidth=0.7),
    )
    ax.legend(
        loc="lower right",
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE - 1,
        frameon=True,
        edgecolor=INK_MID,
        facecolor="white",
    )
    ax.set_yticks([])
    ax.set_xlabel("Held-out ROC-AUC", fontsize=FIG_HEATMAP_SUBTITLE_SIZE, color=INK)
    ax.tick_params(axis="x", labelsize=FIG_TICK_SIZE - 1, colors=INK)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(INK_MID)


def plot_lomo_model_heatmap(
    pivot,
    path,
    *,
    family_b_rf_by_model: dict[str, float],
    family_b_rf_spread: tuple[float, float],
    family_b_cv: float,
    family_b_lomo_mean: float,
    ylabel: str = "Held-out synthesis source (model)",
    xlabel: str = "Predictor family (A, B, D)",
) -> None:
    """Communication-first LOMO heatmap for SQJ Figure 10 (fig:lomo-heatmap)."""
    from matplotlib import gridspec

    apply_figure_style()
    data = pivot.to_numpy(dtype=float)
    n_rows, n_cols = data.shape
    spread_lo, spread_hi = family_b_rf_spread

    fig = plt.figure(figsize=(11.6, 8.0))
    gs = gridspec.GridSpec(
        2,
        1,
        height_ratios=[1.0, 0.62],
        hspace=0.42,
    )
    ax = fig.add_subplot(gs[0])
    ax_spread = fig.add_subplot(gs[1])

    cmap = heatmap_cmap()
    im = ax.imshow(data, aspect="auto", vmin=0, vmax=1, cmap=cmap, zorder=1)
    ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=2.0)
    ax.tick_params(which="minor", size=0)
    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(
        [heatmap_family_label(c) for c in pivot.columns],
        rotation=0,
        ha="center",
        fontsize=FIG_TICK_SIZE,
    )
    row_labels = [model_display(str(m)) for m in pivot.index]
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels(row_labels, fontsize=FIG_TICK_SIZE)
    ax.set_xlabel(xlabel, fontsize=FIG_BASE_SIZE, labelpad=8)
    ax.set_ylabel(ylabel, fontsize=FIG_BASE_SIZE, labelpad=8)

    if "B_basic_structural" in pivot.columns:
        b_j = list(pivot.columns).index("B_basic_structural")
        col_vals = data[:, b_j]
        ax.add_patch(
            Rectangle(
                (b_j - 0.5, -0.5),
                1,
                n_rows,
                fill=False,
                edgecolor=INK,
                linewidth=2.0,
                linestyle=(0, (6, 4)),
                zorder=4,
            )
        )
        worst_i = int(np.nanargmin(col_vals))
        best_i = int(np.nanargmax(col_vals))
        for i, tag in ((worst_i, "min"), (best_i, "max")):
            ax.add_patch(
                Rectangle(
                    (b_j - 0.5, i - 0.5),
                    1,
                    1,
                    fill=False,
                    edgecolor=INK,
                    linewidth=2.4 if tag == "min" else 1.6,
                    linestyle="-" if tag == "max" else (0, (2, 2)),
                    zorder=5,
                )
            )
        # Shade cells in the Family B RF spread interval
        for i in range(n_rows):
            rf = family_b_rf_by_model.get(str(pivot.index[i]), float("nan"))
            if not np.isnan(rf) and spread_lo <= rf <= spread_hi:
                ax.add_patch(
                    Rectangle(
                        (b_j - 0.5, i - 0.5),
                        1,
                        1,
                        facecolor=_gray(GRAY_FILL),
                        edgecolor="none",
                        alpha=0.45,
                        zorder=2,
                    )
                )

    annotate_heatmap(ax, data, mark_transfer_tiers=False)
    style_axes(ax, ink=True)

    ax.text(
        0.0,
        1.05,
        f"All 4/4 folds dual-class; Family B/RF held-out spread {spread_lo:.2f}–{spread_hi:.2f} "
        f"(CV {family_b_cv:.2f} → LOMO μ {family_b_lomo_mean:.2f}; high fold-wise variance).",
        transform=ax.transAxes,
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
        fontweight="bold",
        color=INK,
        ha="left",
        va="bottom",
    )

    cbar = fig.colorbar(im, ax=ax, orientation="horizontal", fraction=0.046, pad=0.10)
    cbar.set_label(
        "Held-out ROC-AUC",
        fontsize=FIG_HEATMAP_CBAR_SIZE,
        labelpad=6,
        color=INK,
        fontweight="medium",
    )
    cbar.set_ticks([0.0, 0.5, 1.0])
    cbar.set_ticklabels(["0", "0.5", "1"])
    cbar.ax.tick_params(labelsize=FIG_TICK_SIZE - 1, colors=INK)
    cbar.outline.set_edgecolor(INK_MID)

    if "B_basic_structural" in pivot.columns:
        b_j = list(pivot.columns).index("B_basic_structural")
        models = [str(m) for m in pivot.index]
        rf_vals = [family_b_rf_by_model.get(m, float("nan")) for m in models]
        mean_vals = list(data[:, b_j])
        short = [model_display(m).split(":")[0] for m in models]
        _draw_lomo_spread_panel(
            ax_spread,
            model_labels=short,
            rf_values=rf_vals,
            spread_lo=spread_lo,
            spread_hi=spread_hi,
            mean_values=mean_vals,
        )

    fig.subplots_adjust(left=0.22, right=0.96, top=0.88, bottom=0.12)
    save_figure(fig, path)


def save_figure(fig: plt.Figure, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
    if path.suffix.lower() == ".png":
        fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
    plt.close(fig)
