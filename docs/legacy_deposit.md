# Legacy deposit-only analyses

The following scripts and outputs belong to an earlier predictor-comparison study framing.
They are **not cited** in the RAP-AQ manuscript but remain in the repository for traceability.

| Item | Location | Status |
|------|----------|--------|
| Families A–D single-seed CV | `scripts/model_behavioural_correctness.py` | Legacy deposit |
| LOMO cross-model hold-out | `scripts/lomo_model_evaluation.py`, `results/tables/lomo_*` | Legacy deposit |
| Pre-oracle screen / risk toolkit | `scripts/pre_oracle_prediction.py`, `scripts/risk_toolkit.py` | Legacy deposit |
| Repair-loop figure source | `../paper/figures/fig_repair_loop.tex` (private manuscript tree) | Not in manuscript PDF |
| `cv_seed_distribution_family_b.png` | `outputs/figures/` | Regenerated but not in manuscript body |
| SQJ / submission snapshot references | `RELEASE_NOTES_v0.3.0.md`, old readiness reports | Superseded by `v1.0.0-submission` |

**Submission freeze command:** `make reproduce` (RAP-AQ outputs under `outputs/`).
