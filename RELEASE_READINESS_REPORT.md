# Release readiness report — v0.3.0-revision-candidate

> **Superseded** by [RELEASE_CHECKLIST_v1.0.0-submission.md](RELEASE_CHECKLIST_v1.0.0-submission.md).

**Audit date:** 2026-06-15  
**Auditor:** release-preparation pass (documentation and verification only)  
**Repositories audited:**

- Artifact: `~/papers/sqj2026/fsm-behavioural-predictors`
- Manuscript: `~/papers/sqj2026/paper` (private; not shipped in artefact)

**Actions explicitly not taken:** no git tag, no GitHub Release, no Zenodo upload.

---

## 1. Reproducibility status

| Check | Result | Evidence |
|-------|--------|----------|
| `make reproduce` | **PASS** | ~13 s; exit 0 |
| `make verify-manuscript` | **PASS** | 24 files across 9 legacy anchors |
| `make strengthen-stats` | **PASS** | ~3 min 27 s; 34 outputs; manifest written |
| Manuscript `make verify` | **PASS** | VERIFY OK; 28 pages; 0 warnings |
| Primary numerics vs CSV | **PASS** | Family B AUC, ρ, bootstrap Δ match `outputs/tables/*.csv` |
| Frozen data immutability | **PASS** | `make reproduce` does not modify `data/raw/` |
| LLM re-inference required | **NO** | Confirmed |

**Overall reproducibility:** **Strong** for a third party with Python 3.11 and documented commands. Dual pipeline (`reproduce` + `strengthen-stats`) is required for full manuscript coverage.

---

## 2. Missing files

| Item | Severity | Detail |
|------|----------|--------|
| Committed strengthen-stats scripts | **Blocker for tag** | 11 scripts staged (`A`/`M` in git) but release tag should include committed code |
| Committed `outputs/` tree | **Blocker for tag** | 34 strengthened outputs staged; Zenodo deposit needs pinned archive |
| Updated `CITATION.cff` | **High** | Still `v0.1.0-pre-submission`, 2026-06-08 |
| Updated `zenodo.json` | **High** | Same stale version metadata |
| Updated `docs/zenodo_record.md` | **Medium** | Likely references v0.1.0 scope |
| Strengthened figure auto-sync to paper | **Medium** | Not in `generate_figures.py` MANUSCRIPT_FIGURES list |

**No missing manuscript-critical outputs** were detected after running both make targets.

---

## 3. Missing documentation

| Document | Status |
|----------|--------|
| `README.md` (v0.3.0) | **Created** — this pass |
| `ARTIFACT_MANIFEST.md` | **Created** |
| `REPRODUCIBILITY.md` (root) | **Created** — supersedes partial `docs/reproducibility.md` for v0.3.0 |
| `RELEASE_NOTES_v0.3.0.md` | **Created** |
| `MANUSCRIPT_ARTIFACT_ALIGNMENT.md` | **Created** in `paper/paper_notes/` |
| `docs/reproducibility.md` | **Stale** — states bootstrap not used; no strengthen-stats section |
| `docs/artifact_structure.md` | **Stale** — no `outputs/` tree documented |
| Appendix workflow text (manuscript) | **Stale** — cites v0.1.0 tag |

---

## 4. Broken references

| Location | Issue | Severity |
|----------|-------|----------|
| Manuscript LaTeX `\ref`/`\cite` | None | — |
| `verify_manuscript_outputs.py` | Does not reference `outputs/` | Medium — false confidence if only legacy verify run |
| `CITATION.cff` → GitHub tag URL | Points to v0.1.0 tree | High for Zenodo |
| `zenodo.json` related_identifier | v0.1.0 GitHub URL | High for Zenodo |
| Bibliography article DOI | `10.1007/PLACEHOLDER` in CITATION.cff preferred-citation | Expected pre-publication |

**Manuscript build references:** no broken `\ref` or undefined citations at audit time.

---

## 5. Non-reproducible numbers

**Primary strengthened Results:** all checked values reproduce from `outputs/tables/` after `make strengthen-stats`.

| Area | Finding |
|------|---------|
| §5.1–5.4 embedded tables | Match CSV formatted intervals |
| Abstract | Match strengthened exports |
| Appendix legacy tables | Match `results/tables/*.md` exports |
| Hand-rounded embeds | Minor rounding only (e.g. 0.667 vs 0.6667 in CSV) — acceptable |

