# Release Checklist

Complete this checklist before publishing the artefact on **GitHub** or depositing it on **Zenodo**. Each item must be verified by a project author.

## Privacy and scope

- [ ] **No private manuscript files** — no `.tex`, `main.pdf`, `sections/`, or other LaTeX sources from `paper/`.
- [ ] **No local bibliography copies** — no `references.bib`, `refs.bib`, or copies of `~/papers/bibliography.bib` in the artefact.
- [ ] **No reviewer correspondence** — no reviews, rebuttals, decision letters, or submission metadata.
- [ ] **No API keys or local paths** — no credentials, `.env` files, tokens, or machine-specific absolute paths in code, configs, or notebooks.

## Reproducibility

- [ ] **All scripts run from frozen data** — `make reproduce` completes without LLM API calls or network access to generation endpoints.
- [ ] **Reproducibility command tested** — `make check-env` and `make reproduce` run cleanly on a fresh clone in a clean environment.
- [ ] Regenerated outputs under `results/` match the tables and figures cited in the paper (or deviations are documented).

## Documentation and metadata

- [ ] **Author metadata compliant** — names, affiliations, email, and ORCID match `~/papers/promts/author_identity_standardization.md`; no invented or duplicate author copies in project files.
- [ ] **Editorial final pass** — `~/papers/promts/editorial_final_pass.md` checklist completed for the manuscript.
- [ ] **README updated** — placeholders (DOIs, abstract) replaced; [Privacy and scope](../README.md#privacy-and-scope) section accurate; contact matches central author identity.
- [ ] **CITATION.cff updated** — authors, title, version, date, and preferred citation match the published record.
- [ ] **zenodo.json updated** — creators, keywords, related identifiers, and licence align with the Zenodo deposit.
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
