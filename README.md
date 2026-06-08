# Predicting Behavioural Correctness from Structural Signals in LLM-Generated Finite State Machines

**Canonical public artefact repository** for the SQJ 2026 study. This GitHub repository (`cesar-andress/fsm-behavioural-predictors`) is the sole public release target for replication materials and the corresponding **Zenodo** deposit.

**Private manuscript (not in this repository):** the LaTeX sources live outside this tree at `~/papers/sqj2026/paper`. They are not included here and must not be committed to this repository.

This repository accompanies a manuscript submitted to the *Software Quality Journal* (2026) and is intended for **public release on GitHub** and **archival deposit on Zenodo**. It is a self-contained replication package: the released version will contain frozen study data and analysis scripts sufficient to reproduce descriptive and predictive analyses, and to regenerate the tables and figures reported in the paper, **without re-running LLM inference**.

> **Scope note.** This README describes the artefact as it will be released at publication time. Datasets and outputs are not yet finalised; neutral wording is used throughout. No empirical findings are reported here.

## Privacy and scope

This repository is the **public** replication artefact only. The following materials are maintained separately and **must not** appear in this repository, a GitHub release, or a Zenodo deposit:

- The private **LaTeX manuscript** at `~/papers/sqj2026/paper` (sibling directory in the local workspace; not part of this repository).
- **Internal drafts**, working notes, and scratch files produced during writing.
- **Reviewer correspondence**, decision letters, rebuttals, and other peer-review records.

The `.gitignore` file lists patterns that block common leak paths. Before any public release, complete [docs/release_checklist.md](docs/release_checklist.md).

---

## 1. Overview

Large language models (LLMs) are increasingly used to synthesise software artefacts, including finite state machines (FSMs). A central open question is whether the **structural properties** of an LLM-generated FSM relate to its **behavioural correctness** when assessed against an independent oracle.

This artefact will contain the materials needed to audit and reproduce the empirical study underlying the paper *Predicting Behavioural Correctness from Structural Signals in LLM-Generated Finite State Machines*. Specifically, it will provide:

- **Frozen campaign records** documenting each generation episode (specification, model identity, prompt context, and related metadata).
- **Derived structural metrics** computed from the serialised FSM representations.
- **Behavioural outcomes** assigning oracle-based correctness labels to each generated model.
- **Scripts** for reproducing descriptive summaries and predictive analyses reported in the manuscript.

The LaTeX manuscript sources are **private** and are **not** part of this public artefact. Raw private notes, working drafts, and reviewer correspondence are likewise excluded.

---

## 2. Research objective

The study investigates whether structural signals extracted from LLM-generated FSMs can serve as predictors of behavioural correctness.

| Aspect | Description |
|--------|-------------|
| **Independent variable(s)** | Structural metrics of generated FSMs (e.g., graph-theoretic and syntactic properties of the state-transition system). |
| **Dependent variable** | Behavioural correctness as determined by an independent oracle aligned with the originating specification. |
| **Analyses** | Descriptive characterisation of the dataset; predictive models relating structural features to correctness outcomes. |

The artefact supports verification of the study protocol and reproduction of reported tables and figures once the final datasets are deposited. It does **not** presuppose or report final empirical conclusions in this document.

---

## 3. Artefact contents

The released version will contain the following component classes:

| Component | Location (planned) | Role |
|-----------|-------------------|------|
| Frozen campaign records | `data/raw/` | Immutable primary inputs: generated FSM serialisations, campaign metadata, and oracle labels. |
| Processed analysis tables | `data/processed/` | Derived structural metrics and analysis-ready feature matrices. |
| Reproduction scripts | `scripts/` | Command-line tools for descriptive and predictive analyses; table and figure generation. |
| Supplementary notebooks | `notebooks/` | Optional exploratory or supplementary material (not on the critical reproduction path unless stated otherwise). |
| Generated outputs | `results/tables/`, `results/figures/` | Publication-ready tables and figures reproducible from frozen data. |
| Documentation | `docs/` | Data dictionary, reproducibility guide, and structural conventions. |
| Environment specification | `requirements.txt`, `environment.yml` | Pinned dependencies for reproducible execution. |
| Citation metadata | `CITATION.cff`, `zenodo.json` | Machine-readable metadata for GitHub and Zenodo. |

