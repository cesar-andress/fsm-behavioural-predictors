# Reproducibility guide

Exact commands, environment assumptions, random seeds, and expected outputs for reproducing all manuscript tables and figures from frozen data.

**Design principle:** no LLM inference, no oracle re-execution, no cloud APIs.

---

## 1. Obtain the artefact

```bash
git clone https://github.com/cesar-andress/fsm-behavioural-predictors.git
cd fsm-behavioural-predictors
git checkout v0.3.0-revision-candidate   # after tag is published
```

Or download the Zenodo archive for the matching version DOI.

---

## 2. Environment

### Prerequisites

- Python **3.11** (Makefile default: `PYTHON ?= python3.11`)
- ~500 MB disk for repository; ~15 MB additional for regenerated `outputs/stats/` intermediates

### Install and verify

```bash
conda env create -f environment.yml
conda activate fsm-behavioural-predictors
make check-env
```

Expected output:

```
Environment OK
```

**Note:** `make check-env` imports `seaborn` (listed in `requirements.txt`). Analysis scripts use `matplotlib` only; seaborn is an environment gate, not a runtime dependency of the pipelines.

### Environment assumptions

| Assumption | Value |
|------------|-------|
| OS tested | Linux (Ubuntu 6.8) |
| BLAS | System default (NumPy/sklearn) |
| Threading | `SKLEARN_N_JOBS=1` — single-threaded fits for cross-platform stability |
| Floating point | IEEE-754 double; minor platform drift possible beyond reported rounding |

---

## 3. One-command reproduction

### 3.1 Legacy pipeline (`results/`)

```bash
make reproduce
make verify-manuscript
```

**Expected terminal output (verify):**

```
Manuscript output verification OK (24 files across 9 anchors)
Zenodo DOI: https://doi.org/10.5281/zenodo.20598129
Reproduction complete. Outputs in results/
```

**Elapsed time (reference workstation, 2026-06-15):** ~13 s.

**Pipeline order:**

1. `scripts/build_master_dataset.py` → `data/processed/master_analysis_dataset.csv`
2. `scripts/generate_tables.py` → `results/tables/profile_*.csv`, descriptive MD
3. `scripts/profile_predictive_signals.py` → `predictive_signal_profile.md`, `bpr_by_*.png`
4. `scripts/model_behavioural_correctness.py` → Families A–D CV, ROC/PR figures
5. `scripts/loso_system_evaluation.py` → LOSO tables and heatmap
6. `scripts/pre_oracle_prediction.py` → pre-oracle tables and supplementary ROC/PR
7. `scripts/lomo_model_evaluation.py` → LOMO tables and heatmap
8. `scripts/risk_toolkit.py` → toolkit validation tables
9. `scripts/generate_figures.py --sync` → copies legacy figures to `../paper/figures/`
10. `scripts/verify_manuscript_outputs.py` → path existence check

### 3.2 Strengthened statistics (`outputs/`)

```bash
make strengthen-stats
```

**Expected terminal output (final lines):**

```
=== Strengthened figures ===
Wrote .../outputs/figures/definibility_map.png
Wrote .../outputs/figures/bootstrap_delta_distribution.png
Wrote .../outputs/figures/cv_seed_distribution_family_b.png
Wrote .../outputs/figures/prevalence_baseline_comparison.png

Wrote .../outputs/stats/strengthened_stats_manifest.json
Generated 34 output files.
```

**Elapsed time (reference workstation, 2026-06-15):** ~3 min 27 s.

---

## 4. Random seeds and protocol constants

All constants: `scripts/repro_config.py`.

### Legacy single-seed CV (`results/`)

| Parameter | Value |
|-----------|-------|
| `RANDOM_STATE` | `42` |
| `N_SPLITS` | `5` (stratified) |
| `RF_N_ESTIMATORS` | `50` |
| `RF_MAX_DEPTH` | `5` |
| `DT_MAX_DEPTH` | `3` |
| `LR_MAX_ITER` | `2000` |
| `SKLEARN_N_JOBS` | `1` |

`apply_reproducibility()` sets `np.random.seed(42)` before stochastic steps.

LOSO/LOMO scripts use deterministic fold order (`sorted` hold-out groups) with the same model defaults.

### Strengthened-stats layer (`outputs/`)

| Parameter | Value |
|-----------|-------|
| `STRENGTHEN_SEEDS` | `list(range(100))` → seeds **0–99** |
| `N_BOOTSTRAP_ITERATIONS` | **5000** |
| `STRENGTHEN_CLASSIFIER` | `random_forest` (RF-only for primary tables) |
| CV protocol | Stratified 5-fold; fold-contained preprocessing per seed |
| Bootstrap unit | Cluster resample episodes by `system_id` |
| LOSO μ | Mean of definable per-system fold AUCs (`skipna`; `n_dc=2/12`) |
| CV summary | Distribution across 100 seeds of pooled out-of-fold ROC-AUC |
| Interval notation | Seed-wise or bootstrap 2.5–97.5% percentiles |

---

## 5. Expected numerical outputs (manuscript alignment)

After `make strengthen-stats`, these values must match the manuscript (rounded to three decimals in prose):

### Definibility audit (`outputs/tables/definibility_audit.csv`)

