# Manuscript output crosswalk

Maps SQJ 2026 manuscript tables and empirical figures to files in this replication package.
TikZ figures (`fig:running-example`, `fig:repair-loop`, `fig:reproducibility-arch`) are authored in the private LaTeX manuscript, not regenerated here.

**Zenodo DOI:** [10.5281/zenodo.20598129](https://doi.org/10.5281/zenodo.20598129) (verified accessible; pre-submission release `v0.1.0-pre-submission`).

| Manuscript anchor | Package output(s) | Regeneration target |
|-------------------|-------------------|---------------------|
| Table `tab:target-distribution` | `results/tables/target_distribution.md` | `make profile-signals` |
| Table `tab:predictive-signal-profile` | `results/tables/predictive_signal_profile.md` | `make profile-signals` |
| Figs `fig:bpr-by-gate`, `fig:bpr-by-model`, `fig:bpr-by-system` | `results/figures/bpr_by_{gate,model,system}.png` | `make profile-signals` |
| Tables `tab:model-performance`, `tab:feature-importance` | `results/tables/model_{performance,feature_importance,validation}.md` | `make model-correctness` |
| Figs `fig:roc-curves`, `fig:pr-curves` | `results/figures/roc_curves.png`, `precision_recall_curves.png` | `make model-correctness` |
| Table `tab:pre-oracle-performance` | `results/tables/pre_oracle_model_performance.md` | `make pre-oracle` |
| Table `tab:loso-summary`; Fig `fig:loso-heatmap` | `results/tables/loso_system_{summary,results}.md`; `results/figures/loso_system_heatmap.png` | `make loso-systems` |
| Table `tab:lomo-summary`; Fig `fig:lomo-heatmap` | `results/tables/lomo_{summary,results}.md`; `results/figures/lomo_heatmap.png` | `make lomo-models` |
| Table `tab:toolkit-validation` | `results/tables/risk_toolkit_validation.md`, `risk_toolkit_predictions.csv` | `make risk-toolkit` |
| Master cohort | `data/processed/master_analysis_dataset.csv` | `make build-master` |
| Descriptive profiles | `results/tables/descriptive_profile.md`, `profile_tables_index.md`, `profile_*.csv` | `make profile-signals`, `make tables` |

Automated check: `make verify-manuscript` (runs at end of `make reproduce`).