Behavioural outcomes and structural metrics will be distributed as frozen files; the default reproduction workflow reads these files and does **not** invoke external LLM APIs.

---

## 4. Directory structure

```
.
├── README.md                 # This file
├── LICENSE                   # SPDX licence text
├── CITATION.cff              # Machine-readable citation metadata
├── zenodo.json               # Zenodo deposit metadata template
├── requirements.txt          # Python dependencies (pip)
├── environment.yml           # Conda environment specification
├── Makefile                  # Standardised reproduction targets
├── data/
│   ├── raw/                  # Frozen campaign records and primary inputs
│   └── processed/            # Derived structural metrics and analysis tables
├── scripts/                  # Descriptive and predictive analysis scripts
├── notebooks/                # Optional supplementary notebooks
├── results/
│   ├── tables/               # Regenerated paper tables
│   └── figures/              # Regenerated paper figures
└── docs/
    ├── reproducibility.md    # Step-by-step reproduction guide
    ├── data_dictionary.md    # Variable and file semantics
    └── artifact_structure.md # Detailed layout and conventions
```

See [docs/artifact_structure.md](docs/artifact_structure.md) for component-level conventions and the release checklist.

---

## 5. Reproducibility workflow

The artefact is designed so that a reader can reproduce analyses from frozen data alone. **LLM inference does not need to be re-run** at any stage of the published workflow.

### Installation

**Option A — Conda (recommended)**

```bash
conda env create -f environment.yml
conda activate fsm-behavioural-predictors
```

**Option B — pip**

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Verify the environment**

```bash
make check-env
```

### Reproduction steps

1. Clone the repository (or download the Zenodo archive).
2. Create and activate the Python environment as above.
3. Confirm that `data/raw/` and `data/processed/` are present and complete.
4. Run the reproduction targets described in Section 6.
5. Compare outputs under `results/` with those archived at publication time.

For a detailed walkthrough, see [docs/reproducibility.md](docs/reproducibility.md). Variable definitions and file formats are documented in [docs/data_dictionary.md](docs/data_dictionary.md).

### Local execution and LLM inference policy

**Default rule for SQJ 2026:** prefer **frozen existing campaign records**. The published reproduction path (`make reproduce`) does not call cloud APIs and does not require a GPU.

| Priority | Rule |
|----------|------|
| 1 | Use archived campaign outputs in `data/raw/` and derived tables in `data/processed/`. |
| 2 | Do **not** re-run LLM inference unless a specific missing variable cannot be reconstructed from archived artefacts. |
| 3 | If re-execution becomes necessary, it is **out of scope** for the public artefact until privacy and reproducibility checks pass (see [docs/release_checklist.md](docs/release_checklist.md)). |

**Hardware note (authors only):** the study workstation has an **NVIDIA RTX 4090** and **local Ollama / Llama-style inference** is available for optional re-execution during data preparation. That environment is **not** required for readers reproducing tables and figures from frozen data.

Any optional re-execution during study development must be:

- **Local only** — no cloud LLM APIs;
- **Reproducible** — scripted, versioned, and documented;
- **Logged** — per-run logs retained with the campaign export;
- **Temperature 0.0** unless a protocol explicitly documents a different setting;
- **Manifest-linked** — tied to a campaign `manifest.json` (model IDs, prompts, timestamps, checksums).

Optional re-execution scripts must document GPU assumptions (e.g., RTX 4090, Ollama) but must **not** require cloud APIs. Outputs from re-execution remain **excluded from this public repository** until manifest review, privacy review, and reproducibility verification are complete.

---

## 6. How to regenerate tables and figures

