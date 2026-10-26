PYTHON ?= python3
.PHONY: help setup simulate exhaustive synth gate gate-exhaustive validate lint physical-preflight physical timing experiments report clean test
help:
	@echo 'setup simulate exhaustive synth gate gate-exhaustive validate lint test physical-preflight physical timing experiments report clean'
	@echo 'Physical: see docs/ENVIRONMENT.md for the pinned Linux ORFS setup'
setup:
	bash scripts/setup.sh
simulate:
	$(PYTHON) scripts/simulate.py
exhaustive:
	$(PYTHON) scripts/simulate.py --exhaustive
synth:
	$(PYTHON) scripts/synthesize.py
gate:
	$(PYTHON) scripts/gate_simulate.py
gate-exhaustive:
	$(PYTHON) scripts/gate_simulate.py --exhaustive
validate:
	$(PYTHON) scripts/validate.py
lint:
	iverilog -g2012 -Wall -s alu_top -tnull rtl/alu_8bit.sv rtl/alu_top.sv
test:
	$(PYTHON) -m unittest discover -s tests -v
physical:
	$(PYTHON) scripts/physical.py
physical-preflight:
	$(PYTHON) scripts/physical.py --preflight
timing:
	$(PYTHON) scripts/report.py --timing
experiments:
	$(PYTHON) scripts/run_experiments.py --study $(or $(STUDY),baseline)
report:
	$(PYTHON) scripts/report.py
clean:
	$(PYTHON) scripts/clean.py
