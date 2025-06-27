# Install dependencies
install:
    uv pip install -e .[dev]

# Run tests
test:
    uv run pytest

# Format code
format:
    uv run ruff format .

# Lint code
lint:
    uv run ruff check .

# Fix linting issues
fix:
    uv run ruff check --fix .

# Type check
typecheck:
    uv run mypy .

# Build package
build:
    uv build

# Clean build artifacts
clean:
    rm -rf dist/
    rm -rf .pytest_cache/
    rm -rf __pycache__/
    find . -name "*.pyc" -delete

# Publish to PyPI
publish:
    uv publish

# Run all checks
check: lint typecheck test

# Show project info
info:
    uv tree
