#!/usr/bin/env python3
"""
Build the SQJ 2026 master analysis dataset from frozen campaign artefacts.

Reads immutable inputs under data/raw/ only. Does not invoke LLM inference.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
RESULTS_TABLES = ROOT / "results" / "tables"

METRICS_FILE = DATA_RAW / "metrics_combined.csv"
CANDIDATES_DIR = DATA_RAW / "candidates"
EVALUATIONS_DIR = DATA_RAW / "evaluations"
OUTPUT_CSV = DATA_PROCESSED / "master_analysis_dataset.csv"
VALIDATION_MD = RESULTS_TABLES / "master_dataset_validation.md"

G1_FAIL_STAGES = frozenset({"parsing", "json_extraction", "generation"})

MASTER_COLUMNS = [
    "run_id",
    "model",
    "system_id",
    "replicate",
    "g1_pass",
    "g2_pass",
    "g3_pass",
    "g3a_pass",
    "requirement_coverage",
    "n_states",
    "n_events",
    "n_transitions",
    "n_unreachable_states",
    "missing_transitions",
    "extra_transitions",
    "behavioral_pass_rate",
    "full_behavioural_pass",
    "behaviourally_scored",
    "failure_stage",
]


def parse_optional_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip()
    if not text:
        return None
    lowered = text.lower()
    if lowered in {"true", "1", "yes"}:
        return True
    if lowered in {"false", "0", "no"}:
        return False
    return None


def parse_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return float(text)


def parse_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return int(float(text))


def is_g1_pass(failure_stage: str) -> bool:
    return failure_stage not in G1_FAIL_STAGES


def is_g2_pass(schema_valid: bool | None, referential_valid: bool | None) -> bool | None:
    if schema_valid is None or referential_valid is None:
        return None
    return schema_valid and referential_valid


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def structural_counts_from_candidate(candidate: dict[str, Any] | None) -> tuple[int | None, int | None, int | None]:
    if candidate is None:
        return None, None, None
    states = candidate.get("states")
    events = candidate.get("events")
    transitions = candidate.get("transitions")
    n_states = len(states) if isinstance(states, list) else None
    n_events = len(events) if isinstance(events, list) else None
    n_transitions = len(transitions) if isinstance(transitions, list) else None
    return n_states, n_events, n_transitions


def unreachable_count_from_evaluation(evaluation: dict[str, Any] | None) -> int | None:
    if evaluation is None:
        return None
    determinism = evaluation.get("determinism")
    if not isinstance(determinism, dict):
        return None
    unreachable = determinism.get("unreachable_states")
    if isinstance(unreachable, list):
        return len(unreachable)
    return None


def build_row(metrics_row: dict[str, str]) -> dict[str, Any]:
    run_id = metrics_row["run_id"]
    failure_stage = str(metrics_row.get("failure_stage") or "")

    schema_valid = parse_optional_bool(metrics_row.get("schema_valid"))
    referential_valid = parse_optional_bool(metrics_row.get("referential_valid"))
    g3_pass = parse_optional_bool(metrics_row.get("strict_deterministic"))
    g3a_pass = parse_optional_bool(metrics_row.get("guard_aware_deterministic"))

    bpr = parse_optional_float(metrics_row.get("behavioral_pass_rate"))
    behaviourally_scored = bpr is not None
    full_behavioural_pass: bool | None
    if bpr is None:
        full_behavioural_pass = None
    else:
        full_behavioural_pass = bpr == 1.0

    candidate = load_json(CANDIDATES_DIR / f"{run_id}.json")
    evaluation = load_json(EVALUATIONS_DIR / f"{run_id}.json")
    n_states, n_events, n_transitions = structural_counts_from_candidate(candidate)
    n_unreachable_states = unreachable_count_from_evaluation(evaluation)

    return {
        "run_id": run_id,
        "model": metrics_row.get("model", ""),
        "system_id": metrics_row.get("system_id", ""),
        "replicate": parse_optional_int(metrics_row.get("replicate")),
        "g1_pass": is_g1_pass(failure_stage),
        "g2_pass": is_g2_pass(schema_valid, referential_valid),
        "g3_pass": g3_pass,
        "g3a_pass": g3a_pass,
        "requirement_coverage": parse_optional_float(metrics_row.get("requirement_coverage")),
        "n_states": n_states,
        "n_events": n_events,
        "n_transitions": n_transitions,
        "n_unreachable_states": n_unreachable_states,
        "missing_transitions": parse_optional_int(metrics_row.get("missing_transitions")),
        "extra_transitions": parse_optional_int(metrics_row.get("extra_transitions")),
        "behavioral_pass_rate": bpr,
        "full_behavioural_pass": full_behavioural_pass,
        "behaviourally_scored": behaviourally_scored,
        "failure_stage": failure_stage,
    }


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MASTER_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def format_bool(value: Any) -> str:
    if value is None:
        return ""
    return "true" if value else "false"


def serialize_row_for_csv(row: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in MASTER_COLUMNS:
        value = row[key]
        if isinstance(value, bool):
            out[key] = format_bool(value)
        elif value is None:
            out[key] = ""
        else:
            out[key] = str(value)
    return out


def write_validation_report(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = len(rows)
    run_ids = [row["run_id"] for row in rows]
    duplicate_count = n - len(set(run_ids))

    missing: dict[str, int] = {col: 0 for col in MASTER_COLUMNS}
    for row in rows:
        for col in MASTER_COLUMNS:
            if row[col] is None or row[col] == "":
                missing[col] += 1

    scored = [row for row in rows if row["behaviourally_scored"]]
    full_pass = sum(1 for row in rows if row["full_behavioural_pass"] is True)
    g1_pass = sum(1 for row in rows if row["g1_pass"] is True)
    g2_pass = sum(1 for row in rows if row["g2_pass"] is True)

    bpr_dist: dict[str, int] = {}
    for row in scored:
        key = f"{row['behavioral_pass_rate']:.6g}"
        bpr_dist[key] = bpr_dist.get(key, 0) + 1

    lines = [
        "# Master dataset validation report",
        "",
        f"**Output:** `{OUTPUT_CSV.relative_to(ROOT)}`",
        f"**Rows:** {n}",
        f"**Duplicate `run_id` count:** {duplicate_count}",
        "",
        "## Missing values per column",
        "",
        "| Column | Missing |",
        "|--------|--------:|",
    ]
    for col in MASTER_COLUMNS:
        lines.append(f"| `{col}` | {missing[col]} |")

    lines.extend(
        [
            "",
            "## Target and gate distributions",
            "",
            f"- `g1_pass` true: **{g1_pass}** / {n}",
            f"- `g2_pass` true: **{g2_pass}** / {n}",
            f"- `behaviourally_scored` true: **{len(scored)}** / {n}",
            f"- `full_behavioural_pass` true: **{full_pass}** / {n}",
            "",
            "## `behavioral_pass_rate` value counts (scored rows only)",
            "",
            "| BPR | Count |",
            "|-----|------:|",
        ]
    )
    for bpr_value, count in sorted(bpr_dist.items(), key=lambda item: float(item[0])):
        lines.append(f"| {bpr_value} | {count} |")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not METRICS_FILE.is_file():
        print(f"ERROR: missing frozen metrics file: {METRICS_FILE}", file=sys.stderr)
        return 1
    if not CANDIDATES_DIR.is_dir() or not EVALUATIONS_DIR.is_dir():
        print("ERROR: missing candidates/ or evaluations/ under data/raw/", file=sys.stderr)
        return 1

    with METRICS_FILE.open(encoding="utf-8") as handle:
        metrics_rows = list(csv.DictReader(handle))

    built = [build_row(row) for row in metrics_rows]
    csv_rows = [serialize_row_for_csv(row) for row in built]
    write_csv(csv_rows, OUTPUT_CSV)
    write_validation_report(built, VALIDATION_MD)

    print(f"Wrote {len(built)} rows to {OUTPUT_CSV}")
    print(f"Wrote validation report to {VALIDATION_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
