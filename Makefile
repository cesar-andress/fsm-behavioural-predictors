# RAP-AQ public artefact — reproduction targets
# Prerequisites: Python environment (see README.md)

PYTHON ?= python3.11
SCRIPTS = scripts

.PHONY: all check-env build-master reproduce submission-freeze legacy-reproduce tables figures profile-signals model-correctness loso-systems pre-oracle lomo-models risk-toolkit verify-manuscript verify-submission strengthen-stats methodological-upgrade clean help

all: reproduce

help:
	@echo "Targets:"
	@echo "  make reproduce           RAP-AQ EMSE submission freeze (primary)"
	@echo "  make check-env           Verify Python and core dependencies"
	@echo "  make build-master        Build data/processed/master_analysis_dataset.csv"
	@echo "  make strengthen-stats    RAP-AQ strengthened outputs under outputs/"
	@echo "  make methodological-upgrade  Pair-partition diagnostics + simulation"
	@echo "  make verify-submission   Check RAP-AQ manuscript output paths"
	@echo "  make legacy-reproduce    Legacy predictor-study pipeline under results/ (deposit only)"
	@echo "  make verify-manuscript   Check legacy results/ paths"
	@echo "  make clean               Remove generated outputs under results/"

check-env:
	@$(PYTHON) -c "import numpy, pandas, scipy, sklearn, matplotlib, seaborn; print('Environment OK')"

build-master:
	@$(PYTHON) $(SCRIPTS)/build_master_dataset.py

reproduce: build-master strengthen-stats methodological-upgrade verify-submission
	@echo "RAP-AQ reproduction complete. Primary outputs in outputs/"

submission-freeze: reproduce
	@echo "Note: submission-freeze is an alias for reproduce."

legacy-reproduce: build-master tables profile-signals model-correctness loso-systems pre-oracle lomo-models risk-toolkit figures verify-manuscript
	@echo "Legacy reproduction complete. Outputs in results/ (deposit-only analyses)."

tables:
	@echo "Generating tables..."
	@$(PYTHON) $(SCRIPTS)/generate_tables.py

figures:
	@echo "Verifying manuscript figures..."
	@$(PYTHON) $(SCRIPTS)/generate_figures.py --sync

verify-manuscript:
	@$(PYTHON) $(SCRIPTS)/verify_manuscript_outputs.py

verify-submission:
	@$(PYTHON) $(SCRIPTS)/verify_submission_outputs.py

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

lomo-models: build-master model-correctness
	@echo "Running leave-one-model-out evaluation (legacy deposit)..."
	@$(PYTHON) $(SCRIPTS)/lomo_model_evaluation.py

risk-toolkit: build-master
	@echo "Running behavioural risk toolkit..."
	@$(PYTHON) $(SCRIPTS)/risk_toolkit.py \
		--input data/processed/master_analysis_dataset.csv \
		--output results/tables/risk_toolkit_predictions.csv

strengthen-stats: build-master
	@echo "Running strengthened-stats pipeline..."
	@$(PYTHON) $(SCRIPTS)/run_strengthened_stats.py

methodological-upgrade:
	@echo "Running methodological-upgrade analyses..."
	@$(PYTHON) $(SCRIPTS)/grouped_auc_decomposition.py
	@$(PYTHON) $(SCRIPTS)/grouped_auc_bootstrap.py
	@$(PYTHON) $(SCRIPTS)/simulate_grouped_reportability.py

clean:
	rm -rf results/tables/*
	rm -rf results/figures/*
	@touch results/tables/.gitkeep results/figures/.gitkeep
	@echo "Cleaned generated outputs (data/ preserved)"
