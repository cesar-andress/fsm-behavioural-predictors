# Definibility-First Evaluation of Pre-Oracle Ranking for LLM-Generated Finite State Machines

**Canonical public artefact repository** for the SQJ 2026 study on structural predictors of behavioural correctness in LLM-generated finite state machines (FSMs).

| Resource | Identifier |
|----------|------------|
| GitHub | [cesar-andress/fsm-behavioural-predictors](https://github.com/cesar-andress/fsm-behavioural-predictors) |
| Zenodo (concept) | [10.5281/zenodo.20598128](https://doi.org/10.5281/zenodo.20598128) |
| Zenodo (version archive) | [10.5281/zenodo.20598129](https://doi.org/10.5281/zenodo.20598129) (prior deposit; update at release) |

**Target release tag:** `v0.3.0-revision-candidate` (revision pass; not yet published).

**Private manuscript:** LaTeX sources live at `~/papers/sqj2026/paper` (sibling directory). They are **not** included in this repository.

---

## 1. Project overview

This replication package supports a **definibility-first** evaluation of pre-oracle ranking for behavioural correctness on a frozen merge of LLM-generated FSM campaign exports:

- **209** oracle-scored episodes from **12** requirement systems (`system_id`) and **4** LLM synthesis sources (`model`)
- **Primary constraint:** under leave-one-`system_id`-out (LOSO) grouped hold-out, cross-system ROC-AUC is largely undefined (`n_dc = 2/12` dual-class withheld systems)
- **Secondary evidence:** repeated-seed stratified cross-validation (100 fold seeds) for in-corpus Family B graph-tally ranking
- **Associational checks:** fold-contained prevalence baseline and Spearman correlation between out-of-fold scores and training-fold system prevalence
- **Exploratory contrast:** nominal pooled-CV versus LOSO Δ with cluster bootstrap by `system_id` (5000 iterations)

The package contains frozen data, analysis scripts, legacy outputs under `results/`, and **strengthened statistics** under `outputs/`. **No LLM inference or oracle re-execution** is required for reproduction.

See [ARTIFACT_MANIFEST.md](ARTIFACT_MANIFEST.md) for manuscript-to-output mapping and [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for exact commands, seeds, and expected outputs.

---

## 2. Dataset description

| Dataset | Location | Description |
|---------|----------|-------------|
| Frozen campaign records | `data/raw/` | Immutable primary inputs: generated FSM serialisations, campaign metadata, oracle labels |
| Master analysis table | `data/processed/master_analysis_dataset.csv` | One row per episode; structural features, gate booleans, behavioural outcomes |
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
├── README.md                    # This file
├── ARTIFACT_MANIFEST.md         # Manuscript table/figure → script/data/output mapping
├── REPRODUCIBILITY.md             # Exact reproduction commands and expected outputs
├── RELEASE_NOTES_v0.3.0.md      # Changes since v0.2.0-submission-candidate
├── RELEASE_READINESS_REPORT.md  # Pre-release audit (Go/No-Go)
├── LICENSE
├── CITATION.cff                   # Update version/DOI at release
├── zenodo.json                    # Update version/DOI at release
├── requirements.txt
├── environment.yml
├── Makefile
├── data/
│   ├── raw/                       # Frozen primary inputs (immutable)
│   └── processed/                 # Analysis-ready tables (immutable after release)
├── scripts/                       # Analysis and reproduction scripts
├── results/                       # Legacy single-seed pipeline outputs
│   ├── tables/
│   └── figures/
├── outputs/                       # Strengthened-stats layer (100 seeds, bootstrap)
│   ├── tables/
│   ├── figures/
│   └── stats/
├── notebooks/                     # Optional exploratory material
└── docs/                          # Data dictionary, legacy reproducibility notes
```

---

## 4. Software requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.11 (recommended; `Makefile` default) |
| numpy | ≥1.24, <3 |
| pandas | ≥2.0, <3 |
| scipy | ≥1.10, <2 |
| scikit-learn | ≥1.3, <2 |
| matplotlib | ≥3.7, <4 |
| seaborn | ≥0.13, <1 (listed in `requirements.txt`; required by `make check-env`) |

**Installation (Conda, recommended):**

```bash
conda env create -f environment.yml
conda activate fsm-behavioural-predictors
make check-env
```

**Installation (pip):**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make check-env
```

No GPU, Ollama, or cloud LLM API access is required.

---

## 5. Replication instructions

### Full legacy pipeline (supporting tables and appendix figures)

```bash
make reproduce          # ~13 s on reference workstation (2026-06-15)
make verify-manuscript  # checks 24 files under results/ and data/
```

Regenerates descriptive profiles, single-seed Families A–D CV, LOSO/LOMO hold-out studies, pre-oracle screen, risk toolkit, and appendix figures under `results/`. Syncs seven legacy PNG/PDF pairs to `../paper/figures/` when invoked via `make figures --sync`.

### Strengthened statistics (primary Results tables and figures)

```bash
make strengthen-stats   # ~3 min 27 s on reference workstation (2026-06-15)
```

Regenerates 34 files under `outputs/` including:

- Definibility audit (`definibility_audit.csv`, `definibility_map.png`)
- Repeated-seed CV summaries (`table5_strengthened.csv`, `cv_seed_distribution_family_b.png`)
- Prevalence association and baseline (`prevalence_correlation.csv`, `prevalence_baseline_comparison.png`)
- Cluster-bootstrap Δ (`table6_strengthened.csv`, `bootstrap_delta_distribution.png`)

Manifest written to `outputs/stats/strengthened_stats_manifest.json`.

### Recommended release verification sequence

```bash
make check-env
make reproduce
make verify-manuscript
make strengthen-stats
# Compare outputs/tables/table5_strengthened.csv and table6_strengthened.csv
# against manuscript Sections 5.1–5.4
```

---

## 6. Manuscript mapping (summary)

| Manuscript section | Primary artefact outputs |
|--------------------|-------------------------|
| §5.1 Definibility audit | `outputs/tables/definibility_audit.csv`, `outputs/figures/definibility_map.png` |
| §5.2 In-corpus ranking | `outputs/tables/table5_strengthened.csv`, `outputs/figures/cv_seed_distribution_family_b.png` |
| §5.3 Prevalence association | `outputs/tables/prevalence_correlation.csv`, `outputs/figures/prevalence_baseline_comparison.png` |
| §5.4 Exploratory CV–LOSO Δ | `outputs/tables/table6_strengthened.csv`, `outputs/figures/bootstrap_delta_distribution.png` |
| §5.5 Supporting / Appendix | `results/tables/`, `results/figures/` (BPR panels, ROC/PR, LOMO, toolkit) |

Full mapping: [ARTIFACT_MANIFEST.md](ARTIFACT_MANIFEST.md). Cross-repo alignment audit: `../paper/paper_notes/MANUSCRIPT_ARTIFACT_ALIGNMENT.md`.

---

## 7. Strengthened analysis description

The strengthened layer (`make strengthen-stats`) implements the protocol cited in the manuscript Results section:

| Parameter | Value | Source |
|-----------|-------|--------|
| CV fold seeds | 0–99 (100 seeds) | `scripts/repro_config.py` → `STRENGTHEN_SEEDS` |
| Classifier | Random forest only | `STRENGTHEN_CLASSIFIER` |
| Bootstrap iterations | 5000 | `N_BOOTSTRAP_ITERATIONS` |
| Bootstrap unit | Cluster resample by `system_id` | `scripts/cluster_bootstrap_delta.py` |
| Legacy single-seed CV | `random_state=42`, 5 folds | `RANDOM_STATE`, `N_SPLITS` |
| RF hyperparameters | 50 trees, max depth 5 | `RF_N_ESTIMATORS`, `RF_MAX_DEPTH` |
| Parallelism | `n_jobs=1` (deterministic) | `SKLEARN_N_JOBS` |

Orchestrator: `scripts/run_strengthened_stats.py`.

---

## 8. Expected runtime

Measured on the author workstation (2026-06-15, Python 3.11):

| Target | Elapsed time | Output location |
|--------|-------------|-----------------|
| `make reproduce` | ~13 s | `results/` (+ sync to `paper/figures/` for legacy figures) |
| `make strengthen-stats` | ~3 min 27 s | `outputs/` (34 files) |
| Combined | ~3 min 40 s | Both trees |

Runtime scales linearly with bootstrap iterations and seed count; no GPU acceleration is used.

---

## 9. What is not included

| Excluded | Reason |
|----------|--------|
| LaTeX manuscript | Private at `~/papers/sqj2026/paper` |
| Live LLM inference | All generation outputs frozen in `data/raw/` |
| Reviewer correspondence | Confidential |
| Credentials / API keys | Never committed (see `.gitignore`) |

---

## 10. Citation

```bibtex
@software{sqj2026_artifact,
  author       = {Andr\'es, C\'esar},
  title        = {Replication Package: Definibility-First Evaluation of Pre-Oracle Ranking for LLM-Generated Finite State Machines},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.20598129},
  url          = {https://github.com/cesar-andress/fsm-behavioural-predictors}
}
```

Machine-readable metadata: [CITATION.cff](CITATION.cff). Update version and DOI when publishing `v0.3.0-revision-candidate`.

---

## 11. License and contact

MIT License — see [LICENSE](LICENSE).

**Corresponding author:** César Andrés — [cesar.andress@ucjc.edu](mailto:cesar.andress@ucjc.edu) — ORCID [0009-0001-8968-3404](https://orcid.org/0009-0001-8968-3404)

**Issue tracker:** [GitHub Issues](https://github.com/cesar-andress/fsm-behavioural-predictors/issues)
