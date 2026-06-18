# RAP-AQ replication package — reportability audit for LLM-generated FSMs

Frozen reproducibility artefact for the **RAP-AQ** manuscript submitted to **Empirical Software Engineering** (EMSE).

| Resource | Identifier |
|----------|------------|
| GitHub | [cesar-andress/fsm-behavioural-predictors](https://github.com/cesar-andress/fsm-behavioural-predictors) |
| Zenodo (this release) | [10.5281/zenodo.20738203](https://doi.org/10.5281/zenodo.20738203) |
| Zenodo (concept, all versions) | [10.5281/zenodo.20598128](https://doi.org/10.5281/zenodo.20598128) |

**Release tag:** `v1.0.0-submission`

This release contains the complete reproducibility package used for the submission manuscript, including:

- RAP-AQ reportability audit workflow
- grouped-hold-out definability audit (`n_dc`)
- prevalence-only baseline analysis
- fixed audit predictor contract
- pair-partition diagnostics
- simulation and methodological-support artefacts
- manuscript tables and figures
- reproducibility scripts and Make targets

**Primary entry point:**

```bash
make reproduce
```

The release freezes the submission artefact associated with DOI [10.5281/zenodo.20738203](https://doi.org/10.5281/zenodo.20738203) and is intended to support independent verification of all results reported in the manuscript. **No post-submission analyses are included in this release.**

The LaTeX manuscript is **not** included in this repository.

---

## 1. Project overview

This package supports a **reportability audit** on a frozen merge of LLM-generated FSM campaign exports:

- **209** oracle-scored episodes from **12** requirement systems (`system_id`) and **4** LLM synthesis sources (`model`)
- **Bounded reportability class:** under leave-one-`system_id`-out (LOSO) grouped hold-out, cross-system ROC-AUC is largely undefined (`n_dc = 2/12` dual-class withheld systems)
- **Fixed audit predictor contract:** repeated-seed stratified cross-validation (100 fold seeds) for the pre-registered structural tally contract (`B_basic_structural`)
- **Prevalence-only baseline:** fold-contained prevalence ranking and Spearman association with out-of-fold scores
- **Pair-partition diagnostic:** grouped AUC decomposition and cluster-bootstrap uncertainty by `system_id`
- **Optional contrast:** nominal pooled-CV versus LOSO Δ with cluster bootstrap (5000 iterations)

Frozen data, analysis scripts, and primary outputs under `outputs/`. **No LLM inference or oracle re-execution** is required.

See [ARTIFACT_MANIFEST.md](ARTIFACT_MANIFEST.md) and [REPRODUCIBILITY.md](REPRODUCIBILITY.md). Legacy predictor-comparison material is documented in [docs/legacy_deposit.md](docs/legacy_deposit.md).

---

## 2. Dataset description

| Dataset | Location | Description |
|---------|----------|-------------|
| Frozen campaign records | `data/raw/` | Immutable primary inputs |
| Master analysis table | `data/processed/master_analysis_dataset.csv` | One row per episode; structural features and behavioural outcomes |
| Derived profiles | `data/processed/profile_*.csv` | Offline structural metric summaries |

**Cohort facts (frozen merge):**

| Metric | Value |
|--------|------:|
| Total generation episodes | 240 |
| Oracle-scored episodes | 209 (87.1%) |
| `full_behavioural_pass` (scored) | 30 (14.4%) |
| Requirement systems (`system_id`) | 12 |
| LLM synthesis sources (`model`) | 4 |

Column definitions: [docs/data_dictionary.md](docs/data_dictionary.md).

---

## 3. Directory layout

```
.
├── README.md
├── ARTIFACT_MANIFEST.md
├── REPRODUCIBILITY.md
├── RELEASE_NOTES_v1.0.0-submission.md
├── LICENSE
├── CITATION.cff
├── zenodo.json
├── Makefile
├── data/raw/
├── data/processed/
├── scripts/
├── outputs/          # primary RAP-AQ submission outputs
└── results/          # legacy deposit-only outputs
```

---

## 4. Software requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.11 (Makefile default) |
| numpy, pandas, scipy, scikit-learn, matplotlib | See `requirements.txt` |
| seaborn | ≥0.13 (environment gate via `make check-env`) |

```bash
conda env create -f environment.yml
conda activate fsm-behavioural-predictors
make check-env
```

No GPU or cloud LLM API access is required.

---

## 5. Replication instructions

```bash
make reproduce
```

Runs `build-master` → `strengthen-stats` → `methodological-upgrade` → `verify-submission`. Primary manuscript tables and figures live under `outputs/`.

**Reference runtime (author workstation):** ~3–4 min.

Optional legacy deposit-only pipeline (appendix predictor-study artefacts under `results/`):

```bash
make legacy-reproduce
make verify-manuscript
```

---

## 6. Manuscript mapping (summary)

| RAP-AQ component | Primary artefact outputs |
|----------------|-------------------------|
| Definability audit (`n_dc`) | `outputs/tables/definability_audit.csv`, `outputs/figures/definability_map.png` |
| Fixed audit predictor contract | `outputs/tables/table5_strengthened.csv` |
| Prevalence-only baseline | `outputs/tables/prevalence_baseline_cv.csv`, `outputs/figures/prevalence_baseline_comparison.png` |
| Pair-partition diagnostic | `outputs/tables/grouped_auc_decomposition.csv`, `group_pair_contribution.csv`, `outputs/figures/sim_auc_components.png` |
| Simulation / methodological support | `outputs/tables/simulation_grouped_reportability.csv` |
| Optional CV–LOSO contrast | `outputs/tables/table6_strengthened.csv`, `outputs/figures/bootstrap_delta_distribution.png` |

Full mapping: [ARTIFACT_MANIFEST.md](ARTIFACT_MANIFEST.md).

---

## 7. Protocol constants

| Parameter | Value | Source |
|-----------|-------|--------|
| CV fold seeds | 0–99 | `scripts/repro_config.py` → `STRENGTHEN_SEEDS` |
| Classifier | Random forest | `STRENGTHEN_CLASSIFIER` |
| Bootstrap iterations | 5000 | `N_BOOTSTRAP_ITERATIONS` |
| Bootstrap unit | Cluster by `system_id` | `cluster_bootstrap_delta.py`, `grouped_auc_bootstrap.py` |

---

## 8. What is not included

| Excluded | Reason |
|----------|--------|
| LaTeX manuscript | Private author tree |
| Live LLM inference | Frozen in `data/raw/` |
| Post-submission analyses | Out of scope for this freeze |
| Reviewer correspondence | Confidential |

---

## 9. Citation

```bibtex
@software{rap_aq_artifact_2026,
  author       = {Andr\'es, C\'esar},
  title        = {Replication Package: RAP-AQ Reportability Audit for LLM-Generated Finite State Machines},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {v1.0.0-submission},
  doi          = {10.5281/zenodo.20738203},
  url          = {https://github.com/cesar-andress/fsm-behavioural-predictors}
}
```

Machine-readable metadata: [CITATION.cff](CITATION.cff). Zenodo record: [docs/zenodo_record.md](docs/zenodo_record.md).

---

## 10. License and contact

MIT License — see [LICENSE](LICENSE).

**Corresponding author:** César Andrés — [cesar.andress@ucjc.edu](mailto:cesar.andress@ucjc.edu) — ORCID [0009-0001-8968-3404](https://orcid.org/0009-0001-8968-3404)

**Issue tracker:** [GitHub Issues](https://github.com/cesar-andress/fsm-behavioural-predictors/issues)
