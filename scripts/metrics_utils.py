#!/usr/bin/env python3
"""Safe classification metrics and seed-level summary helpers."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    roc_auc_score,
)

METRIC_COLUMNS = [
    "roc_auc",
    "pr_auc",
    "balanced_accuracy",
    "f1",
    "mcc",
]


def is_binary_classification(y_true: np.ndarray) -> bool:
    labels = np.unique(y_true[~np.isnan(y_true)] if np.issubdtype(y_true.dtype, np.floating) else y_true)
    if len(labels) == 0:
        return False
    return len(labels) >= 2


def roc_auc_safe(y_true: np.ndarray, y_score: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    if len(y_true) == 0 or not is_binary_classification(y_true):
        return float("nan")
    try:
        return float(roc_auc_score(y_true, y_score))
    except ValueError:
        return float("nan")


def pr_auc_safe(y_true: np.ndarray, y_score: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    if len(y_true) == 0 or not is_binary_classification(y_true):
        return float("nan")
    try:
        return float(average_precision_score(y_true, y_score))
    except ValueError:
        return float("nan")


def balanced_accuracy_safe(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if len(y_true) == 0 or not is_binary_classification(y_true):
        return float("nan")
    return float(balanced_accuracy_score(y_true, y_pred))


def f1_safe(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if len(y_true) == 0 or not is_binary_classification(y_true):
        return float("nan")
    return float(f1_score(y_true, y_pred, zero_division=0))


def mcc_safe(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if len(y_true) == 0 or not is_binary_classification(y_true):
        return float("nan")
    try:
        return float(matthews_corrcoef(y_true, y_pred))
    except ValueError:
        return float("nan")


def classification_metrics(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    threshold: float = 0.5,
) -> dict[str, float]:
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    y_pred = (y_score >= threshold).astype(int)
    return {
        "roc_auc": roc_auc_safe(y_true, y_score),
        "pr_auc": pr_auc_safe(y_true, y_score),
        "balanced_accuracy": balanced_accuracy_safe(y_true, y_pred),
        "f1": f1_safe(y_true, y_pred),
        "mcc": mcc_safe(y_true, y_pred),
    }


def summarize_values(values: np.ndarray | pd.Series) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    valid = arr[~np.isnan(arr)]
    if valid.size == 0:
        return {
            "mean": float("nan"),
            "std": float("nan"),
            "median": float("nan"),
            "p025": float("nan"),
            "p975": float("nan"),
            "n_valid": 0.0,
        }
    return {
        "mean": float(np.mean(valid)),
        "std": float(np.std(valid, ddof=1)) if valid.size > 1 else 0.0,
        "median": float(np.median(valid)),
        "p025": float(np.percentile(valid, 2.5)),
        "p975": float(np.percentile(valid, 97.5)),
        "n_valid": float(valid.size),
    }


def summarize_metric_columns(df: pd.DataFrame, metrics: list[str] | None = None) -> dict[str, Any]:
    metrics = metrics or METRIC_COLUMNS
    out: dict[str, Any] = {}
    for metric in metrics:
        if metric not in df.columns:
            continue
        stats = summarize_values(df[metric])
        for key, val in stats.items():
            out[f"{metric}_{key}"] = val
    return out


def format_interval(mean: float, p025: float, p975: float) -> str:
    if any(np.isnan(x) for x in (mean, p025, p975)):
        return "n/a"
    return f"{mean:.3f} [{p025:.3f}, {p975:.3f}]"


def confusion_counts(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[int, int, int, int]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return int(tn), int(fp), int(fn), int(tp)


def group_definability_table(
    df: pd.DataFrame,
    group_col: str,
    label_col: str,
) -> pd.DataFrame:
    """Per-group counts, prevalence, and dual-class definability status."""
    rows: list[dict[str, Any]] = []
    for group_id, sub in df.groupby(group_col, sort=True):
        n_rows = len(sub)
        n_positive = int(sub[label_col].sum())
        n_negative = int(n_rows - n_positive)
        prevalence = n_positive / n_rows if n_rows else float("nan")
        dual_class = 0 < n_positive < n_rows
        rows.append(
            {
                "group_id": group_id,
                "n_rows": n_rows,
                "n_positive": n_positive,
                "n_negative": n_negative,
                "prevalence": prevalence,
                "dual_class": dual_class,
                "definability_status": "dual-class" if dual_class else "single-class",
            }
        )
    return pd.DataFrame(rows)


def _pair_partition_sums(
    y: np.ndarray,
    score: np.ndarray,
    groups: np.ndarray,
) -> dict[str, float]:
    """Concordance sums and pair counts for within- vs cross-group partitions."""
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=float)
    groups = np.asarray(groups)

    pos_idx = np.flatnonzero(y == 1)
    neg_idx = np.flatnonzero(y == 0)
    if pos_idx.size == 0 or neg_idx.size == 0:
        return {
            "n_within_pairs": 0.0,
            "n_cross_pairs": 0.0,
            "within_concordance_sum": float("nan"),
            "cross_concordance_sum": float("nan"),
        }

    n_within = 0
    n_cross = 0
    within_sum = 0.0
    cross_sum = 0.0

    for i in pos_idx:
        s_pos = score[i]
        g_pos = groups[i]
        for j in neg_idx:
            s_neg = score[j]
            if s_pos > s_neg:
                contribution = 1.0
            elif s_pos < s_neg:
                contribution = 0.0
            else:
                contribution = 0.5

            if groups[j] == g_pos:
                n_within += 1
                within_sum += contribution
            else:
                n_cross += 1
                cross_sum += contribution

    return {
        "n_within_pairs": float(n_within),
        "n_cross_pairs": float(n_cross),
        "within_concordance_sum": within_sum,
        "cross_concordance_sum": cross_sum,
    }


def roc_auc_pair_counts(
    y: np.ndarray,
    score: np.ndarray,
    groups: np.ndarray,
) -> dict[str, float]:
    """
    Partition positive-negative comparison pairs into within-group and cross-group strata.

    This is a pair-count partition, not an additive decomposition of AUC values.
    Pooled AUC equals the weighted mean of stratum AUCs by eligible pair counts.
    """
    parts = _pair_partition_sums(y, score, groups)
    n_within = int(parts["n_within_pairs"])
    n_cross = int(parts["n_cross_pairs"])
    n_total = n_within + n_cross
    share_within = n_within / n_total if n_total else float("nan")
    share_cross = n_cross / n_total if n_total else float("nan")

    within_auc = (
        parts["within_concordance_sum"] / n_within if n_within > 0 else float("nan")
    )
    cross_auc = parts["cross_concordance_sum"] / n_cross if n_cross > 0 else float("nan")
    pooled_auc = (
        (parts["within_concordance_sum"] + parts["cross_concordance_sum"]) / n_total
        if n_total > 0
        else float("nan")
    )

    return {
        "n_within_pairs": float(n_within),
        "n_cross_pairs": float(n_cross),
        "n_total_pairs": float(n_total),
        "share_within_pairs": share_within,
        "share_cross_pairs": share_cross,
        "auc_within": within_auc,
        "auc_cross": cross_auc,
        "auc_pooled": pooled_auc,
    }


def roc_auc_within_groups(
    y: np.ndarray,
    score: np.ndarray,
    groups: np.ndarray,
) -> float:
    """ROC-AUC using only positive-negative pairs inside the same group."""
    counts = roc_auc_pair_counts(y, score, groups)
    return float(counts["auc_within"])


def roc_auc_cross_groups(
    y: np.ndarray,
    score: np.ndarray,
    groups: np.ndarray,
) -> float:
    """ROC-AUC using only positive-negative pairs from different groups."""
    counts = roc_auc_pair_counts(y, score, groups)
    return float(counts["auc_cross"])
