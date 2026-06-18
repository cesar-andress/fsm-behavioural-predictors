# Reproducibility guide — RAP-AQ EMSE submission freeze

Exact commands, environment assumptions, random seeds, and expected outputs for reproducing the EMSE manuscript tables and figures from frozen data.

**Design principle:** no LLM inference, no oracle re-execution, no cloud APIs.

**Zenodo DOI:** [10.5281/zenodo.20738203](https://doi.org/10.5281/zenodo.20738203)

---

## 1. Obtain the artefact

```bash
git clone https://github.com/cesar-andress/fsm-behavioural-predictors.git
cd fsm-behavioural-predictors
git checkout v1.0.0-submission
```

Or download the Zenodo archive for [10.5281/zenodo.20738203](https://doi.org/10.5281/zenodo.20738203).

---

## 2. Environment

```bash
conda env create -f environment.yml
conda activate fsm-behavioural-predictors
make check-env
```

Expected: `Environment OK`

---

## 3. One-command reproduction (primary)

```bash
make reproduce
```

**Pipeline order:**

1. `build_master_dataset.py` → `data/processed/master_analysis_dataset.csv`
2. `run_strengthened_stats.py` → definibility audit, fixed audit predictor contract, prevalence baseline, optional CV–LOSO contrast
3. `grouped_auc_decomposition.py`, `grouped_auc_bootstrap.py`, `simulate_grouped_reportability.py` → pair-partition diagnostics and simulation
4. `verify_submission_outputs.py` → path existence check (18 primary files)

**Expected terminal output:**

```
RAP-AQ submission output verification OK (18 files across 4 anchors)
Zenodo DOI: https://doi.org/10.5281/zenodo.20738203
RAP-AQ reproduction complete. Primary outputs in outputs/
```

**Elapsed time (reference workstation):** ~3–4 min.

---

## 4. Legacy deposit-only pipeline

```bash
make legacy-reproduce
make verify-manuscript
```

Regenerates Families A–D CV, LOMO, and appendix figures under `results/`. Not cited in the RAP-AQ manuscript body. See [docs/legacy_deposit.md](docs/legacy_deposit.md).

---

## 5. Random seeds and protocol constants

All constants: `scripts/repro_config.py`.

| Parameter | Value |
|-----------|-------|
| `STRENGTHEN_SEEDS` | 0–99 (100 seeds) |
| `N_BOOTSTRAP_ITERATIONS` | 5000 |
| `STRENGTHEN_CLASSIFIER` | `random_forest` |
| Bootstrap unit | Cluster resample by `system_id` |

---

## 6. Expected numerical outputs

After `make reproduce`, key quantities in `outputs/tables/` must match the manuscript (three decimal places in prose):

| Output | Quantity | Expected |
|--------|----------|----------|
| `definability_audit.csv` | Dual-class systems | `hotel_booking`, `login_system` (`n_dc = 2/12`) |
| `table5_strengthened.csv` | Fixed audit predictor contract (RF) | 0.981 [0.976, 0.985] |
| `table5_strengthened.csv` | Prevalence-only baseline | 0.958 [0.951, 0.964] |
| `prevalence_correlation.csv` | Spearman ρ | 0.584 [0.534, 0.629] |
| `table6_strengthened.csv` | Δ bootstrap (contract B) | [−0.026, 0.772] |

---

## 7. Quick verification

```bash
make verify-submission
```

---

## 8. Related documentation

| Document | Role |
|----------|------|
| [ARTIFACT_MANIFEST.md](ARTIFACT_MANIFEST.md) | Manuscript → script → file mapping |
| [README.md](README.md) | Overview and installation |
| [docs/zenodo_record.md](docs/zenodo_record.md) | DOI and citation |
| [RELEASE_NOTES_v1.0.0-submission.md](RELEASE_NOTES_v1.0.0-submission.md) | Release description |

---

## 9. Scope limits

This release freezes the submission artefact. **No post-submission analyses are included.**
