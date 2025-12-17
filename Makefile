.PHONY: install install-dev test test-cov lint lint-fix run build clean help

# Variables
PYTHON = python3
PIP = pip3
MANAGE_PY = python manage.py

# Help target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  lint         - Run linting checks"
	@echo "  lint-fix     - Run linting and auto-fix where possible"
	@echo "  run          - Run development server"
	@echo "  build        - Build project for production"
	@echo "  clean        - Clean build artifacts"

# Installation
install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

# Testing
test:
	pytest tests/

test-cov:
	pytest tests/ --cov=. --cov-report=term-missing --cov-report=html

# Linting
lint:
	ruff check .
	black --check .
	mypy .
 
lint-fix:
	ruff check --fix .
	black .
	isort .

# Development
run:
	$(MANAGE_PY) runserver

# Build
build:
	$(PYTHON) -m build

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
