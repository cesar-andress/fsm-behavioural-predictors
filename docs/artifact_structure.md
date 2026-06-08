# Artefact Structure

Conventions and layout for the SQJ 2026 public replication package.

## Top-level files

| File | Purpose |
|------|---------|
| `README.md` | Entry point: overview, installation, reproduction, citation |
| `LICENSE` | SPDX licence text (MIT) |
| `CITATION.cff` | Citation metadata for software archives and reference managers |
| `zenodo.json` | Metadata for Zenodo deposit (archived as 10.5281/zenodo.20598129) |
| `requirements.txt` | pip dependency specification |
| `environment.yml` | Conda environment specification |
| `Makefile` | Standardised reproduction commands |
| `.gitignore` | Excludes build artefacts, secrets, and optional large files |

## `data/`

| Subdirectory | Role | Modified by `make reproduce`? |
|--------------|------|-------------------------------|
| `data/raw/` | Frozen primary inputs | No |
| `data/processed/` | Analysis-ready derived tables | No |

Raw data is never overwritten by reproduction scripts. Preprocessing that produces `data/processed/` is documented separately and run only when building the frozen release.

## `scripts/`

Command-line Python modules invoked by the `Makefile`:

| Script | Output |
|--------|--------|
| `repro_config.py` | Shared `RANDOM_STATE=42`, CV splits, model defaults |
| `build_master_dataset.py` | `data/processed/master_analysis_dataset.csv` |
| `generate_tables.py` | Descriptive `profile_*.csv` under `results/tables/` |
| `profile_predictive_signals.py` | Target/signal profiling tables and BPR figures |
| `model_behavioural_correctness.py` | Families A–D CV tables and ROC/PR figures |
| `loso_system_evaluation.py` | LOSO tables and heatmap |
| `pre_oracle_prediction.py` | Strict-allowlist tables and supplementary figures |
| `lomo_model_evaluation.py` | LOMO tables and heatmap |
| `risk_toolkit.py` | BRS triage audit tables |
| `generate_figures.py` | Verifies manuscript-linked figures exist |
| `verify_manuscript_outputs.py` | Cross-checks Appendix mapping paths |

`make reproduce` runs the full chain above. Scripts must not require live LLM API access.

## `notebooks/`

Optional Jupyter notebooks for exploratory analysis or supplementary material. Notebooks are **not** on the critical path for `make reproduce` unless explicitly documented.

## `results/`

| Subdirectory | Contents |
|--------------|----------|
| `results/tables/` | CSV, LaTeX, or other table formats matching the paper |
| `results/figures/` | Publication-ready figure files |

Generated outputs may be committed at release time so that `make reproduce` can be verified against known baselines.

## `docs/`

| Document | Contents |
|----------|----------|
| `reproducibility.md` | Step-by-step reproduction instructions |
| `zenodo_record.md` | Zenodo DOI, citation, release metadata, and reproducibility scope |
| `data_dictionary.md` | File and variable definitions |
| `artifact_structure.md` | This file |

## Separation from the private manuscript

The LaTeX manuscript lives privately at `~/papers/sqj2026/paper` (not part of this public repository). This artefact does not depend on the manuscript tree; authors copy outputs from `results/` as needed when preparing the paper.

## Release checklist

Before GitHub/Zenodo release, complete [release_checklist.md](release_checklist.md).
