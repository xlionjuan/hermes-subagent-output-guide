# ──────────────────────────────────────────────────────────────────────────────
# subagent-output-guide — task runner
# ──────────────────────────────────────────────────────────────────────────────

default: verify

# Run full verification suite: lint → format check → tests
verify: lint format-check test

# Run tests
test:
    uv run pytest

# Lint with ruff
lint:
    uv run ruff check .

# Format code in-place with ruff
format:
    uv run ruff format .

# Check formatting without modifying files
format-check:
    uv run ruff format --check .
