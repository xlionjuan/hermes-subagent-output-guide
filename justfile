# ──────────────────────────────────────────────────────────────────────────────
# subagent-output-guide — task runner
# ──────────────────────────────────────────────────────────────────────────────

default: verify

# Run full verification suite: lint → format check → security → dead code → type check → tests
verify: lint format-check bandit vulture typecheck test

# Run tests
test:
    uv run pytest

# Lint with ruff
lint:
    uv run ruff check .

# Type check with ty
typecheck:
    uv run ty check . --exclude .vulture_whitelist.py

# Security scan with bandit (project files only)
bandit:
    uv run bandit -r __init__.py tests/ -c pyproject.toml

# Dead code detection with vulture
vulture:
    uv run vulture . .vulture_whitelist.py --exclude '.venv,dist,.git,__pycache__'

# Format code in-place with ruff
format:
    uv run ruff format .

# Check formatting without modifying files
format-check:
    uv run ruff format --check .

# Remove all __pycache__ directories and .pyc files
clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; find . -type f -name '*.pyc' -delete
