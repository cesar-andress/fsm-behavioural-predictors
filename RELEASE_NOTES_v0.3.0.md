# Release notes — v0.3.0-revision-candidate

**Comparison baseline:** [v0.2.0-submission-candidate](https://github.com/cesar-andress/fsm-behavioural-predictors/tree/v0.2.0-submission-candidate)  
**Prior public archive:** [v0.1.0-pre-submission](https://github.com/cesar-andress/fsm-behavioural-predictors/tree/v0.1.0-pre-submission) (Zenodo [10.5281/zenodo.20598129](https://doi.org/10.5281/zenodo.20598129))  
**Status:** revision-candidate documentation pass — tag not yet published.

---

## Summary

Version 0.3.0 is a **revision-candidate** release aligning the replication package with a **definibility-first** manuscript repositioning. It adds a strengthened-statistics layer (100 repeated CV seeds, cluster bootstrap), formal definability auditing, prevalence-structure controls, and updated primary Results tables/figures — without changing the frozen cohort or re-running LLM inference.

---

## Changes since v0.2.0-submission-candidate

### New: strengthened-statistics pipeline

- **Target:** `make strengthen-stats`
- **Orchestrator:** `scripts/run_strengthened_stats.py`
- **Output tree:** `outputs/` (34 files: tables, figures, stats intermediates, manifest)
- **New scripts:**
  - `repeated_seed_cv.py` — 100-seed pooled stratified CV for Families A–D
  - `definibility_audit.py` — per-`system_id` LOSO definability audit
  - `prevalence_baseline.py` — fold-contained prevalence-only baseline
  - `prevalence_correlation.py` — Spearman ρ between OOF scores and training-fold prevalence
  - `cluster_bootstrap_delta.py` — 5000-iteration cluster bootstrap of nominal CV–LOSO Δ
  - `strengthened_tables.py`, `strengthened_figures.py` — manuscript Tables 5.2–5.4 and primary figures
  - `metrics_utils.py`, `strengthen_io.py` — shared I/O and metric helpers
- **Constants extended in** `scripts/repro_config.py`: `STRENGTHEN_SEEDS`, `N_BOOTSTRAP_ITERATIONS`, aggregation rules

### Strengthened statistics (primary Results)

| Quantity | v0.3.0 strengthened estimate |
|----------|-------------------------------|
| Family B RF in-corpus ROC-AUC | 0.981 [0.976, 0.985] (100 seeds) |
| Definable LOSO systems | `n_dc = 2/12` (`hotel_booking`, `login_system`) |
| Definable LOSO AUCs (Family B RF) | 0.500, 0.667 (μ = 0.583) |
| Spearman ρ (OOF vs prevalence) | 0.584 [0.534, 0.629] |
| Prevalence-only baseline AUC | 0.958 [0.951, 0.964] |
| Nominal Family B Δ (CV − LOSO μ) | ≈ 0.397 |
| Cluster-bootstrap Δ interval | [−0.026, 0.772] (includes zero) |

### Definibility audit

- Formal per-`system_id` class-balance audit under LOSO grouped hold-out
- Outputs: `outputs/tables/definibility_audit.csv`, `outputs/figures/definibility_map.png`
- Replaces legacy multi-classifier LOSO heatmap as **primary** grouped-hold-out evidence in the manuscript
- Legacy heatmap retained in deposit (`results/figures/loso_system_heatmap.png`) for traceability only

### Prevalence baseline and correlation

- Fold-contained prevalence-only predictor (no graph tallies) under the same 100-seed CV protocol
- Spearman association between Family B OOF scores and training-fold `system_id` prevalence
- Outputs: `prevalence_correlation.csv`, `prevalence_baseline_cv.csv`, `prevalence_baseline_comparison.png`

### Manuscript repositioning (private LaTeX; not in this repo)

The companion manuscript at `~/papers/sqj2026/paper` was restructured for revision:

- **Title:** *Definibility-First Evaluation of Pre-Oracle Ranking for LLM-Generated Finite State Machines on a Sparse Oracle-Scored Cohort*
- **Results hierarchy:** definability (primary) → in-corpus stability (secondary) → prevalence association → exploratory CV–LOSO Δ (tertiary) → supporting gate/ref-diff analyses
- **Removed from PDF:** legacy LOSO heatmap figure (`fig:loso-heatmap`); deposit-only traceability
- **Rewritten sections:** Abstract, Introduction, Related Work, Results §5.1–5.5, Discussion, Threats, Conclusion, Appendix artefact index

### Figure and reproducibility hardening (v0.2.0 → HEAD)

Commits between v0.2.0 and HEAD (artefact):

- Improved figure readability (labels, DPI, heatmap N/A cells)
- Random-seed audit and `repro_config.py` centralisation
- Publication-quality figure regeneration (`figure_style.py`, updated analysis scripts)
- `verify_manuscript_outputs.py` for legacy `results/` path checks

### Documentation (this release pass)

- Rewritten `README.md` (v0.3.0 scope, dual pipeline)
- New `ARTIFACT_MANIFEST.md`, `REPRODUCIBILITY.md`, `RELEASE_READINESS_REPORT.md`
- Manuscript alignment audit: `../paper/paper_notes/MANUSCRIPT_ARTIFACT_ALIGNMENT.md`

---

## Unchanged from prior releases

| Item | Notes |
|------|-------|
| Frozen cohort | `data/raw/`, `data/processed/master_analysis_dataset.csv` — no new episodes |
| LLM inference | Not re-run; no API calls in reproduction path |
| Legacy `results/` pipeline | Still produced by `make reproduce`; appendix tables/figures unchanged in protocol |
| Scientific cohort facts | 209 scored episodes, 12 systems, 4 models, 30 full passes |

---

## Known gaps before publishing the tag

See [RELEASE_READINESS_REPORT.md](RELEASE_READINESS_REPORT.md) for the full audit. Highlights:

1. Strengthened scripts and `outputs/` staged but **not yet committed** at audit time
2. `CITATION.cff` and `zenodo.json` still reference v0.1.0-pre-submission
3. `verify_manuscript_outputs.py` does not validate `outputs/`
4. `make check-env` requires seaborn in the active environment
5. Strengthened figures require manual copy to `paper/figures/` (not in `generate_figures.py` sync list)

---

## Upgrade path for replicators

```bash
# From v0.2.0-submission-candidate
git fetch --tags
git checkout v0.3.0-revision-candidate   # after published
pip install -r requirements.txt          # or conda env update
make reproduce
make strengthen-stats
```

Compare `outputs/tables/table5_strengthened.csv` and `table6_strengthened.csv` against the archived manifest in the Zenodo deposit.

---

## Citation

Update Zenodo version metadata when publishing. Concept DOI: [10.5281/zenodo.20598128](https://doi.org/10.5281/zenodo.20598128).
