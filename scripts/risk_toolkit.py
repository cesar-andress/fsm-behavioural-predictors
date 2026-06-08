#!/usr/bin/env python3
"""
Pre-oracle FSM Behavioural Risk Toolkit.

Computes a Behavioural Risk Score (BRS), AutoReject triage decisions, and
human-readable health reports from pre-oracle structural features only.
No LLM inference; no oracle-adjacent predictors.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MASTER_CSV = ROOT / "data" / "processed" / "master_analysis_dataset.csv"
TABLES_DIR = ROOT / "results" / "tables"
DOCS_DIR = ROOT / "docs"

# --- Allowed pre-oracle features (strict allowlist) ---
ALLOWED_FEATURES: tuple[str, ...] = (
    "g2_pass",
    "g3_pass",
    "g3a_pass",
    "requirement_coverage",
    "n_states",
    "n_events",
    "n_transitions",
    "n_unreachable_states",
)

FORBIDDEN_FEATURES: frozenset[str] = frozenset(
    {
        "missing_transitions",
        "extra_transitions",
        "behavioral_pass_rate",
        "full_behavioural_pass",
        "behaviourally_scored",
        "g1_pass",
        "model",
        "system_id",
        "replicate",
        "run_id",
        "failure_stage",
    }
)

BOOL_COLUMNS = ["g2_pass", "g3_pass", "g3a_pass"]

# --- BRS formula (fixed weights; not outcome-tuned) ---
# Documented in docs/risk_toolkit.md. Derived from cohort quartiles for thresholds only.
GATE_WEIGHT = 50.0 / 3.0  # 0–50 across three gates
COV_REFERENCE = 0.875  # cohort 75th percentile of requirement_coverage
COV_WEIGHT = 35.0
STATE_WEIGHT = 15.0  # n_states in {2,3,4} → scaled 0–15
EVENT_WEIGHT = 5.0  # minor contribution; n_events scaled within cohort range

# AutoReject thresholds (conservative; frozen from gate-passing scored cohort)
# Median BRS ≈ 21.25; 75th ≈ 25.6; max (gate-passing) = 30. T_REJECT set above
# observed gate-passing maximum so BRS alone never rejects when all gates pass.
T_REVIEW = 25.0
T_REJECT = 35.0

DECISION_ACCEPT = "accept_for_behavioural_testing"
DECISION_REVIEW = "review_before_testing"
DECISION_REJECT = "reject_or_regenerate"

RISK_LOW = "low"
RISK_MEDIUM = "medium"
RISK_HIGH = "high"

NEXT_ACTION = {
    DECISION_ACCEPT: (
        "Proceed to behavioural oracle testing; BRS and gates indicate lower "
        "pre-oracle risk (not a correctness guarantee)."
    ),
    DECISION_REVIEW: (
        "Manual review recommended before committing oracle resources: check "
        "requirement coverage, graph complexity, and gate diagnostics."
    ),
    DECISION_REJECT: (
        "Regenerate or repair the FSM before behavioural testing: structural "
        "gates failed and/or BRS exceeds the conservative reject threshold."
    ),
}


def parse_bool(value: Any, *, missing: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, np.integer)):
        return bool(value)
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return missing
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    raise ValueError(f"Cannot parse boolean: {value!r}")


def load_frame(path: Path) -> pd.DataFrame:
    if not path.is_file():
        print(f"ERROR: input not found: {path}", file=sys.stderr)
        raise SystemExit(1)
    df = pd.read_csv(path)
    for col in BOOL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].map(parse_bool)
    return df


def validate_feature_policy(row: pd.Series) -> None:
    """Ensure scoring uses only the pre-oracle allowlist (not input column presence)."""
    _ = FORBIDDEN_FEATURES  # documented exclusion set; not used as predictors
    for feat in ALLOWED_FEATURES:
        if feat not in row.index:
            raise ValueError(f"Missing required feature column: {feat}")


def coerce_pre_oracle_row(row: pd.Series) -> pd.Series:
    """Conservative defaults for incomplete parses (documented in docs/risk_toolkit.md)."""
    out = row.copy()
    for gate in BOOL_COLUMNS:
        out[gate] = parse_bool(out[gate], missing=False)
    if pd.isna(out["requirement_coverage"]):
        out["requirement_coverage"] = 0.0
    if pd.isna(out["n_unreachable_states"]):
        out["n_unreachable_states"] = 0
    for num_col in ("n_states", "n_events", "n_transitions"):
        if pd.isna(out[num_col]):
            raise ValueError(f"Missing numeric feature after parse: {num_col}")
    return out


def compute_brs_components(row: pd.Series) -> dict[str, float]:
    g2 = parse_bool(row["g2_pass"])
    g3 = parse_bool(row["g3_pass"])
    g3a = parse_bool(row["g3a_pass"])
    gate_failures = 3 - int(g2) - int(g3) - int(g3a)
    gate_risk = gate_failures * GATE_WEIGHT

    cov = float(row["requirement_coverage"])
    coverage_risk = COV_WEIGHT * max(0.0, (COV_REFERENCE - cov) / COV_REFERENCE)

    n_states = float(row["n_states"])
    state_risk = STATE_WEIGHT * max(0.0, min(1.0, (n_states - 2.0) / 2.0))

    n_events = float(row["n_events"])
    event_risk = EVENT_WEIGHT * max(0.0, min(1.0, (n_events - 4.0) / 8.0))

    brs = min(100.0, gate_risk + coverage_risk + state_risk + event_risk)
    return {
        "brs": brs,
        "gate_risk": gate_risk,
        "coverage_risk": coverage_risk,
        "state_risk": state_risk,
        "event_risk": event_risk,
        "gate_failures": float(gate_failures),
    }


def contributing_factors(row: pd.Series, components: dict[str, float]) -> list[str]:
    factors: list[str] = []
    if components["gate_failures"] > 0:
        failed = []
        if not parse_bool(row["g2_pass"]):
            failed.append("g2_pass")
        if not parse_bool(row["g3_pass"]):
            failed.append("g3_pass")
        if not parse_bool(row["g3a_pass"]):
            failed.append("g3a_pass")
        factors.append(f"Failed structural gates: {', '.join(failed)}")
    cov = float(row["requirement_coverage"])
    if cov < COV_REFERENCE:
        factors.append(
            f"Requirement coverage {cov:.3f} below reference {COV_REFERENCE:.3f}"
        )
    if components["state_risk"] > 0:
        factors.append(f"Elevated state count (n_states={int(row['n_states'])})")
    if components["event_risk"] > 0:
        factors.append(f"Elevated event count (n_events={int(row['n_events'])})")
    if not factors:
        factors.append("All gates pass; coverage and size within conservative bounds")
    return factors


def autoreject_decision(row: pd.Series, brs: float) -> tuple[str, str, str]:
    """Return (decision, reason_code, risk_level)."""
    if not (parse_bool(row["g2_pass"]) and parse_bool(row["g3_pass"]) and parse_bool(row["g3a_pass"])):
        return DECISION_REJECT, "gate_failure", RISK_HIGH
    if brs >= T_REJECT:
        return DECISION_REJECT, "high_brs", RISK_HIGH
    if brs >= T_REVIEW:
        return DECISION_REVIEW, "elevated_brs", RISK_MEDIUM
    return DECISION_ACCEPT, "low_brs", RISK_LOW


def score_row(row: pd.Series) -> dict[str, Any]:
    validate_feature_policy(row)
    row = coerce_pre_oracle_row(row)

    components = compute_brs_components(row)
    decision, reason, risk_level = autoreject_decision(row, components["brs"])
    factors = contributing_factors(row, components)

    return {
        "brs": round(components["brs"], 3),
        "gate_risk": round(components["gate_risk"], 3),
        "coverage_risk": round(components["coverage_risk"], 3),
        "state_risk": round(components["state_risk"], 3),
        "event_risk": round(components["event_risk"], 3),
        "risk_level": risk_level,
        "decision": decision,
        "decision_reason": reason,
        "contributing_factors": "; ".join(factors),
        "recommended_action": NEXT_ACTION[decision],
    }


def score_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for feat in ALLOWED_FEATURES:
        if feat not in df.columns:
            raise ValueError(f"Required feature column missing: {feat}")

    records = []
    for idx, row in df.iterrows():
        scored = score_row(row)
        out = {"row_index": idx}
        if "run_id" in df.columns:
            out["run_id"] = row["run_id"]
        out.update(scored)
        records.append(out)
    return pd.DataFrame(records)


def format_health_report(row: pd.Series, scored: dict[str, Any]) -> str:
    run_id = row.get("run_id", "<unknown>")
    lines = [
        "=" * 60,
        "FSM Behavioural Health Report (pre-oracle triage)",
        "=" * 60,
        f"Run ID:           {run_id}",
        f"BRS score:        {scored['brs']:.1f} / 100  (higher = higher risk)",
        f"Risk level:       {scored['risk_level']}",
        f"AutoReject:       {scored['decision']}",
        f"Reason:           {scored['decision_reason']}",
        "",
        "Contributing factors:",
    ]
    for factor in scored["contributing_factors"].split("; "):
        lines.append(f"  - {factor}")
    lines.extend(
        [
            "",
            "Component risks (pre-oracle):",
            f"  - Gate risk:     {scored['gate_risk']:.1f}",
            f"  - Coverage risk: {scored['coverage_risk']:.1f}",
            f"  - State risk:    {scored['state_risk']:.1f}",
            f"  - Event risk:    {scored['event_risk']:.1f}",
            "",
            "Recommended next action:",
            f"  {scored['recommended_action']}",
            "",
            "Disclaimer: triage aid only — not behavioural correctness certification.",
            "=" * 60,
        ]
    )
    return "\n".join(lines)


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


def validate_on_scored_cohort(df: pd.DataFrame, scored: pd.DataFrame) -> str:
    """Evaluate triage decisions against full_behavioural_pass (scored rows only)."""
    if "behaviourally_scored" not in df.columns or "full_behavioural_pass" not in df.columns:
        return (
            "# Risk toolkit validation\n\n"
            "Outcome columns absent; validation skipped.\n"
        )

    for col in ["behaviourally_scored", "full_behavioural_pass"]:
        df[col] = df[col].map(parse_bool)

    merged = df.copy()
    for col in ["brs", "risk_level", "decision", "decision_reason"]:
        merged[col] = scored[col].values

    eval_df = merged[merged["behaviourally_scored"] == True].copy()  # noqa: E712
    n = len(eval_df)
    n_pass = int(eval_df["full_behavioural_pass"].sum())

    bucket_rows = []
    for decision in [DECISION_ACCEPT, DECISION_REVIEW, DECISION_REJECT]:
        sub = eval_df[eval_df["decision"] == decision]
        bucket_rows.append(
            {
                "decision": decision,
                "count": len(sub),
                "share": len(sub) / n if n else 0.0,
                "full_pass_count": int(sub["full_behavioural_pass"].sum()),
                "full_pass_rate": float(sub["full_behavioural_pass"].mean())
                if len(sub)
                else float("nan"),
            }
        )
    bucket_df = pd.DataFrame(bucket_rows)

    false_reject = int(
        (
            (eval_df["decision"] == DECISION_REJECT) & eval_df["full_behavioural_pass"]
        ).sum()
    )
    false_accept = int(
        (
            (eval_df["decision"] == DECISION_ACCEPT)
            & ~eval_df["full_behavioural_pass"]
        ).sum()
    )
    non_pass = eval_df[~eval_df["full_behavioural_pass"]]
    caught = int(
        non_pass["decision"].isin([DECISION_REJECT, DECISION_REVIEW]).sum()
    )
    coverage = caught / len(non_pass) if len(non_pass) else float("nan")

    lines = [
        "# Risk toolkit validation",
        "",
        "Retrospective evaluation on behaviourally scored runs in the frozen cohort. "
        "**Triage audit only** — not certification of behavioural correctness.",
        "",
        f"- Evaluation set: **{n}** scored runs ({n_pass} full behavioural pass, "
        f"{100 * n_pass / n:.1f}% prevalence).",
        f"- Thresholds: `T_REVIEW={T_REVIEW}`, `T_REJECT={T_REJECT}`; "
        "any gate failure ⇒ reject.",
        "",
        "## Decision buckets",
        "",
        markdown_table(
            bucket_df,
            {"share", "full_pass_rate"},
        ),
        "",
        "## Error-oriented metrics (exploratory)",
        "",
        f"- False rejections (full pass but rejected): **{false_reject}**",
        f"- False acceptances (non-pass but accepted for testing): **{false_accept}**",
        f"- Coverage of behavioural failures in reject+review buckets: "
        f"**{caught} / {len(non_pass)}** ({100 * coverage:.1f}%)",
        "",
        "## Interpretation guardrails",
        "",
        "- Accept decisions prioritise oracle budget; they do **not** guarantee pass.",
        "- Reject decisions are conservative when structural gates fail (0% full pass "
        "in this cohort).",
        "- Thresholds are frozen from cohort quartiles; not hyperparameter-tuned.",
        "- Do not treat BRS as a probability of correctness.",
        "",
    ]
    return "\n".join(lines)


def write_examples(df: pd.DataFrame, scored: pd.DataFrame, path: Path) -> None:
    merged = df.copy()
    for col in scored.columns:
        if col not in ("row_index",):
            merged[col] = scored[col].values

    examples: list[pd.Series] = []
    for decision in [DECISION_ACCEPT, DECISION_REVIEW, DECISION_REJECT]:
        sub = merged[merged["decision"] == decision]
        if sub.empty:
            continue
        # prefer a full-pass example if any
        if decision != DECISION_REJECT:
            pass_rows = sub[sub.get("full_behavioural_pass", False) == True]  # noqa: E712
            if len(pass_rows):
                examples.append(pass_rows.iloc[0])
                continue
        examples.append(sub.iloc[0])

    lines = [
        "# Risk toolkit examples",
        "",
        "Illustrative FSM health reports from the frozen master dataset. "
        "Generated by `scripts/risk_toolkit.py`.",
        "",
    ]
    for row in examples:
        if "full_behavioural_pass" in row.index:
            row = row.copy()
            try:
                row["full_behavioural_pass"] = parse_bool(row["full_behavioural_pass"])
            except ValueError:
                pass
        scored_dict = score_row(row)
        lines.append(f"## Example: `{row.get('run_id', 'unknown')}`")
        lines.append("")
        lines.append("```")
        lines.append(format_health_report(row, scored_dict))
        lines.append("```")
        if "full_behavioural_pass" in row.index:
            lines.append(
                f"*Retrospective outcome (not used by toolkit): "
                f"full_behavioural_pass = {row['full_behavioural_pass']}*"
            )
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pre-oracle FSM Behavioural Risk Toolkit (BRS + AutoReject + health reports)."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=MASTER_CSV,
        help="Input CSV (master dataset or compatible row export)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=TABLES_DIR / "risk_toolkit_predictions.csv",
        help="Batch predictions output CSV",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Single run_id for health report mode",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print FSM health report (requires --run-id or scores first row)",
    )
    parser.add_argument(
        "--write-validation",
        action="store_true",
        default=True,
        help="Write validation markdown (default: on)",
    )
    parser.add_argument(
        "--no-write-validation",
        action="store_false",
        dest="write_validation",
        help="Skip validation markdown",
    )
    parser.add_argument(
        "--write-examples",
        action="store_true",
        default=True,
        help="Write examples markdown (default: on)",
    )
    parser.add_argument(
        "--no-write-examples",
        action="store_false",
        dest="write_examples",
        help="Skip examples markdown",
    )
    return parser


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    args = build_parser().parse_args()

    df = load_frame(args.input)
    scored = score_dataframe(df)

    if args.report:
        if args.run_id:
            if "run_id" not in df.columns:
                print("ERROR: --run-id requires run_id column in input", file=sys.stderr)
                raise SystemExit(1)
            match = df[df["run_id"] == args.run_id]
            if match.empty:
                print(f"ERROR: run_id not found: {args.run_id}", file=sys.stderr)
                raise SystemExit(1)
            row = match.iloc[0]
        else:
            row = df.iloc[0]
        print(format_health_report(row, score_row(row)))
        return

    out_df = df.copy()
    for col in scored.columns:
        if col != "row_index":
            out_df[col] = scored[col].values

    args.output.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.output, index=False)
    print(f"Wrote {args.output} ({len(out_df)} rows)")

    if args.write_validation:
        val_path = TABLES_DIR / "risk_toolkit_validation.md"
        val_path.write_text(validate_on_scored_cohort(df, scored), encoding="utf-8")
        print(f"Wrote {val_path}")

    if args.write_examples:
        ex_path = TABLES_DIR / "risk_toolkit_examples.md"
        write_examples(df, scored, ex_path)
        print(f"Wrote {ex_path}")


if __name__ == "__main__":
    main()
