# Artifact manifest — manuscript tables and figures

Maps every manuscript table and figure to its generating script, input data, and output file(s) in this repository.

**Input data (all analyses):** `data/processed/master_analysis_dataset.csv` (built from frozen `data/raw/` by `scripts/build_master_dataset.py`).

**Strengthened pipeline orchestrator:** `scripts/run_strengthened_stats.py`  
**Legacy pipeline orchestrator:** `make reproduce` (see [REPRODUCIBILITY.md](REPRODUCIBILITY.md))

Legend: **Status** — `OK` = output exists and matches manuscript at audit time (2026-06-15); `DEPOSIT-ONLY` = archived but not cited in manuscript PDF; `EMBEDDED` = values transcribed into LaTeX from artefact export.

---

## Primary Results (Section 5)

### Tables

| Manuscript ID | Label | Source script | Source data | Generated output | Status |
|---------------|-------|---------------|-------------|------------------|--------|
| Table (§4) | `tab:target-distribution` | `scripts/generate_tables.py` → `scripts/build_master_dataset.py` | `data/processed/master_analysis_dataset.csv` | `results/tables/target_distribution.md` | EMBEDDED — cohort counts transcribed into LaTeX |
| Table 5.1 | `tab:definibility-audit` | `scripts/definibility_audit.py` | `master_analysis_dataset.csv` | `outputs/tables/definibility_audit.csv`, `.md`, `definibility_audit_summary.csv` | EMBEDDED — per-system rows in LaTeX match CSV |
| Table 5.2 | `tab:model-performance` | `scripts/strengthened_tables.py` ← `repeated_seed_cv.py` | `master_analysis_dataset.csv` | `outputs/tables/table5_strengthened.csv`, `.md`; detail: `repeated_seed_cv_summary.csv` | EMBEDDED — RF intervals match CSV formatted columns |
| Table 5.3 | `tab:prevalence-association` | `scripts/prevalence_correlation.py`, `prevalence_baseline.py`, `strengthened_tables.py` | `master_analysis_dataset.csv` | `outputs/tables/prevalence_correlation.csv`, `prevalence_baseline_cv.csv`, `table5_strengthened.csv` (Family B row) | EMBEDDED — ρ and baseline AUC match CSV |
| Table 5.4 | `tab:loso-summary` | `scripts/strengthened_tables.py` ← `cluster_bootstrap_delta.py`, `repeated_seed_cv.py`, `definibility_audit.py` | `master_analysis_dataset.csv` | `outputs/tables/table6_strengthened.csv`, `.md`; detail: `bootstrap_delta.csv`, `bootstrap_delta_iterations.csv` | EMBEDDED — Δ and bootstrap limits match CSV |

### Figures

| Manuscript ID | Label | Source script | Source data | Generated output | Status |
|---------------|-------|---------------|-------------|------------------|--------|
| Fig. 5.1 | `fig:definibility-map` | `scripts/strengthened_figures.py` ← `definibility_audit.py` | `outputs/tables/definibility_audit.csv` | `outputs/figures/definibility_map.png`, `.pdf` | OK — copied to `paper/figures/` |
| Fig. 5.2 | `fig:cv-seed-distribution-family-b` | `scripts/strengthened_figures.py` ← `repeated_seed_cv.py` | `outputs/stats/repeated_seed_oof_predictions.csv` | `outputs/figures/cv_seed_distribution_family_b.png`, `.pdf` | OK |
| Fig. 5.3 | `fig:prevalence-baseline-comparison` | `scripts/strengthened_figures.py` ← `prevalence_baseline.py`, `repeated_seed_cv.py` | `master_analysis_dataset.csv` | `outputs/figures/prevalence_baseline_comparison.png`, `.pdf` | OK |
| Fig. 5.4 | `fig:bootstrap-delta-distribution` | `scripts/strengthened_figures.py` ← `cluster_bootstrap_delta.py` | `outputs/tables/bootstrap_delta_iterations.csv` | `outputs/figures/bootstrap_delta_distribution.png`, `.pdf` | OK |
| Fig. 5.5 | `fig:bpr-by-gate` | `scripts/profile_predictive_signals.py` | `master_analysis_dataset.csv` | `results/figures/bpr_by_gate.png`, `.pdf` | OK — synced to `paper/figures/` |

---

## Study design (Section 3) — protocol tables

| Manuscript ID | Label | Source | Status |
|---------------|-------|--------|--------|
| Table 3.1 | `tab:variable-glossary` | Authored in `paper/sections/03_study_design.tex` | N/A — not generated |
| Table 3.2 | `tab:predictor-families` | Authored in `paper/sections/03_study_design.tex` | N/A |
| Table 3.3 | `tab:evaluation-protocol` | Authored in `paper/sections/03_study_design.tex`; strengthened constants in `scripts/repro_config.py` | OK — protocol matches `STRENGTHEN_*` constants |

---

## Appendix — supporting tables

