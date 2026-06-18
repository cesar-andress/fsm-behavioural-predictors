# Zenodo record — EMSE submission freeze

Permanent archive of the RAP-AQ replication package for the EMSE submission manuscript.

## DOI

- **Version DOI (this release):** [10.5281/zenodo.20738203](https://doi.org/10.5281/zenodo.20738203)
- **Concept DOI (all versions):** [10.5281/zenodo.20598128](https://doi.org/10.5281/zenodo.20598128)
- **Record URL:** https://zenodo.org/records/20738203

## Citation

Andrés, C. (2026). *Replication Package: RAP-AQ Reportability Audit for LLM-Generated Finite State Machines* (Version v1.0.0-submission) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.20738203

```bibtex
@software{rap_aq_artifact_2026,
  author       = {Andr\'es, C\'esar},
  title        = {Replication Package: RAP-AQ Reportability Audit for LLM-Generated Finite State Machines},
  year         = {2026},
  version      = {v1.0.0-submission},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.20738203},
  url          = {https://github.com/cesar-andress/fsm-behavioural-predictors}
}
```

Machine-readable metadata: [CITATION.cff](../CITATION.cff).

## Release version

**v1.0.0-submission** — EMSE submission freeze.

Git tag: [v1.0.0-submission](https://github.com/cesar-andress/fsm-behavioural-predictors/tree/v1.0.0-submission)

## Reproducibility scope

This deposit supports independent verification of all results reported in the submission manuscript without re-running LLM inference.

**Primary entry point:**

```bash
make reproduce
```

From frozen campaign records in `data/raw/` and `data/processed/`, a reader can reproduce:

- RAP-AQ reportability audit workflow
- grouped-hold-out definability audit (`n_dc`)
- prevalence-only baseline analysis
- fixed audit predictor contract
- pair-partition diagnostics
- simulation and methodological-support artefacts
- manuscript tables and figures under `outputs/`

The LaTeX manuscript is **not** included in this archive. **No post-submission analyses are included in this release.**

See [REPRODUCIBILITY.md](../REPRODUCIBILITY.md) and [ARTIFACT_MANIFEST.md](../ARTIFACT_MANIFEST.md).

## Prior version

| Version | DOI |
|---------|-----|
| v0.1.0-pre-submission | [10.5281/zenodo.20598129](https://doi.org/10.5281/zenodo.20598129) |
