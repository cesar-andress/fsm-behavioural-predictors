#!/usr/bin/env python3
"""
Verify manuscript-linked figures and optionally sync PNG/PDF copies to the private paper.

Empirical figures are produced by the analysis scripts invoked from `make reproduce`
(profile_predictive_signals, model_behavioural_correctness, loso_system_evaluation,
lomo_model_evaluation, pre_oracle_prediction). This entry point checks completeness.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = ROOT / "results" / "figures"
PAPER_FIGURES_DIR = ROOT.parent / "paper" / "figures"

# Figures cited in the SQJ manuscript (Appendix Table artifact-outputs mapping).
MANUSCRIPT_FIGURES = [
    "bpr_by_gate.png",
    "bpr_by_model.png",
    "bpr_by_system.png",
    "roc_curves.png",
    "precision_recall_curves.png",
    "loso_system_heatmap.png",
    "lomo_heatmap.png",
]

# Additional package figures (pre-oracle study; optional for manuscript audit).
SUPPLEMENTARY_FIGURES = [
    "pre_oracle_roc.png",
    "pre_oracle_pr.png",
]


def sync_to_manuscript() -> list[Path]:
    """Copy verified manuscript figures (and PDF siblings) into paper/figures/."""
    PAPER_FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for name in MANUSCRIPT_FIGURES:
        src = FIGURES_DIR / name
        if not src.is_file():
            raise FileNotFoundError(f"Missing figure for sync: {src}")
        dst = PAPER_FIGURES_DIR / name
        shutil.copy2(src, dst)
        copied.append(dst)
        pdf_src = src.with_suffix(".pdf")
        if pdf_src.is_file():
            pdf_dst = PAPER_FIGURES_DIR / pdf_src.name
            shutil.copy2(pdf_src, pdf_dst)
            copied.append(pdf_dst)
    return copied


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Copy manuscript figures to ../paper/figures/ after verification",
    )
    args = parser.parse_args()

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    missing = [name for name in MANUSCRIPT_FIGURES if not (FIGURES_DIR / name).is_file()]
    if missing:
        print("ERROR: manuscript figures missing under results/figures/:", file=sys.stderr)
        for name in missing:
            print(f"  - {name}", file=sys.stderr)
        print(
            "\nRun the full pipeline from the repository root:\n"
            "  make reproduce\n",
            file=sys.stderr,
        )
        raise SystemExit(1)

    present = MANUSCRIPT_FIGURES + [
        name for name in SUPPLEMENTARY_FIGURES if (FIGURES_DIR / name).is_file()
    ]
    lines = [
        "# Figure outputs",
        "",
        "Verified by `scripts/generate_figures.py` after `make reproduce`.",
        "",
        "## Manuscript figures",
        "",
    ]
    for name in MANUSCRIPT_FIGURES:
        lines.append(f"- `{name}`")
    lines.extend(["", "## Supplementary figures", ""])
    for name in SUPPLEMENTARY_FIGURES:
        status = "present" if (FIGURES_DIR / name).is_file() else "not generated"
        lines.append(f"- `{name}` ({status})")
    lines.append("")
    (FIGURES_DIR / "README.txt").write_text("\n".join(lines), encoding="utf-8")

    print(f"Verified {len(MANUSCRIPT_FIGURES)} manuscript figures in {FIGURES_DIR}")
    for name in present:
        print(f"  OK {name}")

    if args.sync:
        copied = sync_to_manuscript()
        print(f"Synced {len(copied)} file(s) to {PAPER_FIGURES_DIR}")


if __name__ == "__main__":
    main()
