# Data Dictionary

This document defines files, variables, and semantics for datasets in the SQJ 2026 replication package.

**Status:** Placeholder structure. Entries will be completed when datasets are frozen for publication.

## Directory overview

### `data/raw/`

Immutable source data collected during the study. No script in this repository modifies files in this directory.

| File / pattern | Description | Format | Notes |
|----------------|-------------|--------|-------|
| *(to be added)* | LLM-generated FSM serialisations | TBD | One record per generated model |
| *(to be added)* | Oracle correctness labels | TBD | Independent behavioural assessment |
| *(to be added)* | Study metadata | TBD | Model ID, prompt template, timestamp, etc. |

### `data/processed/`

Derived datasets produced by preprocessing scripts (run once before freezing; not part of the default `make reproduce` path unless documented otherwise).

| File / pattern | Description | Format | Notes |
|----------------|-------------|--------|-------|
| *(to be added)* | Structural feature matrix | TBD | Features used in predictive analyses |
| *(to be added)* | Train/test partition index | TBD | Ensures reproducible evaluation splits |

## Variable definitions

### Identifier variables

| Variable | Type | Description |
|----------|------|-------------|
| `model_id` | string | Unique identifier for each generated FSM |
| `spec_id` | string | Identifier of the originating specification |

### Outcome variables

| Variable | Type | Description |
|----------|------|-------------|
| `behaviourally_correct` | boolean | Oracle verdict: model satisfies intended behaviour |
| `oracle_notes` | string (optional) | Qualitative notes from oracle assessment |

### Structural feature variables

| Variable | Type | Description |
|----------|------|-------------|
| `n_states` | integer | Number of states in the FSM |
| `n_transitions` | integer | Number of transitions |
| *(additional features)* | TBD | To be defined in the methodology section of the paper |

## Provenance

- **Collection period:** TBD
- **LLM(s) used:** TBD (inference outputs frozen in `data/raw/`; not re-run during replication)
- **Oracle construction:** TBD

## Licence and redistribution

Data files inherit the repository licence (MIT) unless otherwise noted. Update this section if any subset carries additional restrictions.
