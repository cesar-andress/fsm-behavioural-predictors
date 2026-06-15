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
