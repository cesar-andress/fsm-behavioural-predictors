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
FIG_LINEWIDTH = 2.0
FIG_CHANCE_LINEWIDTH = 1.2
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
    v = int(round((1.0 - level) * 255))
    return f"#{v:02x}{v:02x}{v:02x}"


MODEL_STYLES: dict[str, dict] = {
    "logistic_regression": {
        "color": _gray(0.0),
        "linestyle": "-",
        "linewidth": FIG_LINEWIDTH,
    },
    "decision_tree": {
        "color": _gray(GRAY_STROKE),
        "linestyle": "--",
        "linewidth": FIG_LINEWIDTH,
    },
    "random_forest": {
        "color": _gray(GRAY_FAIL),
        "linestyle": "-.",
        "linewidth": FIG_LINEWIDTH,
    },
    "dummy_stratified": {
        "color": _gray(GRAY_DASH),
        "linestyle": ":",
        "linewidth": FIG_LINEWIDTH - 0.2,
    },
    "dummy_majority": {
        "color": _gray(GRAY_FILL_DARK),
        "linestyle": (0, (3, 1, 1, 1)),
        "linewidth": FIG_LINEWIDTH - 0.4,
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
            "axes.edgecolor": _gray(0.18),
            "axes.labelcolor": _gray(0.02),
            "xtick.color": _gray(0.08),
            "ytick.color": _gray(0.08),
            "text.color": _gray(0.02),
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
        color=_gray(0.03),
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "white",
            "edgecolor": _gray(GRAY_DASH),
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


def style_axes(ax: plt.Axes) -> None:
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_linewidth(FIG_AXES_LINEWIDTH)
        spine.set_color(_gray(0.18))
    ax.tick_params(axis="both", colors=_gray(0.08), labelsize=FIG_TICK_SIZE)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(_gray(0.08))
    xlabel = ax.xaxis.get_label()
    ylabel = ax.yaxis.get_label()
    xlabel.set_color(_gray(0.02))
    ylabel.set_color(_gray(0.02))


def heatmap_text_color(value: float) -> str:
    return _gray(GRAY_FILL) if value >= 0.58 else _gray(0.03)


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
                        facecolor=_gray(0.94),
                        edgecolor=_gray(GRAY_STROKE),
                        hatch="xx",
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
                    color=_gray(GRAY_STROKE),
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
                            edgecolor=_gray(GRAY_STROKE),
                            linewidth=1.4,
                            linestyle=(0, (3, 2)),
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
                            edgecolor=_gray(0.03),
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
            facecolor=_gray(0.94),
            edgecolor=_gray(GRAY_STROKE),
            hatch="xx",
            linewidth=1.0,
            label="Undefined (single-class hold-out)",
        ),
        Patch(
            facecolor=poor_color,
            edgecolor=_gray(GRAY_STROKE),
            linewidth=1.0,
            linestyle=(0, (3, 2)),
            label=f"Poor transfer (ROC-AUC $<$ {poor_threshold:.1f})",
        ),
        Patch(
            facecolor=strong_color,
            edgecolor=_gray(0.03),
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
        edgecolor=_gray(0.18),
        facecolor="white",
        fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
        handlelength=1.6,
        handleheight=1.2,
        borderpad=0.6,
        labelspacing=0.45,
    )
    for text in leg.get_texts():
        text.set_color(_gray(0.05))


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
        ax.set_title(title, fontsize=FIG_TITLE_SIZE, fontweight="bold", loc="left", pad=22)
    if subtitle:
        ax.text(
            0.0,
            1.02,
            subtitle,
            transform=ax.transAxes,
            fontsize=FIG_HEATMAP_SUBTITLE_SIZE,
            fontstyle="italic",
            color=_gray(GRAY_FAIL),
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
            color=_gray(GRAY_STROKE),
            ha="center",
            va="bottom",
            bbox={
                "boxstyle": "round,pad=0.35",
                "facecolor": _gray(GRAY_FILL),
                "edgecolor": _gray(GRAY_DASH),
                "linewidth": 0.7,
            },
        )
    if annotation_note:
        ax.text(
            0.0,
            -0.08 if show_transfer_legend else -0.14,
            annotation_note,
            transform=ax.transAxes,
            fontsize=FIG_HEATMAP_SUBTITLE_SIZE - 0.5,
            color=_gray(GRAY_DASH),
            ha="left",
            va="top",
        )
    style_axes(ax)
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
        color=_gray(0.02),
    )
    cbar.set_ticks([0.0, 0.5, 1.0])
    cbar.set_ticklabels(["0", "0.5\n(chance)", "1"])
    cbar.ax.tick_params(labelsize=FIG_TICK_SIZE, colors=_gray(0.08))
    cbar.outline.set_edgecolor(_gray(0.18))
    if show_transfer_legend:
        _add_transfer_tier_legend(
            ax,
            cmap,
            poor_threshold=poor_threshold,
            strong_threshold=strong_threshold,
        )
    fig.subplots_adjust(left=0.24, right=0.90, top=top_margin, bottom=bottom_margin)
    save_figure(fig, path)


def save_figure(fig: plt.Figure, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
    if path.suffix.lower() == ".png":
        fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight", facecolor="white")
    plt.close(fig)
