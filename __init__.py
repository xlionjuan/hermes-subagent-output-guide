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
        "Parent task instructions take priority. Use this only as a "
        "fallback when the parent does not specify output details. "
        "If you create files, use the parent-specified path when given; "
        "otherwise use /tmp/. Use descriptive filenames and mention "
        "created file paths in your response. For large reports, write "
        "the full content to /tmp/; do not include the full report in "
        "the response. For temporary artifacts (coverage, logs, scripts, "
        "tables, generated data, debug output, etc.), save them under "
        "/tmp/ when useful. Reply with the key findings, decisions, or "
        "next steps, plus the file paths. If the task needs substantial "
        "output but you lack file tools, say so neutrally so the parent "
        "can add them next time for review.\n"
        "</subagent-output-guide>\n"
    )


# ---------------------------------------------------------------------------
# Plugin registration
# ---------------------------------------------------------------------------


def register(ctx: Any) -> None:
    ctx.register_hook("subagent_start", _on_subagent_start)
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)
