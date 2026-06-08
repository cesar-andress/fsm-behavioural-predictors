# Master dataset validation report

**Output:** `data/processed/master_analysis_dataset.csv`
**Rows:** 240
**Duplicate `run_id` count:** 0

## Missing values per column

| Column | Missing |
|--------|--------:|
| `run_id` | 0 |
| `model` | 0 |
| `system_id` | 0 |
| `replicate` | 0 |
| `g1_pass` | 0 |
| `g2_pass` | 31 |
| `g3_pass` | 31 |
| `g3a_pass` | 31 |
| `requirement_coverage` | 31 |
| `n_states` | 0 |
| `n_events` | 0 |
| `n_transitions` | 0 |
| `n_unreachable_states` | 31 |
| `missing_transitions` | 31 |
| `extra_transitions` | 31 |
| `behavioral_pass_rate` | 31 |
| `full_behavioural_pass` | 31 |
| `behaviourally_scored` | 0 |
| `failure_stage` | 0 |

## Target and gate distributions

- `g1_pass` true: **235** / 240
- `g2_pass` true: **189** / 240
- `behaviourally_scored` true: **209** / 240
- `full_behavioural_pass` true: **30** / 240

## `behavioral_pass_rate` value counts (scored rows only)

| BPR | Count |
|-----|------:|
| 0.166667 | 5 |
| 0.25 | 60 |
| 0.294118 | 15 |
| 0.3125 | 14 |
| 0.352941 | 15 |
| 0.5 | 45 |
| 0.666667 | 5 |
| 0.705882 | 5 |
| 0.764706 | 5 |
| 0.875 | 10 |
| 1 | 30 |