| Quantity | Expected |
|----------|----------|
| Dual-class systems | `hotel_booking`, `login_system` only |
| `n_dc` | 2 / 12 |
| Family B RF LOSO AUC | 0.500, 0.667 (mean 0.583) |

### Table 5.2 — in-corpus ranking (`outputs/tables/table5_strengthened.csv`)

| Row | ROC-AUC [2.5–97.5%] |
|-----|---------------------|
| Family A gates (RF) | 0.614 [0.599, 0.629] |
| Family B graph tallies (RF) | **0.981 [0.976, 0.985]** |
| Family C ref-diff (RF) | 1.000 [1.000, 1.000] |
| Family D combined (RF) | 1.000 [1.000, 1.000] |
| Stratified dummy (A) | 0.505 [0.430, 0.596] |

### Prevalence association (`outputs/tables/prevalence_correlation.csv`, `table5_strengthened.csv`)

| Quantity | Expected [2.5–97.5%] |
|----------|----------------------|
| Spearman ρ (OOF vs training-fold prevalence) | 0.584 [0.534, 0.629] |
| Prevalence-only baseline ROC-AUC | 0.958 [0.951, 0.964] |
| Family B graph-tally ROC-AUC | 0.981 [0.976, 0.985] |

### Table 5.4 — CV–LOSO contrast (`outputs/tables/table6_strengthened.csv`)

| Family (RF) | CV AUC | LOSO μ | Δ | Bootstrap Δ [2.5–97.5%] |
|-------------|--------|--------|---|-------------------------|
| A (gates) | 0.614 [0.599, 0.629] | 0.833 | −0.219 | [−0.193, 0.276] |
| B (graph) | 0.981 [0.976, 0.985] | 0.583 | 0.397 | **[−0.026, 0.772]** |
| C (ref-diff) | 1.000 | 1.000 | 0.000 | [0.000, 0.000] |
| D (combined) | 1.000 | 1.000 | 0.000 | [−0.000, 0.036] |

Bootstrap definability rates (~97%): see `delta_bootstrap_definability_rate` column (resamples where ≥1 dual-class LOSO fold exists).

### Legacy cohort counts (`results/tables/target_distribution.md`)

| Metric | Expected |
|--------|----------|
| Total episodes | 240 |
| Oracle-scored | 209 (87.1%) |
| Full behavioural pass (scored) | 30 (14.4%) |

---

## 6. Quick verification commands

```bash
# Legacy path check
make verify-manuscript

# Strengthened key metrics (Family B)
python3.11 - <<'PY'
import pandas as pd
t5 = pd.read_csv("outputs/tables/table5_strengthened.csv")
t6 = pd.read_csv("outputs/tables/table6_strengthened.csv")
b = t5[t5["predictor_family"].str.contains("Family B")]
print("Family B CV:", b["roc_auc_interval"].values[0])
row = t6[t6["predictor_family"].str.contains("Family B")]
print("Family B Δ boot:", row["delta_bootstrap_interval"].values[0])
PY

# Manifest file count
python3.11 -c "import json; m=json.load(open('outputs/stats/strengthened_stats_manifest.json')); print(len(m['output_files']), 'files')"
```

Expected manifest count: **34** files.

---

## 7. Manuscript figure sync

Strengthened figures (`outputs/figures/`) are **not** auto-synced by `make reproduce`. For a full PDF rebuild of the private manuscript:

1. Run `make strengthen-stats`
2. Copy strengthened PNG/PDF to `../paper/figures/`:
   - `definibility_map`
   - `cv_seed_distribution_family_b`
   - `prevalence_baseline_comparison`
   - `bootstrap_delta_distribution`
3. Run `make reproduce` (syncs legacy appendix figures)
4. From `../paper/`: `make verify`

---

## 8. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: seaborn` on `make check-env` | Environment not installed | `pip install -r requirements.txt` or use Conda env |
| `verify-manuscript` fails | Missing `results/` outputs | `make reproduce` |
| Strengthened numbers differ | Wrong seed list or edited `master_analysis_dataset.csv` | Restore frozen data; rerun `make strengthen-stats` |
| Figure missing in paper PDF | Strengthened figures not copied to `paper/figures/` | Manual copy (Section 7) |

---

## 9. Related documentation

| Document | Role |
|----------|------|
| [ARTIFACT_MANIFEST.md](ARTIFACT_MANIFEST.md) | Manuscript ID → script → file mapping |
| [README.md](README.md) | Project overview and installation |
| [docs/data_dictionary.md](docs/data_dictionary.md) | Column semantics |
| [docs/reproducibility.md](docs/reproducibility.md) | Legacy guide (pre–strengthen-stats; superseded by this file for v0.3.0) |

---

## 10. Audit record

| Field | Value |
|-------|-------|
| Audit date | 2026-06-15 |
| Git commit (strengthened manifest) | `d3a1d29235d2823081188acbf20e81325eb1b262` |
| `make reproduce` | PASS (~13 s) |
| `make verify-manuscript` | PASS (24 files) |
| `make strengthen-stats` | PASS (~3 min 27 s, 34 outputs) |
| Manuscript `make verify` | PASS (28 pages, VERIFY OK) |
