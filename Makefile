# Makefile for memU MCP Server

.PHONY: help install install-dev test lint format clean run example

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install package dependencies"
	@echo "  install-dev - Install package with development dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code with black"
	@echo "  clean       - Clean up build artifacts"
	@echo "  run         - Run the server"
	@echo "  example     - Run basic usage example"
	@echo "  help        - Show this help message"

# Install package dependencies
install:
	pip install -r requirements.txt

# Install with development dependencies
install-dev:
	pip install -r requirements.txt
	pip install -e .[dev]

# Run tests
test:
	pytest tests/ -v --cov=src/memu_mcp_server --cov-report=term-missing

# Run linting checks
lint:
	flake8 src/memu_mcp_server tests examples
	mypy src/memu_mcp_server

# Format code
format:
	black src/memu_mcp_server tests examples

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the server (requires MEMU_API_KEY environment variable)
run:
	python -m memu_mcp_server.main

# Run basic usage example
example:
	python examples/basic_usage.py

# Run with debug logging
debug:
	python -m memu_mcp_server.main --log-level DEBUG

# Install pre-commit hooks
pre-commit:
	pre-commit install

# Run all checks (format, lint, test)
check: format lint test
	@echo "All checks passed!"

# Build package
build:
	python -m build

# Create virtual environment
venv:
	python -m venv venv
	@echo "Activate virtual environment with:"
	@echo "  source venv/bin/activate  # On macOS/Linux"
	@echo "  venv\\Scripts\\activate     # On Windows"