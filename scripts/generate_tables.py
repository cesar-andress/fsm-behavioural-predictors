#!/usr/bin/env python3
"""
Generate all paper tables from frozen data.

Reads from data/processed/ (and data/raw/ if needed).
Writes to results/tables/.
Does not invoke LLM inference.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "results" / "tables"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Placeholder: implement table generation when datasets are available.
    placeholder = OUT_DIR / "README.txt"
    placeholder.write_text(
        "Table outputs will be generated here by this script once data/processed/ "
        "is populated.\n"
        "Run: make tables\n",
        encoding="utf-8",
    )
    print(f"Placeholder written to {placeholder}")
    print("No frozen data found yet — populate data/ before final reproduction.")


if __name__ == "__main__":
    main()
