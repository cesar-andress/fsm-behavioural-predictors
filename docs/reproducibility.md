# Reproducibility Guide

This document describes how to reproduce all tables and figures reported in the paper *Predicting Behavioural Correctness from Structural Signals in LLM-Generated Finite State Machines* using only the frozen data in this repository.

## Obtaining the artefact

| Source | Identifier |
|--------|------------|
| Zenodo (recommended for citation) | [10.5281/zenodo.20598129](https://doi.org/10.5281/zenodo.20598129) |
| GitHub (tag `v0.1.0-pre-submission`) | https://github.com/cesar-andress/fsm-behavioural-predictors |

Archive metadata and citation text: [zenodo_record.md](zenodo_record.md).

## Design principle

**No LLM inference is required.** The replication pipeline reads pre-computed inputs from `data/raw/` and `data/processed/` and writes outputs to `results/`. This ensures that reviewers and readers can verify reported findings without API keys, cloud APIs, GPU resources, or non-deterministic model calls.

## Local execution constraint

SQJ 2026 follows a **frozen-data-first** policy:

1. **Prefer frozen existing campaign records** in `data/raw/` and `data/processed/`.
2. **Do not re-run LLM inference** unless a specific missing variable cannot be reconstructed from archived artefacts (e.g., derived structural counts from frozen `candidates/*.json` rather than new generation).
3. **If re-execution becomes necessary** (author workflow only, not the published `make reproduce` path), it must be:
   - **local only** — Ollama or equivalent on the author workstation; **no cloud LLM APIs**;
   - **reproducible** — scripted entry points, pinned model identifiers, documented prompts;
   - **logged** — per-run logs stored alongside campaign exports;
   - **temperature 0.0** unless the study protocol explicitly documents a different setting;
   - **manifest-linked** — recorded in a campaign `manifest.json` with model IDs, config hashes, timestamps, and file checksums;
   - **excluded from the public artefact** until privacy and reproducibility checks in [release_checklist.md](release_checklist.md) pass.

### Hardware note (authors)

The author workstation has an **NVIDIA RTX 4090** and can run **local Ollama / Llama-style models**. Optional re-execution scripts may document GPU assumptions for transparency, but:

- the **published reproduction path does not require a GPU**;
- readers reproducing from Zenodo/GitHub archives should not need Ollama installed;
- no re-execution script in this repository may **require** cloud APIs.

## Prerequisites

1. Clone this repository.
2. Create the Python environment (Conda or pip; see root `README.md`).
3. Confirm dependencies: `make check-env`

No Ollama installation, CUDA toolkit, or network access to LLM endpoints is required for `make reproduce`.

## Random seeds and CV protocol

All predictive scripts share constants in `scripts/repro_config.py`:

| Parameter | Value | Used by |
|-----------|-------|---------|
| `RANDOM_STATE` | `42` | `StratifiedKFold`, logistic regression, decision tree, random forest, stratified dummy |
| `N_SPLITS` | `5` | Stratified five-fold CV |
| `SKLEARN_N_JOBS` | `1` | `cross_val_predict`, random forest (`n_jobs`) — single-threaded for stable outputs |
| `RF_N_ESTIMATORS` / `RF_MAX_DEPTH` | `50` / `5` | Random forest (fixed; no tuning) |
| `DT_MAX_DEPTH` | `3` | Decision tree |
| `LR_MAX_ITER` | `2000` | Logistic regression |

Predictive entry points call `apply_reproducibility()` (`np.random.seed(42)`) before fitting.

Bootstrap resampling is **not** used; fold-wise means and standard deviations report uncertainty. This matches the manuscript threats discussion.

Grouped hold-out scripts (LOSO/LOMO) use deterministic fold order (`sorted` held-out groups) and inherit `random_state=42` from `make_model()`; they do not reshuffle rows.

## One-command reproduction

```bash
make reproduce
```

This executes, in order (no LLM inference at any step):

1. `scripts/build_master_dataset.py` → `data/processed/master_analysis_dataset.csv`
2. `scripts/generate_tables.py` → descriptive `profile_*.csv` tables
3. `scripts/profile_predictive_signals.py` → target/signal profiling tables and BPR boxplot figures
4. `scripts/model_behavioural_correctness.py` → Families A–D CV tables and ROC/PR figures
5. `scripts/loso_system_evaluation.py` → LOSO tables and heatmap
6. `scripts/pre_oracle_prediction.py` → strict-allowlist tables and supplementary ROC/PR figures
7. `scripts/lomo_model_evaluation.py` → LOMO tables and heatmap
8. `scripts/risk_toolkit.py` → BRS triage audit tables
9. `scripts/generate_figures.py` → verifies all manuscript-linked figures exist
10. `scripts/verify_manuscript_outputs.py` → cross-checks paths in Appendix Table artifact-outputs

Verify outputs only (after a successful `make reproduce`):

```bash
make verify-manuscript
```

Manuscript anchor mapping: [manuscript_outputs.md](manuscript_outputs.md).

## Step-by-step reproduction

### Tables

```bash
make tables
# equivalent to:
python scripts/generate_tables.py
```

Expected outputs (to be defined when analyses are finalised) will be listed in `docs/data_dictionary.md`.

### Predictive-signal profiling

```bash
make profile-signals
# equivalent to:
python scripts/build_master_dataset.py
python scripts/profile_predictive_signals.py
```

Writes:

- `results/tables/target_distribution.md`
- `results/tables/descriptive_profile.md`
- `results/tables/predictive_signal_profile.md`
- `results/tables/profile_signals_validation.md`
- `results/figures/bpr_by_gate.png`, `bpr_by_model.png`, `bpr_by_system.png`

Associations are descriptive only (no hypothesis tests, no ML models).

### Exploratory predictive modelling

```bash
make model-correctness
# equivalent to:
python scripts/build_master_dataset.py
python scripts/model_behavioural_correctness.py
```

Writes `model_performance.md`, `model_feature_importance.md`, `model_validation.md`, and ROC/PR curve figures. Stratified 5-fold CV on behaviourally scored runs; not confirmatory.

### Leave-one-system-out generalization

```bash
make loso-systems
# requires model_performance.md from make model-correctness
```

Trains on 11 `system_id` values, tests on the held-out system (12 folds). Writes `loso_system_results.md`, `loso_system_summary.md`, and `loso_system_heatmap.png`, with explicit comparison to random CV.

### Pre-oracle prediction

```bash
make pre-oracle
# requires model_performance.md from make model-correctness
```

Strict feature allowlist (gates, requirement coverage, basic FSM counts only). Writes `pre_oracle_model_performance.md`, `pre_oracle_feature_importance.md`, and ROC/PR figures; compares against `A_gate_only` and `B_basic_structural` from random CV.

### Leave-one-model-out generalization

```bash
make lomo-models
# requires model_performance.md from make model-correctness
```

Trains on three LLM families, tests on the held-out fourth (`model` grouping). Writes `lomo_results.md`, `lomo_summary.md`, and `lomo_heatmap.png`, with comparison to random CV.

### Behavioural risk toolkit

```bash
make risk-toolkit
```

Pre-oracle triage implementation: Behavioural Risk Score (BRS), AutoReject decisions, and FSM health reports. See [risk_toolkit.md](risk_toolkit.md). Writes `risk_toolkit_predictions.csv`, `risk_toolkit_validation.md`, and `risk_toolkit_examples.md`.

### Figures

```bash
make figures
# equivalent to:
python scripts/generate_figures.py
```

Figure files are written to `results/figures/` in formats suitable for inclusion in the manuscript (e.g., PDF, PNG).

## Frozen data policy

| Stage | Location | Mutability |
|-------|----------|------------|
| Raw inputs | `data/raw/` | Immutable after publication |
| Processed features | `data/processed/` | Immutable after publication |
| Generated results | `results/` | Regenerated by scripts; should match published outputs |

If regenerated outputs differ from those archived at publication time, document the cause (e.g., dependency version drift) in the release notes.

Re-execution outputs from local Ollama campaigns are **not** merged into `data/raw/` until a new freeze is explicitly documented and checked.

## Master dataset provenance

The canonical analysis table `data/processed/master_analysis_dataset.csv` is built by `scripts/build_master_dataset.py` from the following **frozen** inputs (no LLM inference):

| Artefact | Path in this repository | Upstream origin |
|----------|-------------------------|-----------------|
| Combined per-run metrics | `data/raw/metrics_combined.csv` | EMSE 2026 paper campaign ingest (C1+C2; 240 runs) |
| Parsed FSM serialisations | `data/raw/candidates/{run_id}.json` | `C1_pilot_ollama_behavioral/20260603T003118Z/candidates/` and `C2_core_ollama_behavioral/20260603T080817Z/candidates/` |
| Oracle evaluation records | `data/raw/evaluations/{run_id}.json` | Matching `evaluations/` directories from the same C1/C2 freezes |
| Provenance metadata | `data/raw/frozen_campaign_manifest.json` | Authored at SQJ ingest |

**Build command:**

```bash
python scripts/build_master_dataset.py
```

Validation output is written to `results/tables/master_dataset_validation.md`.

## Computational requirements

| Path | Hardware | Typical runtime |
|------|----------|-----------------|
| `make reproduce` (published) | Standard CPU laptop; no GPU | Minutes (once datasets are deposited) |
| Optional author re-execution (not published) | NVIDIA RTX 4090 + local Ollama | Campaign-dependent; logged separately |

Exact runtime for the frozen-data path will be reported once datasets and scripts are finalised.

## Troubleshooting

| Issue | Suggested action |
|-------|------------------|
| Import errors | Re-create the environment from `environment.yml` or `requirements.txt` |
| Missing data files | Ensure `data/raw/` and `data/processed/` are fully checked out; see `.gitignore` for large-file notes |
| Output mismatch | Compare package versions with those recorded in `environment.yml`; compare against the archived Zenodo release ([10.5281/zenodo.20598129](https://doi.org/10.5281/zenodo.20598129)) |
| Temptation to re-run Ollama | Reconstruct missing columns from archived `candidates/` or `evaluations/` JSON first; see data audit notes in the private study workspace |

## Contact

Open an issue in the public repository or contact the corresponding author (see root `README.md`).
