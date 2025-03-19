# Directories.
BACKEND_DIR := backend
FRONTEND_DIR := frontend
POLICY_DB_DIR := policies

# Python virtual environment.
VENV := .venv
PYTHON := python
PIP := $(VENV)/bin/pip

# Activate venv and install dependencies for backend.
install-backend-deps:
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt

run-backend: install-backend-deps
	@cd $(BACKEND_DIR) && $(PYTHON) app.py

# Deletes all PolicyDB.
clean-policies:
	@rm -rf $(POLICY_DB_DIR)