# SQJ 2026 public artefact — reproduction targets
# Prerequisites: Python environment (see README.md)

PYTHON ?= python3
SCRIPTS = scripts

.PHONY: all check-env reproduce tables figures clean help

all: reproduce

help:
	@echo "Targets:"
	@echo "  make check-env   Verify Python and core dependencies"
	@echo "  make reproduce   Regenerate all tables and figures from frozen data"
	@echo "  make tables      Regenerate tables only"
	@echo "  make figures     Regenerate figures only"
	@echo "  make clean       Remove generated outputs under results/"

check-env:
	@$(PYTHON) -c "import numpy, pandas, scipy, sklearn, matplotlib, seaborn; print('Environment OK')"

reproduce: tables figures
	@echo "Reproduction complete. Outputs in results/"

tables:
	@echo "Generating tables..."
	@$(PYTHON) $(SCRIPTS)/generate_tables.py

figures:
	@echo "Generating figures..."
	@$(PYTHON) $(SCRIPTS)/generate_figures.py

clean:
	rm -rf results/tables/*
	rm -rf results/figures/*
	@touch results/tables/.gitkeep results/figures/.gitkeep
	@echo "Cleaned generated outputs (data/ preserved)"
