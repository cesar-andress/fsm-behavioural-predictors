# Risk toolkit validation

Retrospective evaluation on behaviourally scored runs in the frozen cohort. **Triage audit only** — not certification of behavioural correctness.

- Evaluation set: **209** scored runs (30 full behavioural pass, 14.4% prevalence).
- Thresholds: `T_REVIEW=25.0`, `T_REJECT=35.0`; any gate failure ⇒ reject.

## Decision buckets

| decision | count | share | full_pass_count | full_pass_rate |
| --- | --- | --- | --- | --- |
| accept_for_behavioural_testing | 98 | 0.469 | 25 | 0.255 |
| review_before_testing | 65 | 0.311 | 5 | 0.077 |
| reject_or_regenerate | 46 | 0.220 | 0 | 0.000 |

## Error-oriented metrics (exploratory)

- False rejections (full pass but rejected): **0**
- False acceptances (non-pass but accepted for testing): **73**
- Coverage of behavioural failures in reject+review buckets: **106 / 179** (59.2%)

## Interpretation guardrails

- Accept decisions prioritise oracle budget; they do **not** guarantee pass.
- Reject decisions are conservative when structural gates fail (0% full pass in this cohort).
- Thresholds are frozen from cohort quartiles; not hyperparameter-tuned.
- Do not treat BRS as a probability of correctness.
