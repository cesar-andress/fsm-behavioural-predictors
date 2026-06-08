# Zenodo Record

Permanent archive of the SQJ 2026 public replication artefact.

## DOI

- **Version DOI:** [10.5281/zenodo.20598129](https://doi.org/10.5281/zenodo.20598129)
- **Concept DOI (all versions):** [10.5281/zenodo.20598128](https://doi.org/10.5281/zenodo.20598128)
- **Record URL:** https://zenodo.org/records/20598129

## Citation

Andrés, C. (2026). *Replication Package: Predicting Behavioural Correctness from Structural Signals in LLM-Generated Finite State Machines* (Version v0.1.0-pre-submission) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.20598129

```bibtex
@software{sqj2026_artifact,
  author       = {Andr\'es, C.},
  title        = {Replication Package: Predicting Behavioural Correctness from Structural Signals in LLM-Generated Finite State Machines},
  year         = {2026},
  version      = {v0.1.0-pre-submission},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.20598129},
  url          = {https://github.com/cesar-andress/fsm-behavioural-predictors}
}
```

Machine-readable metadata: [CITATION.cff](../CITATION.cff).

## Release version

**v0.1.0-pre-submission** — pre-submission release prepared for journal evaluation.

Git tag: [v0.1.0-pre-submission](https://github.com/cesar-andress/fsm-behavioural-predictors/tree/v0.1.0-pre-submission)

## Archive date

**2026-06-08** (published on Zenodo)

## Repository URL

- **GitHub:** https://github.com/cesar-andress/fsm-behavioural-predictors
- **Release tag:** https://github.com/cesar-andress/fsm-behavioural-predictors/tree/v0.1.0-pre-submission

## Reproducibility scope

This deposit supports independent verification of the pre-submission artefact without re-running LLM inference. From frozen campaign records in `data/raw/` and `data/processed/`, a reader can reproduce:

- descriptive profiling tables and figures;
- predictive modelling results (random CV, LOSO, LOMO, pre-oracle);
- behavioural risk toolkit outputs (BRS, AutoReject, FSM health reports);
- validation reports under `results/tables/`.

The default workflow is `make reproduce` (see [reproducibility.md](reproducibility.md)). The LaTeX manuscript is **not** included in this archive.

**Status:** Pre-submission release. Results, documentation, and metadata may be refined in future Zenodo versions associated with peer-review feedback.
