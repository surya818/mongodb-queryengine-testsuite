.PHONY: help install test test-unit test-integration test-performance clean lint format setup

# Default target
help:
	@echo "MongoDB Test Automation Suite"
	@echo "Available commands:"
	@echo "  install           Install dependencies"
	@echo "  setup            Setup virtual environment and install dependencies"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only" 
	@echo "  test-performance Run performance tests only"
	@echo "  test-verbose     Run tests with verbose output"
	@echo "  clean            Clean up cache and temporary files"
	@echo "  lint             Run code linting (if available)"
	@echo "  format           Format code (if available)"

# Setup virtual environment and install dependencies
setup:
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "Setup complete. Activate virtual environment with: source .venv/bin/activate"

# Install dependencies
install:
	pip install -r requirements.txt

# Run all tests
test:
	pytest

# Run unit tests only
test-unit:
	pytest src/tests/unit/

# Run integration tests only
test-integration:
	pytest src/tests/integration/

# Run performance tests only
test-performance:
	pytest src/tests/performance/

# Run tests with verbose output
test-verbose:
	pytest -v

# Clean up cache and temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf logs/*.log 2>/dev/null || true
	rm -rf reports/* 2>/dev/null || true

# Lint code (requires additional tools)
lint:
	@echo "Add linting tools like flake8, pylint, or black to requirements.txt to enable linting"

# Format code (requires additional tools)
format:
	@echo "Add formatting tools like black or autopep8 to requirements.txt to enable formatting"