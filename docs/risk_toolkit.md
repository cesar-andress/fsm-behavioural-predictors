# FSM Behavioural Risk Toolkit

Lightweight **pre-oracle triage** for LLM-generated finite state machines.
Part of the SQJ 2026 public artefact (`fsm-behavioural-predictors`).

> **Triage only — not certification.** The toolkit ranks behavioural risk using
> cheap structural signals. It does **not** guarantee behavioural correctness and
> must not replace oracle evaluation.

## Components

### 1. Behavioural Risk Score (BRS)

Continuous score on **[0, 100]** where **higher = higher pre-oracle behavioural risk**.

**Allowed inputs only:**

| Feature | Role |
|---------|------|
| `g2_pass`, `g3_pass`, `g3a_pass` | Structural gate outcomes |
| `requirement_coverage` | Fraction of requirements covered by transitions |
| `n_states`, `n_events`, `n_transitions`, `n_unreachable_states` | Basic graph counts |

**Forbidden (never used):** `missing_transitions`, `extra_transitions`,
`behavioral_pass_rate`, `full_behavioural_pass`, `model`, `system_id`, or any
oracle-derived variable.

**Fixed formula** (weights are **not** outcome-tuned):

```
gate_failures = (¬g2) + (¬g3) + (¬g3a)
gate_risk     = gate_failures × (50/3)                    # 0–50
coverage_risk = 35 × max(0, (0.875 − requirement_coverage) / 0.875)
state_risk    = 15 × clip((n_states − 2) / 2, 0, 1)
event_risk    =  5 × clip((n_events − 4) / 8, 0, 1)
BRS           = min(100, gate_risk + coverage_risk + state_risk + event_risk)
```

`0.875` is the 75th percentile of `requirement_coverage` in the frozen scored cohort.

**Missing values (conservative):** rows that fail early parsing may lack gate and coverage
fields. The toolkit treats missing gates as failed, `requirement_coverage` as `0.0`, and
`n_unreachable_states` as `0` before scoring. This yields high BRS and reject decisions
without using oracle or outcome columns.

### 2. AutoReject

Maps BRS and gate status to one of three decisions:

| Decision | Meaning |
|----------|---------|
| `accept_for_behavioural_testing` | Lower pre-oracle risk; proceed to oracle |
| `review_before_testing` | Elevated risk; manual review first |
| `reject_or_regenerate` | High risk or gate failure; fix before testing |

**Conservative rules** (frozen thresholds):

1. If **any** of `g2_pass`, `g3_pass`, `g3a_pass` is false → `reject_or_regenerate`
   (`gate_failure`). In the frozen cohort, no full behavioural pass occurs when gates fail.
2. Else if `BRS ≥ 35` → `reject_or_regenerate` (`high_brs`).
   Set above the maximum BRS observed when all gates pass (≈30), so gate-passing runs
   are never rejected on score alone in this cohort.
3. Else if `BRS ≥ 25` → `review_before_testing` (`elevated_brs`).
   Approximates the gate-passing cohort median.
4. Else → `accept_for_behavioural_testing` (`low_brs`).

Thresholds `25` and `35` are documented constants in `scripts/risk_toolkit.py`;
they were chosen from gate-passing quartiles, not by optimising accuracy on outcomes.

### 3. FSM Health Report

Human-readable CLI report with BRS, risk level, decision, contributing factors, and
recommended next action.

## Usage

```bash
# Batch scoring (default paths)
make risk-toolkit

# Explicit paths
python scripts/risk_toolkit.py \
  --input data/processed/master_analysis_dataset.csv \
  --output results/tables/risk_toolkit_predictions.csv

# Single-run health report
python scripts/risk_toolkit.py \
  --input data/processed/master_analysis_dataset.csv \
  --run-id <run_id> \
  --report
```

## Outputs

| File | Description |
|------|-------------|
| `results/tables/risk_toolkit_predictions.csv` | Input rows + BRS, risk level, decision |
| `results/tables/risk_toolkit_validation.md` | Retrospective triage audit on scored cohort |
| `results/tables/risk_toolkit_examples.md` | Sample health reports |

## Validation

On behaviourally scored runs (`n=209`), the toolkit reports:

- Counts and full-pass rates per decision bucket
- False rejections (full pass but rejected)
- False acceptances (non-pass but accepted)
- Coverage of behavioural failures in reject+review buckets

See `results/tables/risk_toolkit_validation.md` after `make risk-toolkit`.

## Design rationale

- **Interpretable:** each BRS component maps to an inspectable structural factor.
- **Pre-oracle:** no reference-difference or behavioural-outcome features.
- **Conservative:** gate failures always reject; BRS reject threshold exceeds observed
  gate-passing maximum in the frozen cohort.
- **Not overfit:** fixed weights and round thresholds; no hyperparameter search on
  `full_behavioural_pass`.

## Limitations

- Calibrated on a single frozen EMSE 2026 cohort (four Ollama models, twelve systems).
- Random cross-validation overstates cross-specification generalization (see LOSO study).
- Accept decisions still include many eventual behavioural failures — expected for triage.

## Availability

The toolkit is part of the archived replication package:

- **Zenodo:** [10.5281/zenodo.20738203](https://doi.org/10.5281/zenodo.20738203)
- **GitHub:** https://github.com/cesar-andress/fsm-behavioural-predictors (tag `v1.0.0-submission`)

See [zenodo_record.md](zenodo_record.md) for citation and reproducibility scope.
