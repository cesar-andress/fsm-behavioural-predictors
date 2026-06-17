# Artifact manifest — RAP-AQ manuscript tables and figures

Maps every cited manuscript table and figure to its generating script, input data, and output file(s).

**Input data (all analyses):** `data/processed/master_analysis_dataset.csv` (from frozen `data/raw/` via `scripts/build_master_dataset.py`).

**Primary orchestrator:** `make submission-freeze` (`run_strengthened_stats.py` + methodological-upgrade scripts)  
**Legacy deposit:** `make legacy-reproduce` — see [docs/legacy_deposit.md](docs/legacy_deposit.md)

Legend: **Status** — `OK` = output exists at submission freeze; `DEPOSIT-ONLY` = archived, not cited in manuscript PDF; `EMBEDDED` = values transcribed into LaTeX.

---

## RAP-AQ Results (primary)

### Tables

| Manuscript anchor | Label | Source script | Generated output | Status |
|-------------------|-------|---------------|------------------|--------|
| Cohort counts | `tab:target-distribution` | `generate_tables.py` | `results/tables/target_distribution.md` | EMBEDDED |
| Step 2 — definability audit | `tab:definibility-audit` | `definibility_audit.py` | `outputs/tables/definibility_audit.csv`, `definibility_audit_summary.csv` | EMBEDDED |
| Step 3 — fixed audit predictor | `tab:model-performance` | `strengthened_tables.py` ← `repeated_seed_cv.py` | `outputs/tables/table5_strengthened.csv` | EMBEDDED |
| Step 3 — prevalence association | `tab:prevalence-association` | `prevalence_correlation.py`, `prevalence_baseline.py` | `outputs/tables/prevalence_correlation.csv`, `prevalence_baseline_cv.csv` | EMBEDDED |
| Step 4 — pair-partition diagnostic | `tab:grouped-auc` | `grouped_auc_decomposition.py` | `outputs/tables/grouped_auc_decomposition.csv`, `group_pair_contribution.csv` | EMBEDDED |
| Optional CV–LOSO contrast | `tab:loso-summary` | `strengthened_tables.py` ← `cluster_bootstrap_delta.py` | `outputs/tables/table6_strengthened.csv`, `bootstrap_delta.csv` | EMBEDDED |
| Simulation sensitivity | `tab:simulation-reportability` | `simulate_grouped_reportability.py` | `outputs/tables/simulation_grouped_reportability.csv` | EMBEDDED |

### Figures

| Manuscript anchor | Label | Source script | Generated output | Status |
|-------------------|-------|---------------|------------------|--------|
| Step 2 — definibility map | `fig:definibility-map` | `strengthened_figures.py` | `outputs/figures/definibility_map.png` | OK |
| Step 3 — prevalence baseline | `fig:prevalence-baseline-comparison` | `strengthened_figures.py` | `outputs/figures/prevalence_baseline_comparison.png` | OK |
| Step 4 — pair-partition components | `fig:sim-auc-components` | `simulate_grouped_reportability.py` | `outputs/figures/sim_auc_components.png` | OK |
| Optional CV–LOSO Δ | `fig:bootstrap-delta-distribution` | `strengthened_figures.py` | `outputs/figures/bootstrap_delta_distribution.png` | OK |
| Supporting BPR panel | `fig:bpr-by-gate` | `profile_predictive_signals.py` | `results/figures/bpr_by_gate.png` | OK |

**Deposit-only figure (not in manuscript PDF):** `outputs/figures/cv_seed_distribution_family_b.png` — seed distribution for fixed audit predictor contract.

---

## Study design — protocol tables (authored)

| Label | Source | Status |
|-------|--------|--------|
| `tab:variable-glossary` | `paper/sections/03_study_design.tex` | N/A |
| `tab:predictor-contracts` | `paper/sections/03_study_design.tex` | N/A |
| `tab:evaluation-protocol` | `paper/sections/03_study_design.tex`; constants in `repro_config.py` | OK |

---

## Appendix — supporting material

| Label | Source script | Generated output | Status |
|-------|---------------|------------------|--------|
| `tab:predictive-signal-profile` | `profile_predictive_signals.py` | `results/tables/predictive_signal_profile.md` | EMBEDDED |
| `tab:artifact-outputs` | Authored index in appendix | — | OK |
| `fig:reproducibility-arch` | TikZ (`fig_reproducibility_arch.tex`) | Compiled in PDF | N/A |
| `fig:bpr-by-system`, `fig:bpr-by-model` | `profile_predictive_signals.py` | `results/figures/bpr_by_*.png` | OK |
| `fig:roc-curves`, `fig:pr-curves` | `model_behavioural_correctness.py` | `results/figures/roc_curves.png`, etc. | OK |

---

## Legacy deposit-only (not cited in RAP-AQ manuscript)

| Item | Output | Script |
|------|--------|--------|
| LOMO summary | `results/tables/lomo_*.md` | `lomo_model_evaluation.py` |
| LOMO heatmap | `results/figures/lomo_heatmap.png` | `lomo_model_evaluation.py` |
| Pre-oracle screen | `results/tables/pre_oracle_*.md` | `pre_oracle_prediction.py` |
| Risk toolkit | `results/tables/risk_toolkit_*.md` | `risk_toolkit.py` |
| Repair-loop diagram | `fig_repair_loop.tex` (manuscript tree) | Authored — removed from PDF |

---

## Intermediate outputs

| Output | Script | Purpose |
|--------|--------|---------|
| `outputs/stats/repeated_seed_oof_predictions.csv` | `repeated_seed_cv.py` | Per-seed OOF scores |
| `outputs/stats/strengthened_stats_manifest.json` | `run_strengthened_stats.py` | Release manifest |
| `outputs/tables/grouped_auc_bootstrap_iterations.csv` | `grouped_auc_bootstrap.py` | Bootstrap draw log |
| `outputs/tables/bootstrap_delta_iterations.csv` | `cluster_bootstrap_delta.py` | CV–LOSO bootstrap log |

---

## Verification

| Target | Script | Scope |
|--------|--------|-------|
| `make verify-submission` | `scripts/verify_submission_outputs.py` | RAP-AQ paths under `outputs/` |
| `make verify-manuscript` | `scripts/verify_manuscript_outputs.py` | Legacy paths under `results/` |
