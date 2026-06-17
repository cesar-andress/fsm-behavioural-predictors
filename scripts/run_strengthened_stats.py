#!/usr/bin/env python3
"""Orchestrate strengthened-stats analyses into outputs/."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import cluster_bootstrap_delta  # noqa: E402
import definability_audit  # noqa: E402
import prevalence_baseline  # noqa: E402
import prevalence_correlation  # noqa: E402
import repeated_seed_cv  # noqa: E402
import strengthened_figures  # noqa: E402
import strengthened_tables  # noqa: E402
from repro_config import (  # noqa: E402
    N_BOOTSTRAP_ITERATIONS,
    STRENGTHEN_AGGREGATION_RULE,
    STRENGTHEN_CLASSIFIER,
    STRENGTHEN_SEEDS,
)
from strengthen_io import MASTER_CSV, git_commit_hash, utc_timestamp, write_manifest  # noqa: E402

STEPS: list[tuple[str, object]] = [
    ("Repeated-seed pooled CV", repeated_seed_cv.main),
    ("LOSO definability audit", definability_audit.main),
    ("Prevalence-only baseline", prevalence_baseline.main),
    ("Fixed audit predictor vs prevalence correlation", prevalence_correlation.main),
    ("Cluster bootstrap Δ", cluster_bootstrap_delta.main),
    ("Strengthened summary tables", strengthened_tables.main),
    ("Strengthened figures", strengthened_figures.main),
]


def collect_output_files() -> list[str]:
    from strengthen_io import FIGURES_DIR, STATS_DIR, TABLES_DIR

    files: list[str] = []
    for directory in (TABLES_DIR, FIGURES_DIR, STATS_DIR):
        if directory.is_dir():
            for path in sorted(directory.rglob("*")):
                if path.is_file():
                    files.append(str(path.relative_to(ROOT)))
    return files


def main() -> None:
    for label, runner in STEPS:
        print(f"\n=== {label} ===")
        runner()

    manifest = {
        "timestamp": utc_timestamp(),
        "git_commit_hash": git_commit_hash(),
        "dataset_path": str(MASTER_CSV.relative_to(ROOT)),
        "seed_list": STRENGTHEN_SEEDS,
        "n_bootstrap_iterations": N_BOOTSTRAP_ITERATIONS,
        "classifier": STRENGTHEN_CLASSIFIER,
        "aggregation_rule": STRENGTHEN_AGGREGATION_RULE,
        "scripts": [
            "metrics_utils.py",
            "strengthen_io.py",
            "repeated_seed_cv.py",
            "definibility_audit.py",
            "prevalence_baseline.py",
            "prevalence_correlation.py",
            "cluster_bootstrap_delta.py",
            "strengthened_tables.py",
            "strengthened_figures.py",
            "run_strengthened_stats.py",
        ],
        "output_files": collect_output_files(),
    }
    manifest_path = write_manifest(manifest)
    print(f"\nWrote {manifest_path}")
    print(f"Generated {len(manifest['output_files'])} output files.")


if __name__ == "__main__":
    main()