| Manuscript ID | Label | Source script | Source data | Generated output | Status |
|---------------|-------|---------------|-------------|------------------|--------|
| App. Table | `tab:predictive-signal-profile` | `scripts/profile_predictive_signals.py` | `master_analysis_dataset.csv` | `results/tables/predictive_signal_profile.md` | EMBEDDED — PB *r* values match MD export |
| App. Table | `tab:upstream-screen` | `scripts/pre_oracle_prediction.py` | `master_analysis_dataset.csv` | `results/tables/pre_oracle_model_performance.md` | EMBEDDED — RF row 0.983 ± 0.011 matches export |
| App. Table | `tab:feature-importance` | `scripts/model_behavioural_correctness.py` | `master_analysis_dataset.csv` | `results/tables/model_feature_importance.md` | EMBEDDED — top weights transcribed |
| App. Table | `tab:lomo-summary` | `scripts/lomo_model_evaluation.py` | `master_analysis_dataset.csv` | `results/tables/lomo_summary.md`, `lomo_results.md` | EMBEDDED — RF Family B row matches export |
| App. Table | `tab:toolkit-validation` | `scripts/risk_toolkit.py` | `master_analysis_dataset.csv` | `results/tables/risk_toolkit_validation.md`, `risk_toolkit_predictions.csv` | EMBEDDED — bucket counts match export |
| App. Table | `tab:artifact-outputs` | Authored index in `paper/sections/09_appendix_artefact.tex` | — | — | OK — paths match this manifest |

---

## Appendix — supporting figures

| Manuscript ID | Label | Source script | Source data | Generated output | Status |
|---------------|-------|---------------|-------------|------------------|--------|
| App. Fig. | `fig:reproducibility-arch` | TikZ (`paper/figures/fig_reproducibility_arch.tex`) | — | Compiled in PDF | N/A — authored diagram |
| App. Fig. | `fig:bpr-by-system` | `scripts/profile_predictive_signals.py` | `master_analysis_dataset.csv` | `results/figures/bpr_by_system.png`, `.pdf` | OK |
| App. Fig. | `fig:bpr-by-model` | `scripts/profile_predictive_signals.py` | `master_analysis_dataset.csv` | `results/figures/bpr_by_model.png`, `.pdf` | OK |
| App. Fig. | `fig:roc-curves` | `scripts/model_behavioural_correctness.py` | `master_analysis_dataset.csv` | `results/figures/roc_curves.png`, `.pdf` | OK |
| App. Fig. | `fig:pr-curves` | `scripts/model_behavioural_correctness.py` | `master_analysis_dataset.csv` | `results/figures/precision_recall_curves.png`, `.pdf` | OK |
| App. Fig. | `fig:lomo-heatmap` | `scripts/lomo_model_evaluation.py` | `master_analysis_dataset.csv` | `results/figures/lomo_heatmap.png`, `.pdf` | OK |
| — | `fig:loso-heatmap` | `scripts/loso_system_evaluation.py` | `master_analysis_dataset.csv` | `results/figures/loso_system_heatmap.png`, `.pdf` | DEPOSIT-ONLY — removed from manuscript; retained for traceability |

---

## Conceptual / running-example figures (authored)

| Manuscript ID | Label | Source | Status |
|---------------|-------|--------|--------|
| Fig. 2 | `fig:running-example` | `paper/figures/fig_running_example.tex` | N/A — TikZ |
| Fig. 3 | `fig:repair-loop` | `paper/figures/fig_repair_loop.tex` | N/A — TikZ |

---

## Strengthened-stats intermediate outputs (not directly cited)

| Output | Script | Purpose |
|--------|--------|---------|
| `outputs/stats/repeated_seed_oof_predictions.csv` (~6.3 MB) | `repeated_seed_cv.py` | Per-seed OOF scores for CV figures and correlation |
| `outputs/stats/repeated_seed_loso_predictions.csv` | `definibility_audit.py` | Per-system LOSO predictions |
| `outputs/stats/prevalence_baseline_cv_predictions.csv` | `prevalence_baseline.py` | Prevalence-only baseline OOF scores |
| `outputs/stats/prevalence_baseline_loso_predictions.csv` | `prevalence_baseline.py` | Prevalence baseline LOSO |
| `outputs/stats/bootstrap_delta.json` | `cluster_bootstrap_delta.py` | Machine-readable bootstrap summary |
| `outputs/tables/bootstrap_delta_iterations.csv` (~1.5 MB) | `cluster_bootstrap_delta.py` | Full bootstrap draw log |
| `outputs/tables/prevalence_correlation_by_seed.csv` | `prevalence_correlation.py` | Per-seed Spearman values |
| `outputs/stats/strengthened_stats_manifest.json` | `run_strengthened_stats.py` | Release manifest (34 outputs, seeds, commit hash) |

---

## Legacy single-seed outputs (supporting)

| Output prefix | Script |
|---------------|--------|
| `results/tables/model_performance.md` | `model_behavioural_correctness.py` |
| `results/tables/model_validation.md` | `model_behavioural_correctness.py` |
| `results/tables/loso_system_summary.md` | `loso_system_evaluation.py` |
| `results/tables/descriptive_profile.md` | `generate_tables.py` |
| `results/tables/profile_*.csv` | `generate_tables.py` |

Verification entry point: `scripts/verify_manuscript_outputs.py` (legacy `results/` paths only; does not yet validate `outputs/`).
