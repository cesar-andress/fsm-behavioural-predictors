# Target distribution

Descriptive summary of behavioural outcomes from `master_analysis_dataset.csv`.
No hypothesis tests; counts and rates only.

## Cohort counts

| Metric | Count | Rate |
|--------|------:|-----:|
| Total runs | 240 | 100.0% |
| `behaviourally_scored` | 209 | 87.1% |
| `full_behavioural_pass` (all runs) | 30 | 12.5% |
| `full_behavioural_pass` (scored runs) | 30 | 14.4% |
| `full_behavioural_pass` (G2-pass, scored) | 30 | 15.9% |

## `behavioral_pass_rate` summary (scored runs only)

| Statistic | Value |
|-----------|------:|
| n | 209 |
| mean | 0.487 |
| median | 0.353 |
| std | 0.271 |
| min | 0.167 |
| max | 1.000 |

## `full_behavioural_pass` among scored runs

| Value | Count | Proportion |
|-------|------:|-----------:|
| true | 30 | 14.4% |
| false | 179 | 85.6% |

## Notes

- Behaviourally non-scored runs (`behaviourally_scored=false`, n=31) have empty BPR; they are excluded from BPR summaries.
- G2-pass scored stratum: runs with `behaviourally_scored=true` and `g2_pass=true` (n=189).
