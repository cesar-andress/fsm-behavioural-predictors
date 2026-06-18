# Release notes — v1.0.0-submission

**Tag:** `v1.0.0-submission`  
**Journal:** Empirical Software Engineering (EMSE)  
**DOI:** [10.5281/zenodo.20738203](https://doi.org/10.5281/zenodo.20738203)

---

Frozen reproducibility artefact for the RAP-AQ manuscript submitted to Empirical Software Engineering (EMSE).

This release contains the complete reproducibility package used for the submission manuscript, including:

- RAP-AQ reportability audit workflow
- grouped-hold-out definability audit (`n_dc`)
- prevalence-only baseline analysis
- fixed audit predictor contract
- pair-partition diagnostics
- simulation and methodological-support artefacts
- manuscript tables and figures
- reproducibility scripts and Make targets

**Primary entry point:**

```bash
make reproduce
```

The release freezes the submission artefact associated with DOI [10.5281/zenodo.20738203](https://doi.org/10.5281/zenodo.20738203) and is intended to support independent verification of all results reported in the manuscript.

**No post-submission analyses are included in this release.**

---

## Reproduction

```bash
git checkout v1.0.0-submission
conda env create -f environment.yml && conda activate fsm-behavioural-predictors
make check-env
make reproduce
```

Expected terminal output:

```
RAP-AQ submission output verification OK (18 files across 4 anchors)
Zenodo DOI: https://doi.org/10.5281/zenodo.20738203
RAP-AQ reproduction complete. Primary outputs in outputs/
```

---

## Citation

```bibtex
@software{rap_aq_artifact_2026,
  author    = {Andr\'es, C\'esar},
  title     = {Replication Package: RAP-AQ Reportability Audit for LLM-Generated Finite State Machines},
  year      = {2026},
  version   = {v1.0.0-submission},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.20738203},
  url       = {https://github.com/cesar-andress/fsm-behavioural-predictors}
}
```

---

## Prior archives

| Version | DOI | Notes |
|---------|-----|-------|
| v0.1.0-pre-submission | [10.5281/zenodo.20598129](https://doi.org/10.5281/zenodo.20598129) | SQJ-era pre-submission deposit |

---

## Superseded documents

- `RELEASE_NOTES_v0.3.0.md`
- `RELEASE_READINESS_REPORT.md`
- `docs/release_checklist.md` (v0.1.0 checklist)
