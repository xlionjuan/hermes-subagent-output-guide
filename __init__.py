"""
subagent-output-guide plugin — injects output-location guidance into subagents.

Wires two hooks:

1. ``subagent_start`` — records ``child_session_id`` as a child-agent session
   so subsequent ``pre_llm_call`` invocations can recognise it.
2. ``pre_llm_call`` — when the current session is a child agent on its first
   turn, returns a context block telling it to write output files to ``/tmp/``
   when the task doesn't specify a location.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global state: set of session IDs known to be child (subagent) sessions.
# Thread-safe because subagent_start and pre_llm_call can fire concurrently.
# ---------------------------------------------------------------------------
_child_sessions: set[str] = set()
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------


def _on_subagent_start(
    child_session_id: str | None = None,
    child_role: str | None = None,
    child_goal: str = "",
    **_: Any,
) -> None:
    """Record ``child_session_id`` as a child-agent session."""
    if child_session_id:
        with _lock:
            _child_sessions.add(child_session_id)
        logger.debug(
            "subagent-output-guide: tracking child session %s (role=%s)",
            child_session_id,
            child_role,
        )


def _on_session_end(
    session_id: str = "",
    **_: Any,
) -> None:
    """Clean up child session tracking when a session ends."""
    if session_id:
        with _lock:
            _child_sessions.discard(session_id)


def _on_pre_llm_call(
    session_id: str = "",
    is_first_turn: bool = False,
    **_: Any,
) -> str | None:
    """Inject output-location guidance on the child's first turn.

    Returns a plain-string context block that gets appended to the current
    user message (never touches the system prompt — preserves prompt cache).
    Only injects on the first turn to keep token overhead minimal.
    """
    if not session_id:
        return None

    with _lock:
        is_child = session_id in _child_sessions

    if not is_child or not is_first_turn:
        return None

    logger.debug(
        "subagent-output-guide: injecting guidance into child session %s",
        session_id,
    )
    return (
        "<subagent-output-guide>\n"
        "\n"
        "## File Output Location\n"
        "\n"
        "This guidance only applies if your delegated task requires you "
        "to create output files. It does not require you to create a "
        "file. If the task can be completed by replying in chat, reply "
        "in chat.\n"
        "\n"
        "If you do create output files:\n"
        "\n"
        "- If the task **explicitly specifies** an output location, use "
        "that location.\n"
        "- If **no output location is specified**, write output files "
        "to ``/tmp/``.\n"
        "- Do not write output files to the home directory, project "
        "root, or other locations unless explicitly directed.\n"
        "\n"
        "</subagent-output-guide>\n"
    )


# ---------------------------------------------------------------------------
# Plugin registration
# ---------------------------------------------------------------------------


def register(ctx) -> None:
    ctx.register_hook("subagent_start", _on_subagent_start)
    ctx.register_hook("on_session_end", _on_session_end)
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)
