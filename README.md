# RAP-AQ replication package — reportability audit for LLM-generated FSMs

**Canonical public artefact** for the EMSE manuscript on **RAP-AQ** (reportability audit protocol): a fixed-audit evaluation of whether bounded cross-group ranking metrics are reportable on a frozen cohort of LLM-generated finite state machines (FSMs).

| Resource | Identifier |
|----------|------------|
| GitHub | [cesar-andress/fsm-behavioural-predictors](https://github.com/cesar-andress/fsm-behavioural-predictors) |
| Zenodo (concept) | [10.5281/zenodo.20598128](https://doi.org/10.5281/zenodo.20598128) |
| Zenodo (version archive) | [10.5281/zenodo.20598129](https://doi.org/10.5281/zenodo.20598129) (update at release) |

**Submission freeze tag:** `v1.0.0-submission`

The LaTeX manuscript is **not** included in this repository (private author tree).

---

## 1. Project overview

This package supports a **reportability audit** on a frozen merge of LLM-generated FSM campaign exports:

- **209** oracle-scored episodes from **12** requirement systems (`system_id`) and **4** LLM synthesis sources (`model`)
- **Step 1 — bounded reportability class:** under leave-one-`system_id`-out (LOSO) grouped hold-out, cross-system ROC-AUC is largely undefined (`n_dc = 2/12` dual-class withheld systems)
- **Step 2 — fixed audit predictor contract:** repeated-seed stratified cross-validation (100 fold seeds) for the pre-registered structural tally contract (`B_basic_structural`)
- **Step 3 — prevalence-only baseline:** fold-contained prevalence ranking and Spearman association with out-of-fold scores
- **Step 4 — pair-partition diagnostic:** grouped AUC decomposition and cluster-bootstrap uncertainty by `system_id`
- **Optional contrast:** nominal pooled-CV versus LOSO Δ with cluster bootstrap (5000 iterations)

Frozen data, analysis scripts, primary outputs under `outputs/`, and **legacy deposit-only** outputs under `results/`. **No LLM inference or oracle re-execution** is required.

See [ARTIFACT_MANIFEST.md](ARTIFACT_MANIFEST.md) and [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

Legacy predictor-comparison material (Families A–D screen, LOMO, repair-loop figure source) is documented in [docs/legacy_deposit.md](docs/legacy_deposit.md).

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
├── RELEASE_CHECKLIST_v1.0.0-submission.md
├── RELEASE_NOTES_v1.0.0-submission.md
├── LICENSE
├── CITATION.cff
├── zenodo.json
├── Makefile
├── data/raw/                  # Frozen primary inputs
├── data/processed/            # Analysis-ready tables
├── scripts/                   # Analysis pipelines
├── outputs/                   # RAP-AQ primary outputs (submission freeze)
│   ├── tables/
│   ├── figures/
│   └── stats/
├── results/                   # Legacy deposit-only outputs
└── docs/
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

### RAP-AQ submission freeze (recommended)

```bash
make submission-freeze
```

Runs `build-master` → `strengthen-stats` → `methodological-upgrade` → `verify-submission`. Primary manuscript tables and figures live under `outputs/`.

**Reference runtime (author workstation, 2026-06-17):** ~3–4 min for `strengthen-stats` plus ~30 s for methodological-upgrade.

### Legacy deposit-only pipeline

```bash
make legacy-reproduce    # alias: make reproduce
make verify-manuscript   # checks 24 paths under results/
```

Regenerates Families A–D CV, LOMO, pre-oracle screen, and appendix figures under `results/`. **Not cited** in the RAP-AQ manuscript body.

---

## 6. Manuscript mapping (summary)

| RAP-AQ step | Primary artefact outputs |
|-------------|-------------------------|
| Reportability audit (definibility) | `outputs/tables/definibility_audit.csv`, `outputs/figures/definibility_map.png` |
| Fixed audit predictor contract | `outputs/tables/table5_strengthened.csv` |
| Prevalence-only baseline | `outputs/tables/prevalence_baseline_cv.csv`, `outputs/figures/prevalence_baseline_comparison.png` |
| Pair-partition diagnostic | `outputs/tables/grouped_auc_decomposition.csv`, `group_pair_contribution.csv`, `outputs/figures/sim_auc_components.png` |
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

Orchestrator: `scripts/run_strengthened_stats.py`.

---

## 8. What is not included

| Excluded | Reason |
|----------|--------|
| LaTeX manuscript | Private author tree |
| Live LLM inference | Frozen in `data/raw/` |
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
  doi          = {10.5281/zenodo.20598129},
  url          = {https://github.com/cesar-andress/fsm-behavioural-predictors}
}
```

Machine-readable metadata: [CITATION.cff](CITATION.cff).

---

## 10. License and contact

MIT License — see [LICENSE](LICENSE).

**Corresponding author:** César Andrés — [cesar.andress@ucjc.edu](mailto:cesar.andress@ucjc.edu) — ORCID [0009-0001-8968-3404](https://orcid.org/0009-0001-8968-3404)

**Issue tracker:** [GitHub Issues](https://github.com/cesar-andress/fsm-behavioural-predictors/issues)
