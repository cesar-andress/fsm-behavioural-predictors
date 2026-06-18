# Release Checklist

> **Superseded** by [RELEASE_CHECKLIST_v1.0.0-submission.md](../RELEASE_CHECKLIST_v1.0.0-submission.md).

Complete this checklist before publishing the artefact on **GitHub** or depositing it on **Zenodo**. Each item must be verified by a project author.

## Zenodo deposit (v1.0.0-submission)

- [x] **Zenodo record published** — [10.5281/zenodo.20738203](https://doi.org/10.5281/zenodo.20738203).
- [x] **zenodo_record.md created** — DOI, citation, version, and reproducibility scope documented.
- [x] **CITATION.cff updated** — Zenodo DOI, release date, and version match the published record.
- [x] **zenodo.json updated** — creators, version, publication date, and related identifiers align with the deposit.
- [x] **README updated** — Zenodo DOI and data/code availability statements in place.

Future releases should repeat the documentation and metadata checks below before publishing a new Zenodo version.

## Privacy and scope

- [ ] **No private manuscript files** — no `.tex`, `main.pdf`, `sections/`, or other LaTeX sources from `paper/`.
- [ ] **No local bibliography copies** — no `references.bib`, `refs.bib`, or copies of `~/papers/bibliography.bib` in the artefact.
- [ ] **No reviewer correspondence** — no reviews, rebuttals, decision letters, or submission metadata.
- [ ] **No API keys or local paths** — no credentials, `.env` files, tokens, or machine-specific absolute paths in code, configs, or notebooks.

## Reproducibility

- [x] **All scripts run from frozen data** — `make reproduce` completes without LLM API calls or network access to generation endpoints (verified 2026-06-08).
- [ ] **Risk toolkit tested** — `make risk-toolkit` completes; `risk_toolkit_validation.md` matches published triage audit.
- [x] **Reproducibility command tested** — `make check-env`, `make reproduce`, and `make verify-submission` run cleanly.
- [x] Regenerated outputs under `results/` match the tables and figures cited in the paper (`docs/manuscript_outputs.md`; `make verify-manuscript`).

## LLM inference and local execution

- [ ] **Frozen campaign records preferred** — `data/raw/` and `data/processed/` are complete; missing variables were reconstructed from archived artefacts where possible before any re-execution.
- [ ] **No cloud LLM APIs** — published artefact and reproduction scripts do not call remote inference endpoints.
- [ ] **No unpublished re-execution in public tree** — any local Ollama re-runs (RTX 4090 workstation) are excluded until this checklist passes.
- [ ] **Re-execution policy** (if any re-run occurred during study development):
  - [ ] local only (Ollama / Llama-style on author machine);
  - [ ] temperature **0.0** unless protocol documents otherwise;
  - [ ] per-run logs retained;
  - [ ] campaign tied to `manifest.json` (models, prompts, timestamps, checksums);
  - [ ] GPU assumptions documented (e.g., NVIDIA RTX 4090) but not required for `make reproduce`;
  - [ ] privacy and reproducibility review completed before deposit.
- [ ] **Optional re-execution scripts** (if present) document that cloud APIs are not required and are off the critical `make reproduce` path.

## Documentation and metadata

- [ ] **Author metadata compliant** — names, affiliations, email, and ORCID match `~/papers/promts/author_identity_standardization.md`; no invented or duplicate author copies in project files.
- [ ] **Editorial final pass** — `~/papers/promts/editorial_final_pass.md` checklist completed for the manuscript.
- [x] **README updated** — Zenodo DOI and availability statements in place; [Privacy and scope](../README.md#privacy-and-scope) section accurate; contact matches central author identity.
- [x] **CITATION.cff updated** — authors, title, version, date, and Zenodo DOI match the published record.
- [x] **zenodo.json updated** — creators, keywords, related identifiers, and licence align with the Zenodo deposit.
- [ ] **License confirmed** — `LICENSE` file present; `MIT` (or chosen licence) consistent across README, `CITATION.cff`, and `zenodo.json`.
- [ ] [data_dictionary.md](data_dictionary.md) complete for all files in `data/raw/` and `data/processed/`.

## Repository hygiene

- [ ] `.gitignore` covers manuscript drafts, LaTeX aux files, private notes, credentials, and cache directories.
- [ ] No `README_PRIVATE.md`, `paper/`, `drafts/`, or `notes/` directories in the repository tree.
- [ ] Dependency versions pinned in `requirements.txt` and `environment.yml`.
- [ ] Large or sensitive files handled via Git LFS or external archives as documented (if applicable).

## Sign-off

| Role | Name | Date |
|------|------|------|
| Corresponding author | | |
| Artefact maintainer | | |