From the repository root:

```bash
make reproduce    # regenerate all tables and figures from frozen data
make tables       # tables only
make figures      # figures only
make clean        # remove generated outputs under results/ (preserves data/)
```

| Target | Script | Output directory |
|--------|--------|------------------|
| `make tables` | `scripts/generate_tables.py` | `results/tables/` |
| `make figures` | `scripts/generate_figures.py` | `results/figures/` |

These scripts will read from `data/processed/` (and `data/raw/` where required). They will **not** call LLM APIs or regenerate FSMs from prompts. Descriptive and predictive analyses executed by the scripts will be documented in `docs/reproducibility.md` as they are finalised.

At publication, regenerated outputs should match the tables and figures archived in this repository and cited in the paper. Any intentional deviation will be noted in the release documentation.

---

## 7. Data provenance

| Dataset | Provenance | Mutability after release |
|---------|------------|--------------------------|
| Campaign records | Outputs of a controlled LLM generation campaign over a defined set of specifications; frozen at study completion. | Immutable (`data/raw/`) |
| Structural metrics | Computed offline from frozen FSM serialisations using documented extraction procedures. | Immutable once deposited (`data/processed/`) |
| Behavioural outcomes | Assigned by independent oracles; stored alongside campaign records. | Immutable (`data/raw/` or `data/processed/` as documented) |

The released version will document:

- LLM model identifier(s) and prompt templates used during data collection.
- Oracle construction and labelling protocol.
- Version identifiers and checksums for frozen data files.
- The date on which data were frozen for publication.

Full column-level definitions will appear in [docs/data_dictionary.md](docs/data_dictionary.md) prior to Zenodo deposit.

---

## 8. What is not included

The following materials are **deliberately excluded** from this public artefact:

| Excluded material | Reason |
|-------------------|--------|
| LaTeX manuscript sources | Maintained privately at `~/papers/sqj2026/paper`; not part of this repository. |
| Live LLM inference | All generation outputs are frozen; reproduction does not require API keys, cloud APIs, or model re-execution. Optional local Ollama re-runs (RTX 4090) are author-only and excluded until release checks pass. |
| Raw private notes and working drafts | Internal research records with no replication value. |
| Reviewer correspondence and submission metadata | Confidential peer-review materials. |
| Credentials, API keys, or environment secrets | Must never be committed; see `.gitignore`. |

If supplementary material beyond this package is required, it will be referenced explicitly in the paper and linked from the Zenodo record.

---

## 9. Citation

If you use this artefact, please cite both the journal article (when available) and the Zenodo deposit:

```bibtex
@software{sqj2026_artifact,
  author       = {Andr\'es, C.},
  title        = {Replication Package: Predicting Behavioural Correctness from Structural Signals in LLM-Generated Finite State Machines},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.PLACEHOLDER},
  url          = {https://github.com/cesar-andress/fsm-behavioural-predictors}
}
```

A machine-readable citation file is provided in [CITATION.cff](CITATION.cff). Author metadata is maintained centrally; update DOIs before the Zenodo deposit.

---

## 10. License

This artefact is released under the [MIT License](LICENSE). See the `LICENSE` file for the full text.

Individual data files may carry additional terms if required by upstream sources; any such restrictions will be stated in [docs/data_dictionary.md](docs/data_dictionary.md) at release time.

---

## 11. Contact

For questions about this replication package:

- **Corresponding author:** César Andrés — [cesar.andress@ucjc.edu](mailto:cesar.andress@ucjc.edu) — ORCID [0009-0001-8968-3404](https://orcid.org/0009-0001-8968-3404)
- **Issue tracker:** [GitHub Issues](https://github.com/cesar-andress/fsm-behavioural-predictors/issues)
- **Zenodo record:** [10.5281/zenodo.PLACEHOLDER](https://doi.org/10.5281/zenodo.PLACEHOLDER)

For manuscript-related enquiries, refer to the *Software Quality Journal* submission.
