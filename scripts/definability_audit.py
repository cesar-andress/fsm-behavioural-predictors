#!/usr/bin/env python3
"""Per-system LOSO definability audit for Family B / random forest."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from metrics_utils import roc_auc_safe  # noqa: E402
from model_behavioural_correctness import (  # noqa: E402
    PREDICTOR_SETS,
    load_scored_frame,
    make_model,
    prepare_features,
)
from repro_config import RANDOM_STATE, STRENGTHEN_CLASSIFIER  # noqa: E402
from strengthen_io import TABLES_DIR, ensure_output_dirs, write_csv_md  # noqa: E402

FAMILY_B = "B_basic_structural"


def family_b_loso_roc_auc(df: pd.DataFrame, held_out: str) -> float:
    features = PREDICTOR_SETS[FAMILY_B]
    X_all = prepare_features(df, features)
    y_all = df["full_behavioural_pass"].astype(int)
    test_mask = df["system_id"] == held_out
    train_mask = ~test_mask
    X_train, y_train = X_all.loc[train_mask], y_all.loc[train_mask]
    X_test, y_test = X_all.loc[test_mask], y_all.loc[test_mask]

    if y_test.nunique() < 2 or y_train.nunique() < 2:
        return float("nan")

    model = make_model(STRENGTHEN_CLASSIFIER)
    if hasattr(model, "named_steps"):
        clf = model.named_steps.get("clf")
        if clf is not None and hasattr(clf, "random_state"):
            clf.set_params(random_state=RANDOM_STATE)

    fitted = clone(model)
    fitted.fit(X_train, y_train)
    prob = fitted.predict_proba(X_test)[:, 1]
    return roc_auc_safe(y_test.to_numpy(), prob)


def main() -> None:
    ensure_output_dirs()
    df = load_scored_frame()
    y = df["full_behavioural_pass"].astype(int)

    rows: list[dict] = []
    for system_id in sorted(df["system_id"].unique()):
        sub = df[df["system_id"] == system_id]
        n_rows = len(sub)
        n_pos = int(sub["full_behavioural_pass"].sum())
        n_neg = int(n_rows - n_pos)
        prevalence = n_pos / n_rows if n_rows else float("nan")
        labels_present = "dual-class" if n_pos > 0 and n_neg > 0 else "single-class"
        roc_definable = labels_present == "dual-class"
        loso_auc = family_b_loso_roc_auc(df, system_id) if roc_definable else float("nan")

        rows.append(
            {
                "system_id": system_id,
                "n_rows": n_rows,
                "n_positive": n_pos,
                "n_negative": n_neg,
                "prevalence": prevalence,
                "labels_present": labels_present,
                "loso_roc_auc_definable": roc_definable,
                "family_b_rf_loso_roc_auc": loso_auc if roc_definable else "n/a",
            }
        )

    audit_df = pd.DataFrame(rows)
    n_systems = len(audit_df)
    n_dual = int(audit_df["loso_roc_auc_definable"].sum())
    pct_systems = 100.0 * n_dual / n_systems if n_systems else float("nan")
    definable_rows = int(
        audit_df.loc[audit_df["loso_roc_auc_definable"], "n_rows"].sum()
    )
    pct_rows = 100.0 * definable_rows / len(df) if len(df) else float("nan")

    summary = pd.DataFrame(
        [
            {"metric": "n_systems", "value": n_systems},
            {"metric": "n_dual_class_systems", "value": n_dual},
            {"metric": "ndc_over_total_systems", "value": f"{n_dual}/{n_systems}"},
            {
                "metric": "pct_systems_loso_roc_auc_definable",
                "value": pct_systems,
            },
            {
                "metric": "pct_rows_in_definable_systems",
                "value": pct_rows,
            },
        ]
    )

    write_csv_md(
        audit_df,
        "definability_audit",
        title="LOSO definability audit by system_id",
        intro=(
            f"Family B / `{STRENGTHEN_CLASSIFIER}` LOSO ROC-AUC is definable only when "
            "the held-out system contains both pass and fail labels. "
            f"Summary: {n_dual}/{n_systems} dual-class systems; "
            f"{pct_rows:.1f}% of scored rows belong to definable systems."
        ),
    )

    summary_path = TABLES_DIR / "definability_audit_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"Wrote {TABLES_DIR / 'definability_audit.csv'}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
