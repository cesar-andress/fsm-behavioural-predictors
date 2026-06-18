# Release checklist — v1.0.0-submission (EMSE)

Frozen reproducibility artefact for the RAP-AQ manuscript submitted to **Empirical Software Engineering**.

**DOI:** [10.5281/zenodo.20738203](https://doi.org/10.5281/zenodo.20738203)

---

## Pre-flight

- [x] Documentation framing — RAP-AQ / EMSE submission
- [x] Primary entry point — `make reproduce`
- [x] Zenodo DOI — `10.5281/zenodo.20738203` in README, CITATION.cff, zenodo.json, verify scripts
- [x] No post-submission analyses in release scope
- [ ] Raw data unchanged (`data/raw/`)
- [ ] Empirical spot-check — `table5_strengthened.csv`, `table6_strengthened.csv`

---

## Commands

```bash
make check-env
make reproduce
make legacy-reproduce    # optional deposit-only
make verify-manuscript
```

---

## Verification

| Check | Result |
|-------|--------|
| `make check-env` | PASS |
| `make reproduce` | PASS |
| `make verify-submission` | PASS (18 files) |
| `make verify-manuscript` | PASS (24 files, legacy) |

---

## Git metadata

| Field | Value |
|-------|-------|
| Tag | `v1.0.0-submission` |
| Commit | `git rev-parse HEAD` at publish time |

---

## Zenodo

- [x] Version DOI published — [10.5281/zenodo.20738203](https://doi.org/10.5281/zenodo.20738203)
- [ ] GitHub release/tag points to matching commit
- [ ] Archive upload matches tagged tree
