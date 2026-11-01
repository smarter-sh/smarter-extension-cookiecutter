SHELL := /bin/bash

ifeq ($(OS),Windows_NT)
    PYTHON := python.exe
    ACTIVATE_VENV := venv/Scripts/activate
else
    PYTHON := python3.14
    ACTIVATE_VENV := source venv/bin/activate
endif
PIP := $(PYTHON) -m pip
BUILD := build

.PHONY: all init check-python python-init python-clean pre-commit-init pre-commit-run pre-commit-update \
	lint test bake test-generated clean help

# Default target executed when no arguments are given to make.
all: help

# initialize the local development environment: a Python virtual environment with cookiecutter and
# pre-commit, and the pre-commit hooks.
init:
	make check-python
	make python-init
	make pre-commit-init

check-python:
	@command -v $(PYTHON) >/dev/null 2>&1 || { \
	echo >&2 "This project requires $(PYTHON) but it's not installed.  Aborting."; \
	exit 1; \
}

python-init:
	@echo "==============================================================================="
	@echo "Initializing the Python virtual environment ..."
	@echo "==============================================================================="
	make python-clean
	$(PYTHON) -m venv venv && \
	$(ACTIVATE_VENV) && \
	$(PIP) install --upgrade pip && \
	$(PIP) install -r requirements/local.txt

python-clean:
	rm -rf venv
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

pre-commit-init:
	$(ACTIVATE_VENV) && pre-commit install

pre-commit-run:
	$(ACTIVATE_VENV) && pre-commit run --all-files

pre-commit-update:
	$(ACTIVATE_VENV) && pre-commit autoupdate

lint:
	make pre-commit-run

# the template's tests: generate extensions with different answers, and check them.
test:
	$(ACTIVATE_VENV) && python -m unittest discover -s tests -t . -v

# generate an extension from the working tree, with the default answers, into build/, to look at.
bake:
	$(ACTIVATE_VENV) && cookiecutter --no-input --overwrite-if-exists --output-dir $(BUILD) .

# generate one extension per starter into build/, and run each one's own tests and
# validate_extension in a Smarter development container (smarter-app), as an author would.
test-generated:
	$(ACTIVATE_VENV) && \
	cookiecutter --no-input --overwrite-if-exists --output-dir $(BUILD) . extension_name="Example Web Api" starter=web-api && \
	cookiecutter --no-input --overwrite-if-exists --output-dir $(BUILD) . extension_name="Example Function" starter=pure-function && \
	$(BUILD)/smarter-extension-example-web-api/scripts/run-tests.sh --validate && \
	$(BUILD)/smarter-extension-example-function/scripts/run-tests.sh --validate

clean:
	make python-clean
	rm -rf $(BUILD)

help:
	@echo '===================================================================='
	@echo 'init                   - Create the virtual environment and install the pre-commit hooks'
	@echo 'test                   - Run the template tests (generate and check extensions)'
	@echo 'bake                   - Generate an extension with the default answers into build/'
	@echo 'test-generated         - Generate both starters and run their tests in smarter-app'
	@echo 'lint                   - Run all code linters and formatters (pre-commit)'
	@echo 'clean                  - Delete the virtual environment and build/'
	@echo '===================================================================='
