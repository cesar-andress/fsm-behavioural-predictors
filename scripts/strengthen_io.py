#!/usr/bin/env python3
"""Shared paths and I/O helpers for strengthened-stats outputs."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = ROOT / "outputs"
TABLES_DIR = OUTPUTS_DIR / "tables"
FIGURES_DIR = OUTPUTS_DIR / "figures"
STATS_DIR = OUTPUTS_DIR / "stats"
MASTER_CSV = ROOT / "data" / "processed" / "master_analysis_dataset.csv"

PREDICTOR_FAMILY_LABELS: dict[str, str] = {
    "A_gate_only": "Family A gates",
    "B_basic_structural": "Family B graph tallies",
    "C_reference_difference": "Family C ref-diff",
    "D_combined": "Family D combined",
    "dummy_stratified": "stratified dummy",
    "prevalence_only": "prevalence-only baseline",
}


def ensure_output_dirs() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    STATS_DIR.mkdir(parents=True, exist_ok=True)


def git_commit_hash() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def markdown_table(df: pd.DataFrame, float_cols: set[str] | None = None) -> str:
    float_cols = float_cols or set()
    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        cells = []
        for col in headers:
            val = row[col]
            if col in float_cols and pd.notna(val):
                cells.append(f"{float(val):.3f}")
            elif isinstance(val, float) and pd.notna(val):
                cells.append(f"{float(val):.3f}")
            else:
                cells.append(str(val))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_csv_md(
    df: pd.DataFrame,
    stem: str,
    *,
    title: str,
    intro: str = "",
    float_cols: set[str] | None = None,
) -> tuple[Path, Path]:
    ensure_output_dirs()
    csv_path = TABLES_DIR / f"{stem}.csv"
    md_path = TABLES_DIR / f"{stem}.md"
    df.to_csv(csv_path, index=False)
    float_cols = float_cols or {
        c for c in df.columns if df[c].dtype in ("float64", "float32")
    }
    lines = [f"# {title}", ""]
    if intro:
        lines.extend([intro, ""])
    lines.append(markdown_table(df, float_cols))
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return csv_path, md_path


def save_predictions(df: pd.DataFrame, stem: str) -> Path:
    ensure_output_dirs()
    parquet_path = STATS_DIR / f"{stem}.parquet"
    csv_path = STATS_DIR / f"{stem}.csv"
    try:
        df.to_parquet(parquet_path, index=False)
        return parquet_path
    except (ImportError, ValueError, ModuleNotFoundError):
        df.to_csv(csv_path, index=False)
        return csv_path


def load_predictions(stem: str) -> pd.DataFrame:
    parquet_path = STATS_DIR / f"{stem}.parquet"
    csv_path = STATS_DIR / f"{stem}.csv"
    if parquet_path.is_file():
        return pd.read_parquet(parquet_path)
    if csv_path.is_file():
        return pd.read_csv(csv_path)
    raise FileNotFoundError(f"Missing predictions: {parquet_path} or {csv_path}")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_manifest(payload: dict[str, Any]) -> Path:
    import json

    ensure_output_dirs()
    path = STATS_DIR / "strengthened_stats_manifest.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
