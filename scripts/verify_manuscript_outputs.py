#!/usr/bin/env python3
"""
Cross-check manuscript table/figure anchors against archived package outputs.

Exits 0 when every mapped artefact path exists under the repository root.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"
DATA = ROOT / "data" / "processed"

# Mirrors paper/sections/09_appendix_artefact.tex (Table artifact-outputs).
EXPECTED: list[tuple[str, list[Path]]] = [
    (
        "Table target-distribution",
        [TABLES / "target_distribution.md"],
    ),
    (
        "Table predictive-signal-profile; Figs bpr-by-gate/model/system",
        [
            TABLES / "predictive_signal_profile.md",
            FIGURES / "bpr_by_gate.png",
            FIGURES / "bpr_by_model.png",
            FIGURES / "bpr_by_system.png",
        ],
    ),
    (
        "Tables model-performance, feature-importance; Figs roc/pr-curves",
        [
            TABLES / "model_performance.md",
            TABLES / "model_feature_importance.md",
            TABLES / "model_validation.md",
            FIGURES / "roc_curves.png",
            FIGURES / "precision_recall_curves.png",
        ],
    ),
    (
        "Tables pre-oracle-performance, feature-importance",
        [
            TABLES / "pre_oracle_model_performance.md",
            TABLES / "pre_oracle_feature_importance.md",
        ],
    ),
    (
        "Table loso-summary; Fig loso-heatmap",
        [
            TABLES / "loso_system_summary.md",
            TABLES / "loso_system_results.md",
            FIGURES / "loso_system_heatmap.png",
        ],
    ),
    (
        "Table lomo-summary; Fig lomo-heatmap",
        [
            TABLES / "lomo_summary.md",
            TABLES / "lomo_results.md",
            FIGURES / "lomo_heatmap.png",
        ],
    ),
    (
        "Table toolkit-validation",
        [
            TABLES / "risk_toolkit_validation.md",
            TABLES / "risk_toolkit_predictions.csv",
        ],
    ),
    (
        "Master analysis table",
        [
            DATA / "master_analysis_dataset.csv",
            TABLES / "master_dataset_validation.md",
        ],
    ),
    (
        "Descriptive profiles",
        [
            TABLES / "descriptive_profile.md",
            TABLES / "profile_tables_index.md",
        ],
    ),
]


def main() -> None:
    missing: list[str] = []
    for anchor, paths in EXPECTED:
        for path in paths:
            rel = path.relative_to(ROOT)
            if not path.is_file():
                missing.append(f"{anchor}: {rel}")

    if missing:
        print("Manuscript output verification FAILED. Missing files:", file=sys.stderr)
        for line in missing:
            print(f"  - {line}", file=sys.stderr)
        print("\nRun: make reproduce", file=sys.stderr)
        raise SystemExit(1)

    total = sum(len(paths) for _, paths in EXPECTED)
    print(f"Manuscript output verification OK ({total} files across {len(EXPECTED)} anchors)")
    print(f"Zenodo DOI: https://doi.org/10.5281/zenodo.20598129")


if __name__ == "__main__":
    main()