**No scientific conclusion changes required.** No bugs discovered in the strengthened pipeline during this audit.

---

## 6. Large files that should not be included (or should be optional)

| File | Size | Recommendation |
|------|------|----------------|
| `outputs/stats/repeated_seed_oof_predictions.csv` | ~6.3 MB | Include in Zenodo (audit trail) or document as regenerable intermediate |
| `outputs/tables/bootstrap_delta_iterations.csv` | ~1.5 MB | Same — regenerable from `make strengthen-stats` |
| `data/raw/` (total) | ~3.8 MB (with processed) | **Include** — required for reproduction |
| Legacy figure PNGs | <400 KB each | Include |
| `paper/figures/loso_system_heatmap.png` | ~218 KB | Optional in manuscript tree; include in artefact deposit |

**Exclude from any release:** credentials, `.env`, internal notes, reviewer correspondence (already gitignored).

---

## 7. Recommended final release contents

### Git tag `v0.3.0-revision-candidate` should contain

```
README.md, ARTIFACT_MANIFEST.md, REPRODUCIBILITY.md, RELEASE_NOTES_v0.3.0.md
LICENSE, CITATION.cff (updated), zenodo.json (updated)
Makefile, requirements.txt, environment.yml
data/raw/, data/processed/
scripts/ (including strengthen-stats layer)
results/tables/, results/figures/ (regenerated or pinned)
outputs/ (full strengthened tree — 34 files)
docs/ (updated zenodo_record.md, artifact_structure.md)
```

### GitHub Release notes

- Attach `RELEASE_NOTES_v0.3.0.md` as release body
- Link to Zenodo version DOI once uploaded
- Note dual command path: `make reproduce` + `make strengthen-stats`

### Zenodo deposit

- New version under concept DOI 10.5281/zenodo.20598128
- Update title/description to match definibility-first framing
- Pin git commit hash from manifest (`d3a1d292…` or post-commit hash after staging)
- Upload full repository archive (or GitHub-Zenodo integration)

### Pre-tag checklist (minimum)

1. Commit all staged strengthen-stats scripts and `outputs/`
2. Update `CITATION.cff`, `zenodo.json`, `docs/zenodo_record.md`
3. Extend `verify_manuscript_outputs.py` to check `outputs/` primary files (recommended)
4. Fix `make check-env` documentation (Conda env required) or relax seaborn gate
5. Update manuscript appendix tag reference to v0.3.0
6. Re-run `make reproduce && make strengthen-stats && make verify` on clean checkout

---

## 8. Go / No-Go recommendation

### Verdict: **CONDITIONAL GO**

The artefact and manuscript are **scientifically aligned and reproducible** for `v0.3.0-revision-candidate`. Primary strengthened evidence traces cleanly from frozen data through scripts to manuscript numbers. Both pipelines execute successfully with documented runtime.

**Conditions before creating the tag and publishing GitHub Release / Zenodo:**

| # | Condition | Priority |
|---|-----------|----------|
| 1 | Commit strengthen-stats code + `outputs/` to git | **Required** |
| 2 | Update `CITATION.cff` and `zenodo.json` to v0.3.0 | **Required** |
| 3 | Re-run full verify on committed tree | **Required** |
| 4 | Update appendix Zenodo/tag citation in manuscript | **Required** |
| 5 | Extend verify script for `outputs/` | Recommended |
| 6 | Sync strengthened figures in `generate_figures.py` | Recommended |
| 7 | Refresh `docs/reproducibility.md` or add redirect to root `REPRODUCIBILITY.md` | Recommended |

**Do not block on:** journal article DOI placeholder, stale `submission/sqj2026/` snapshot, deposit-only LOSO heatmap.

---

## Audit commands log

```bash
cd fsm-behavioural-predictors
make reproduce                    # PASS, ~13 s
make verify-manuscript            # PASS
make strengthen-stats             # PASS, ~3 min 27 s
cd ../paper && make verify        # VERIFY OK
```

**Environment note:** `make check-env` failed with `ModuleNotFoundError: seaborn` when the Conda env was not activated; pipelines ran successfully under `python3.11` with core scientific stack installed.

---

*End of report.*
