# Makefile for LinkedIn Outreach Generation Project

# Install dependencies
install:
	pip install -r requirements.txt

# Format code with black
format:
	black .

# Check formatting with black
check-format:
	black --check .

# Lint code with flake8
lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

# Type check with mypy
type-check:
	mypy --package pinggenius_backend_fastapi

# Run tests
test:
	pytest

# Run all checks (formatting, linting, type checking)
check:
	make check-format
	make lint
	make type-check

# Run the application
run:
	uvicorn main:app --reload

# Run the application in production mode
run-prod:
	gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

.PHONY: install format check-format lint type-check test check run run-prod