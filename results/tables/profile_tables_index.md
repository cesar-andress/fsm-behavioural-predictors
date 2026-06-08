# Descriptive profiling tables

Generated from `data/processed/master_analysis_dataset.csv` by `scripts/generate_tables.py`.

| Table | Description |
|-------|-------------|
| `profile_cohort_summary.csv` | Overall cohort counts and pass rates. |
| `profile_gate_pass_rates.csv` | Structural gate pass counts and rates (including G2-pass denominators for G3/G3a). |
| `profile_by_model.csv` | Descriptive profiles grouped by LLM model. |
| `profile_by_system.csv` | Descriptive profiles grouped by system specification. |
| `profile_failure_stage.csv` | Run counts by pipeline failure stage. |
| `profile_numeric_summary.csv` | Numeric structural and behavioural summaries by analysis stratum. |
| `profile_bpr_distribution.csv` | Exact behavioural pass rate (BPR) value counts among scored runs. |
| `profile_gate_combinations.csv` | Run counts by G1–G3a gate pattern among structurally evaluable runs. |
