#!/usr/bin/env python3
"""
Verify that all manuscript-linked figures exist under results/figures/.

Empirical figures are produced by the analysis scripts invoked from `make reproduce`
(profile_predictive_signals, model_behavioural_correctness, loso_system_evaluation,
lomo_model_evaluation, pre_oracle_prediction). This entry point checks completeness.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = ROOT / "results" / "figures"

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


def main() -> None:
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


if __name__ == "__main__":
    main()
