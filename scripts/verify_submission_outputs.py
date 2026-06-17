#!/usr/bin/env python3
"""
Verify RAP-AQ submission-freeze outputs under outputs/ and core data tables.

Exits 0 when every path required by the EMSE manuscript replication deposit exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_TABLES = ROOT / "outputs" / "tables"
OUTPUTS_FIGURES = ROOT / "outputs" / "figures"
OUTPUTS_STATS = ROOT / "outputs" / "stats"
RESULTS_TABLES = ROOT / "results" / "tables"
DATA = ROOT / "data" / "processed"

# Primary RAP-AQ manuscript outputs (strengthen-stats + methodological-upgrade).
EXPECTED: list[tuple[str, list[Path]]] = [
    (
        "RAP-AQ Step 2 definability audit",
        [
            OUTPUTS_TABLES / "definibility_audit.csv",
            OUTPUTS_TABLES / "definibility_audit_summary.csv",
            OUTPUTS_FIGURES / "definibility_map.png",
        ],
    ),
    (
        "RAP-AQ Steps 3–4 prevalence and pair partition",
        [
            OUTPUTS_TABLES / "prevalence_correlation.csv",
            OUTPUTS_TABLES / "prevalence_baseline_cv.csv",
            OUTPUTS_TABLES / "table5_strengthened.csv",
            OUTPUTS_FIGURES / "prevalence_baseline_comparison.png",
            OUTPUTS_TABLES / "grouped_auc_decomposition.csv",
            OUTPUTS_TABLES / "group_pair_contribution.csv",
            OUTPUTS_FIGURES / "sim_auc_components.png",
        ],
    ),
    (
        "RAP-AQ optional CV–LOSO contrast",
        [
            OUTPUTS_TABLES / "table6_strengthened.csv",
            OUTPUTS_TABLES / "bootstrap_delta.csv",
            OUTPUTS_TABLES / "bootstrap_delta_iterations.csv",
            OUTPUTS_FIGURES / "bootstrap_delta_distribution.png",
            OUTPUTS_TABLES / "grouped_auc_bootstrap.csv",
        ],
    ),
    (
        "Cohort and manifest",
        [
            DATA / "master_analysis_dataset.csv",
            RESULTS_TABLES / "target_distribution.md",
            OUTPUTS_STATS / "strengthened_stats_manifest.json",
        ],
    ),
]


def main() -> None:
    missing: list[str] = []
    for anchor, paths in EXPECTED:
        for path in paths:
            if not path.is_file():
                missing.append(f"{anchor}: {path.relative_to(ROOT)}")

    if missing:
        print("RAP-AQ submission output verification FAILED. Missing files:", file=sys.stderr)
        for line in missing:
            print(f"  - {line}", file=sys.stderr)
        print(
            "\nRun: make submission-freeze",
            file=sys.stderr,
        )
        raise SystemExit(1)

    total = sum(len(paths) for _, paths in EXPECTED)
    print(f"RAP-AQ submission output verification OK ({total} files across {len(EXPECTED)} anchors)")
    print("Zenodo DOI: https://doi.org/10.5281/zenodo.20598129")


if __name__ == "__main__":
    main()
