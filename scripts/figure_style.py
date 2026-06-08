"""Shared matplotlib style for SQJ replication-package figures.

Mirrors paper/figures/FIGURE_STYLE_GUIDE.md (grayscale palette, typography).
"""

from __future__ import annotations

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Grayscale tokens (match fig_styles.tex)
GRAY_STROKE = 0.72
GRAY_DASH = 0.48
GRAY_FILL = 0.05
GRAY_FILL_MID = 0.14
GRAY_FILL_DARK = 0.22
GRAY_FAIL = 0.42

FIG_DPI = 200
FIG_BASE_SIZE = 9
FIG_LEGEND_SIZE = 8
FIG_HEATMAP_CELL_SIZE = 10
FIG_LINEWIDTH = 1.2
FIG_AXES_LINEWIDTH = 1.0
FIG_GRID_ALPHA = 0.25

PREDICTOR_SET_ORDER = [
    "A_gate_only",
    "B_basic_structural",
    "C_reference_difference",
    "D_combined",
]

PREDICTOR_SET_LABELS: dict[str, str] = {
    "A_gate_only": "A: gates",
    "B_basic_structural": "B: structural",
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
        "color": _gray(GRAY_STROKE),
        "linestyle": "-",
        "linewidth": FIG_LINEWIDTH,
    },
    "decision_tree": {
        "color": _gray(GRAY_DASH),
        "linestyle": "--",
        "linewidth": FIG_LINEWIDTH,
    },
    "random_forest": {
        "color": _gray(GRAY_FAIL),
        "linestyle": "-",
        "linewidth": FIG_LINEWIDTH,
    },
    "dummy_stratified": {
        "color": _gray(GRAY_FILL_DARK),
        "linestyle": ":",
        "linewidth": FIG_LINEWIDTH,
    },
    "dummy_majority": {
        "color": _gray(GRAY_FILL_MID),
        "linestyle": "-.",
        "linewidth": FIG_LINEWIDTH,
    },
}


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
            "font.size": FIG_BASE_SIZE,
            "axes.titlesize": FIG_BASE_SIZE,
            "axes.titleweight": "bold",
            "axes.labelsize": FIG_BASE_SIZE,
            "xtick.labelsize": FIG_BASE_SIZE,
            "ytick.labelsize": FIG_BASE_SIZE,
            "legend.fontsize": FIG_LEGEND_SIZE,
            "lines.linewidth": FIG_LINEWIDTH,
            "axes.linewidth": FIG_AXES_LINEWIDTH,
            "axes.edgecolor": _gray(GRAY_STROKE),
            "axes.labelcolor": _gray(GRAY_STROKE),
            "xtick.color": _gray(GRAY_STROKE),
            "ytick.color": _gray(GRAY_STROKE),
            "text.color": _gray(GRAY_STROKE),
            "axes.prop_cycle": mpl.cycler(color=gray_scale),
            "grid.alpha": FIG_GRID_ALPHA,
            "grid.color": _gray(GRAY_DASH),
        }
    )


def heatmap_cmap() -> LinearSegmentedColormap:
    """Grayscale colormap: white (0) → black!72 (1)."""
    return LinearSegmentedColormap.from_list(
        "fig_gray",
        [_gray(GRAY_FILL), _gray(GRAY_FILL_MID), _gray(GRAY_STROKE)],
    )


def style_axes(ax: plt.Axes) -> None:
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_linewidth(FIG_AXES_LINEWIDTH)
        spine.set_color(_gray(GRAY_STROKE))


def heatmap_text_color(value: float) -> str:
    return _gray(GRAY_FILL) if value < 0.55 else _gray(GRAY_STROKE)


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
) -> None:
    """Write per-cell values; undefined folds use ``nan_label`` on a light hatch."""
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            if np.isnan(val):
                ax.add_patch(
                    plt.Rectangle(
                        (j - 0.5, i - 0.5),
                        1,
                        1,
                        fill=True,
                        facecolor=_gray(GRAY_FILL_MID),
                        edgecolor=_gray(GRAY_DASH),
                        hatch="///",
                        linewidth=0.6,
                        zorder=0,
                    )
                )
                ax.text(
                    j,
                    i,
                    nan_label,
                    ha="center",
                    va="center",
                    color=_gray(GRAY_DASH),
                    fontsize=FIG_HEATMAP_CELL_SIZE,
                    fontweight="bold",
                )
            else:
                color = heatmap_text_color(float(val))
                ax.text(
                    j,
                    i,
                    fmt.format(val),
                    ha="center",
                    va="center",
                    color=color,
                    fontsize=FIG_HEATMAP_CELL_SIZE,
                )


def save_figure(fig: plt.Figure, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
