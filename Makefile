# SQJ 2026 public artefact — reproduction targets
# Prerequisites: Python environment (see README.md)

PYTHON ?= python3.11
SCRIPTS = scripts

.PHONY: all check-env build-master reproduce tables figures profile-signals model-correctness loso-systems pre-oracle clean help

all: reproduce

help:
	@echo "Targets:"
	@echo "  make check-env      Verify Python and core dependencies"
	@echo "  make build-master   Build data/processed/master_analysis_dataset.csv"
	@echo "  make reproduce        Regenerate all tables and figures from frozen data"
	@echo "  make tables           Regenerate descriptive profiling tables"
	@echo "  make profile-signals    Descriptive and predictive-signal profiling"
	@echo "  make model-correctness  Exploratory CV models for full behavioural pass"
	@echo "  make loso-systems       Leave-one-system-out generalization study"
	@echo "  make pre-oracle         Pre-oracle behavioural prediction (strict features)"
	@echo "  make figures            Regenerate figures only"
	@echo "  make clean       Remove generated outputs under results/"

check-env:
	@$(PYTHON) -c "import numpy, pandas, scipy, sklearn, matplotlib, seaborn; print('Environment OK')"

build-master:
	@$(PYTHON) $(SCRIPTS)/build_master_dataset.py

reproduce: build-master tables figures
	@echo "Reproduction complete. Outputs in results/"

tables:
	@echo "Generating tables..."
	@$(PYTHON) $(SCRIPTS)/generate_tables.py

figures:
	@echo "Generating figures..."
	@$(PYTHON) $(SCRIPTS)/generate_figures.py

profile-signals: build-master
	@echo "Profiling predictive signals..."
	@$(PYTHON) $(SCRIPTS)/profile_predictive_signals.py

model-correctness: build-master
	@echo "Modelling behavioural correctness..."
	@$(PYTHON) $(SCRIPTS)/model_behavioural_correctness.py

loso-systems: build-master model-correctness
	@echo "Running leave-one-system-out evaluation..."
	@$(PYTHON) $(SCRIPTS)/loso_system_evaluation.py

pre-oracle: build-master model-correctness
	@echo "Running pre-oracle prediction study..."
	@$(PYTHON) $(SCRIPTS)/pre_oracle_prediction.py

clean:
	rm -rf results/tables/*
	rm -rf results/figures/*
	@touch results/tables/.gitkeep results/figures/.gitkeep
	@echo "Cleaned generated outputs (data/ preserved)"
