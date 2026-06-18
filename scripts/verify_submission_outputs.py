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
            OUTPUTS_TABLES / "definability_audit.csv",
            OUTPUTS_TABLES / "definability_audit_summary.csv",
            OUTPUTS_FIGURES / "definability_map.png",
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


def _check_path(path: Path) -> str | None:
    if not path.is_file():
        return f"missing: {path.relative_to(ROOT)}"
    if path.suffix.lower() == ".png" and path.stat().st_size == 0:
        return f"empty PNG: {path.relative_to(ROOT)}"
    return None


def main() -> None:
    missing: list[str] = []
    for anchor, paths in EXPECTED:
        for path in paths:
            issue = _check_path(path)
            if issue:
                missing.append(f"{anchor}: {issue}")

    if missing:
        print("RAP-AQ submission output verification FAILED. Missing files:", file=sys.stderr)
        for line in missing:
            print(f"  - {line}", file=sys.stderr)
        print(
            "\nRun: make reproduce",
            file=sys.stderr,
        )
        raise SystemExit(1)

    total = sum(len(paths) for _, paths in EXPECTED)
    print(f"RAP-AQ submission output verification OK ({total} files across {len(EXPECTED)} anchors)")
    print("Zenodo DOI: https://doi.org/10.5281/zenodo.20738203")


if __name__ == "__main__":
    main()
