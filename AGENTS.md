# subagent-output-guide

A Hermes user plugin that automatically injects output-location guidance into
subagent prompts, preventing subagents from writing files to arbitrary locations
when the parent agent (玖璃) forgets to specify an output path.

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

Run before every commit:

    uv run ruff check .
    uv run ruff format --check .
    uv run ty src/ tests/
    uv run pytest

Or via just:

    just verify

## Structure

```
~/.hermes/plugins/subagent-output-guide/
├── plugin.yaml          # Plugin manifest (name, version, hooks)
├── __init__.py          # Plugin entry — register() + hook callbacks
├── AGENTS.md            # This file
├── src/
│   └── subagent_output_guide/
│       ├── __init__.py
│       ├── tracker.py   # Child-session tracking
│       └── guidance.py  # Context-building for the injected guidance
├── tests/
│   ├── __init__.py
│   ├── test_tracker.py
│   └── test_guidance.py
├── pyproject.toml       # Project metadata, dependencies, tool config
└── justfile             # Task runner (verify, test, lint)
```

## Python toolchain

- **Python 3.12+** (same as Hermes)
- **uv** for package management (not pip)
- **ruff** for linting and formatting
- **`ty`** for static type checking
- **pytest** for testing

## Workflow

All code changes must pass:

    ruff check .          # Lint
    ruff format --check . # Format check
    ty src/ tests/        # Type check
    pytest                # Unit tests

## Git conventions

- Branch name: `fix/`, `feat/`, `chore/` prefix
- Commit message format: `<type>: <short description>`
