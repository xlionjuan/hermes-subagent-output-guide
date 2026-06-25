# subagent-output-guide

A Hermes user plugin that automatically injects output-location guidance into
subagent prompts, preventing subagents from writing files to arbitrary locations
when the parent agent (Kuri) forgets to specify an output path.

## How it works

Two hooks working together:

1. `subagent_start` — records `child_session_id` as belonging to a child agent
2. `pre_llm_call` — checks if the current `session_id` is a known child session.
   If so, and it's the first turn, injects a context block into the user message
   telling the subagent to write to `/tmp/` when no output path is specified.

## Verification

- pytest (all tests under tests/)
- ruff (linting + formatting)
- `ty` (static type checking)
- bandit (security scan)
- vulture (dead code detection)

Run before every commit:

    uv run ruff check .
    uv run ruff format --check .
    uv run bandit -r . -c pyproject.toml
    uv run vulture . --exclude '.venv,dist,.git,__pycache__'
    uv run ty check .
    uv run pytest

Or via just:

    just verify     # Full suite
    just clean      # Remove __pycache__ and .pyc files

## Structure

```
~/.hermes/plugins/subagent-output-guide/
├── plugin.yaml          # Plugin manifest (name, version, hooks)
├── __init__.py          # Plugin entry — register() + hook callbacks
├── AGENTS.md            # This file
├── tests/
│   ├── __init__.py
│   ├── test_tracker.py
│   ├── test_guidance.py
│   └── test_registration.py
├── pyproject.toml       # Project metadata, dependencies, tool config
├── justfile             # Task runner (verify, test, lint)
└── .gitignore
```

## Python toolchain

- **Python 3.12+** (same as Hermes)
- **uv** for package management (not pip)
- **ruff** for linting and formatting
- **`ty`** for static type checking
- **bandit** for security scanning
- **vulture** for dead code detection
- **pytest** for testing

## Workflow

All code changes must pass:

    uv run ruff check .          # Lint
    uv run ruff format --check . # Format check
    uv run bandit -r __init__.py tests/ -c pyproject.toml  # Security scan
    uv run vulture . .vulture_whitelist.py --exclude '.venv,dist,.git,__pycache__'  # Dead code
    uv run ty check . --exclude .vulture_whitelist.py  # Type check
    uv run pytest                # Unit tests

## Git conventions

- Branch name: `fix/`, `feat/`, `chore/` prefix
- Commit message format: `<type>: <short description>`
