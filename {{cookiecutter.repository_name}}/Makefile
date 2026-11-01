SHELL := /bin/bash

ifeq ($(OS),Windows_NT)
    PYTHON := python.exe
    ACTIVATE_VENV := venv/Scripts/activate
else
    PYTHON := python3.14
    ACTIVATE_VENV := source venv/bin/activate
endif
PIP := $(PYTHON) -m pip

.PHONY: all init check-python python-init python-clean pre-commit-init pre-commit-run pre-commit-update \
	lint test validate package clean help

# Default target executed when no arguments are given to make.
all: help

# initialize the local development environment: a Python virtual environment with the development
# tools, and the pre-commit hooks. The tests run in a Smarter development container: see `make test`.
init:
	make check-python
	make python-init
	make pre-commit-init
	@echo ""
	@echo "==============================================================================="
	@echo "Initialization complete!"
	@echo ""
	@echo "Run 'source venv/bin/activate' to activate the Python virtual environment."
	@echo "Run 'make test' to run the tests in a Smarter development container."
	@echo "    'make help' to see all available commands."
	@echo "==============================================================================="

check-python:
	@echo "==============================================================================="
	@echo "Verifying that Python $(PYTHON) is installed ..."
	@echo "==============================================================================="
	@command -v $(PYTHON) >/dev/null 2>&1 || { \
	echo >&2 "This project requires $(PYTHON) but it's not installed.  Aborting."; \
	echo >&2 "python --version output:"; \
	python --version 2>&1; \
	exit 1; \
}

python-init:
	@echo "==============================================================================="
	@echo "Initializing the Python virtual environment and installing the development tools ..."
	@echo "==============================================================================="
	make python-clean
	$(PYTHON) -m venv venv && \
	$(ACTIVATE_VENV) && \
	$(PIP) install --upgrade pip && \
	$(PIP) install -r requirements/local.txt

python-clean:
	rm -rf venv
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

# ---------------------------------------------------------
# Code management
# ---------------------------------------------------------

pre-commit-init:
	@echo "==============================================================================="
	@echo "Installing the pre-commit hooks (pre-commit and commit-msg) ..."
	@echo "==============================================================================="
	$(ACTIVATE_VENV) && pre-commit install

pre-commit-run:
	@echo "==============================================================================="
	@echo "Running pre-commit hooks on all files ..."
	@echo "==============================================================================="
	$(ACTIVATE_VENV) && pre-commit run --all-files

pre-commit-update:
	$(ACTIVATE_VENV) && pre-commit autoupdate

lint:
	make pre-commit-run

# the unit tests, with coverage, in the smarter-app container of a Smarter development
# environment (a checkout of smarter-sh/smarter, started with its `make run`).
test:
	scripts/run-tests.sh

# the tests, then manage.py validate_extension: the checks the installer and the registry make.
validate:
	scripts/run-tests.sh --validate

# the release archive, dist/<slug>-<version>.zip, and its sha256, exactly as a release builds it.
package:
	$(PYTHON) scripts/package.py dist

clean:
	make python-clean
	rm -rf dist .coverage coverage.xml htmlcov

help:
	@echo '===================================================================='
	@echo 'init                   - Create the virtual environment and install the pre-commit hooks'
	@echo 'test                   - Run the tests, with coverage, in the smarter-app container'
	@echo 'validate               - Run the tests, then manage.py validate_extension'
	@echo 'package                - Build the release archive in dist/'
	@echo 'clean                  - Delete the virtual environment and build artifacts'
	@echo '<************************** Code Management **************************>'
	@echo 'lint                   - Run all code linters and formatters (pre-commit)'
	@echo 'pre-commit-update      - Update the pre-commit hooks to their latest versions'
	@echo '===================================================================='
