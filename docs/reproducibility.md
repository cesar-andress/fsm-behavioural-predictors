# Reproducibility Guide

This document describes how to reproduce all tables and figures reported in the paper *Predicting Behavioural Correctness from Structural Signals in LLM-Generated Finite State Machines* using only the frozen data in this repository.

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

## One-command reproduction

```bash
make reproduce
```

This executes, in order:

1. `scripts/generate_tables.py` → `results/tables/`
2. `scripts/generate_figures.py` → `results/figures/`

Neither script invokes LLM inference.

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
| Output mismatch | Compare package versions with those recorded in `environment.yml`; pin exact versions before Zenodo deposit |
| Temptation to re-run Ollama | Reconstruct missing columns from archived `candidates/` or `evaluations/` JSON first; see data audit notes in the private study workspace |

## Contact

Open an issue in the public repository or contact the corresponding author (see root `README.md`).
