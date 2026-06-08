#!/usr/bin/env python3
"""
Generate descriptive profiling tables from the master analysis dataset.

Reads data/processed/master_analysis_dataset.csv.
Writes CSV tables to results/tables/.
Does not invoke LLM inference.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MASTER_CSV = ROOT / "data" / "processed" / "master_analysis_dataset.csv"
OUT_DIR = ROOT / "results" / "tables"

BOOL_COLUMNS = [
    "g1_pass",
    "g2_pass",
    "g3_pass",
    "g3a_pass",
    "full_behavioural_pass",
    "behaviourally_scored",
]

NUMERIC_COLUMNS = [
    "requirement_coverage",
    "n_states",
    "n_events",
    "n_transitions",
    "n_unreachable_states",
    "missing_transitions",
    "extra_transitions",
    "behavioral_pass_rate",
]


def load_master() -> pd.DataFrame:
    if not MASTER_CSV.is_file():
        print(f"ERROR: master dataset not found: {MASTER_CSV}", file=sys.stderr)
        print("Run: make build-master", file=sys.stderr)
        raise SystemExit(1)

    df = pd.read_csv(MASTER_CSV)
    for col in BOOL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].map(
                {"true": True, "false": False, True: True, False: False}
            )
    return df


def pass_rate(series: pd.Series) -> float | None:
    valid = series.dropna()
    if valid.empty:
        return None
    return float(valid.mean())


def write_csv(df: pd.DataFrame, name: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    df.to_csv(path, index=False)
    return path


def profile_cohort_summary(df: pd.DataFrame) -> pd.DataFrame:
    n = len(df)
    scored_n = int(df["behaviourally_scored"].sum())

    def row(statistic: str, value: int, denominator: int) -> dict:
        return {
            "statistic": statistic,
            "value": value,
            "denominator": denominator,
            "rate": value / denominator if denominator else None,
        }

    g2_pass_n = int(df["g2_pass"].sum(skipna=True))
    g3_pass_n = int(df["g3_pass"].sum(skipna=True))
    g3a_pass_n = int(df["g3a_pass"].sum(skipna=True))
    full_pass_n = int(df["full_behavioural_pass"].sum(skipna=True))

    rows = [
        row("total_runs", n, n),
        row("g1_pass", int(df["g1_pass"].sum()), n),
        row("g2_pass", g2_pass_n, n),
        row("g3_pass", g3_pass_n, n),
        row("g3a_pass", g3a_pass_n, n),
        row("behaviourally_scored", scored_n, n),
        row("full_behavioural_pass", full_pass_n, scored_n),
    ]
    return pd.DataFrame(rows)


def profile_gate_pass_rates(df: pd.DataFrame) -> pd.DataFrame:
    g2_subset = df[df["g2_pass"] == True]  # noqa: E712
    records = []
    for gate, col in [
        ("G1", "g1_pass"),
        ("G2", "g2_pass"),
        ("G3", "g3_pass"),
        ("G3a", "g3a_pass"),
    ]:
        valid = df[col].dropna()
        records.append(
            {
                "gate": gate,
                "pass_count": int(valid.sum()),
                "eligible_count": len(valid),
                "pass_rate": pass_rate(df[col]),
            }
        )
    records.append(
        {
            "gate": "G3 (G2-pass denominator)",
            "pass_count": int(g2_subset["g3_pass"].sum(skipna=True)),
            "eligible_count": len(g2_subset),
            "pass_rate": pass_rate(g2_subset["g3_pass"]),
        }
    )
    records.append(
        {
            "gate": "G3a (G2-pass denominator)",
            "pass_count": int(g2_subset["g3a_pass"].sum(skipna=True)),
            "eligible_count": len(g2_subset),
            "pass_rate": pass_rate(g2_subset["g3a_pass"]),
        }
    )
    return pd.DataFrame(records)


def profile_by_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    scored = df[df["behaviourally_scored"]]
    grouped = df.groupby(dimension, sort=True)
    scored_grouped = scored.groupby(dimension, sort=True)

    rows = []
    for key, group in grouped:
        scored_group = (
            scored_grouped.get_group(key)
            if key in scored_grouped.groups
            else scored.iloc[0:0]
        )
        rows.append(
            {
                dimension: key,
                "n_runs": len(group),
                "g1_pass_rate": pass_rate(group["g1_pass"]),
                "g2_pass_rate": pass_rate(group["g2_pass"]),
                "g3_pass_rate": pass_rate(group["g3_pass"]),
                "g3a_pass_rate": pass_rate(group["g3a_pass"]),
                "behaviourally_scored_n": int(group["behaviourally_scored"].sum()),
                "full_behavioural_pass_n": int(group["full_behavioural_pass"].sum(skipna=True)),
                "full_behavioural_pass_rate_scored": pass_rate(scored_group["full_behavioural_pass"]),
                "mean_behavioral_pass_rate": scored_group["behavioral_pass_rate"].mean(),
                "median_behavioral_pass_rate": scored_group["behavioral_pass_rate"].median(),
                "mean_requirement_coverage": group["requirement_coverage"].mean(),
                "mean_n_states": group["n_states"].mean(),
                "mean_n_transitions": group["n_transitions"].mean(),
                "mean_missing_transitions": group["missing_transitions"].mean(),
                "mean_extra_transitions": group["extra_transitions"].mean(),
            }
        )
    return pd.DataFrame(rows)


def profile_failure_stage(df: pd.DataFrame) -> pd.DataFrame:
    counts = (
        df.groupby("failure_stage", dropna=False)
        .size()
        .reset_index(name="run_count")
        .sort_values("run_count", ascending=False)
    )
    counts["proportion"] = counts["run_count"] / len(df)
    return counts


def profile_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for stratum_name, subset in [
        ("all_runs", df),
        ("behaviourally_scored", df[df["behaviourally_scored"]]),
        ("g2_pass", df[df["g2_pass"] == True]),  # noqa: E712
        ("full_behavioural_pass", df[df["full_behavioural_pass"] == True]),  # noqa: E712
    ]:
        if subset.empty:
            continue
        desc = subset[NUMERIC_COLUMNS].describe(percentiles=[0.25, 0.5, 0.75]).T
        desc = desc.reset_index().rename(columns={"index": "variable"})
        desc.insert(0, "stratum", stratum_name)
        desc.insert(1, "n", len(subset))
        frames.append(desc)
    return pd.concat(frames, ignore_index=True)


def profile_bpr_distribution(df: pd.DataFrame) -> pd.DataFrame:
    scored = df[df["behaviourally_scored"]].copy()
    counts = (
        scored["behavioral_pass_rate"]
        .value_counts()
        .sort_index()
        .reset_index()
        .rename(columns={"behavioral_pass_rate": "behavioral_pass_rate", "count": "run_count"})
    )
    counts["proportion_scored"] = counts["run_count"] / len(scored)
    return counts


def profile_gate_combinations(df: pd.DataFrame) -> pd.DataFrame:
    eligible = df[df["g2_pass"].notna()].copy()
    eligible["gate_pattern"] = (
        eligible["g1_pass"].map({True: "1", False: "0"})
        + eligible["g2_pass"].map({True: "1", False: "0"})
        + eligible["g3_pass"].map({True: "1", False: "0"})
        + eligible["g3a_pass"].map({True: "1", False: "0"})
    )
    summary = (
        eligible.groupby("gate_pattern", sort=True)
        .agg(
            run_count=("run_id", "count"),
            full_behavioural_pass_n=("full_behavioural_pass", lambda s: int(s.sum(skipna=True))),
            mean_behavioral_pass_rate=("behavioral_pass_rate", "mean"),
        )
        .reset_index()
    )
    summary["proportion"] = summary["run_count"] / len(eligible)
    summary["gate_pattern_label"] = summary["gate_pattern"].map(
        lambda p: f"G1/G2/G3/G3a={p[0]}/{p[1]}/{p[2]}/{p[3]}"
    )
    return summary


def write_index(paths: list[tuple[str, Path]]) -> None:
    lines = [
        "# Descriptive profiling tables",
        "",
        "Generated from `data/processed/master_analysis_dataset.csv` by `scripts/generate_tables.py`.",
        "",
        "| Table | Description |",
        "|-------|-------------|",
    ]
    descriptions = {
        "profile_cohort_summary.csv": "Overall cohort counts and pass rates.",
        "profile_gate_pass_rates.csv": "Structural gate pass counts and rates (including G2-pass denominators for G3/G3a).",
        "profile_by_model.csv": "Descriptive profiles grouped by LLM model.",
        "profile_by_system.csv": "Descriptive profiles grouped by system specification.",
        "profile_failure_stage.csv": "Run counts by pipeline failure stage.",
        "profile_numeric_summary.csv": "Numeric structural and behavioural summaries by analysis stratum.",
        "profile_bpr_distribution.csv": "Exact behavioural pass rate (BPR) value counts among scored runs.",
        "profile_gate_combinations.csv": "Run counts by G1–G3a gate pattern among structurally evaluable runs.",
    }
    for name, path in paths:
        lines.append(f"| `{path.name}` | {descriptions.get(path.name, '')} |")
    lines.append("")
    (OUT_DIR / "profile_tables_index.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df = load_master()
    outputs: list[tuple[str, Path]] = []

    tables = [
        ("profile_cohort_summary.csv", profile_cohort_summary(df)),
        ("profile_gate_pass_rates.csv", profile_gate_pass_rates(df)),
        ("profile_by_model.csv", profile_by_dimension(df, "model")),
        ("profile_by_system.csv", profile_by_dimension(df, "system_id")),
        ("profile_failure_stage.csv", profile_failure_stage(df)),
        ("profile_numeric_summary.csv", profile_numeric_summary(df)),
        ("profile_bpr_distribution.csv", profile_bpr_distribution(df)),
        ("profile_gate_combinations.csv", profile_gate_combinations(df)),
    ]

    for name, table in tables:
        path = write_csv(table, name)
        outputs.append((name, path))
        print(f"Wrote {path} ({len(table)} rows)")

    write_index(outputs)
    print(f"Wrote {OUT_DIR / 'profile_tables_index.md'}")


if __name__ == "__main__":
    main()
