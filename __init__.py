"""subagent-output-guide plugin — injects text-report delivery guidance into subagents.

Wires three hooks:

1. ``subagent_start`` — records ``child_session_id`` (with parent relationship)
   as a child-agent session so subsequent ``pre_llm_call`` invocations can
   recognise it.
2. ``pre_llm_call`` — when the current session is a child agent on its first
   turn, returns a context block that keeps concise reports in the response
   and saves long text reports under ``/tmp/`` when no location is specified.
3. ``on_session_end`` — cleans up the tracked child session when it ends and
   performs cascade cleanup: if the ending session is a parent, all its
   descendants are removed as well (recursive BFS walk).
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ChildInfo dataclass — metadata for a child (subagent) session.
# ---------------------------------------------------------------------------


@dataclass
class ChildInfo:
    """Metadata about a child (subagent) session and its parent relationship."""

    parent_session_id: str
    parent_turn_id: str
    child_session_id: str
    child_role: str | None = None
    child_goal: str = ""


# ---------------------------------------------------------------------------
# Global state: child_session_id → ChildInfo mapping.
# Dict instead of set so we can track parent→children relationships and
# cascade-cleanup when a parent session ends.
# Thread-safe because subagent_start and pre_llm_call can fire concurrently.
# ---------------------------------------------------------------------------
_child_sessions: dict[str, ChildInfo] = {}
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------


def _on_subagent_start(
    child_session_id: str | None = None,
    child_role: str | None = None,
    child_goal: str = "",
    parent_session_id: str | None = None,
    parent_turn_id: str = "",
    **_: Any,
) -> None:
    """Record ``child_session_id`` (with parent relation) as a child-agent session."""
    if child_session_id:
        with _lock:
            _child_sessions[child_session_id] = ChildInfo(
                parent_session_id=parent_session_id or "",
                parent_turn_id=parent_turn_id,
                child_session_id=child_session_id,
                child_role=child_role,
                child_goal=child_goal,
            )
        logger.debug(
            "subagent-output-guide: tracking child session %s (role=%s, parent=%s)",
            child_session_id,
            child_role,
            parent_session_id,
        )


def _on_session_end(
    session_id: str = "",
    **_: Any,
) -> None:
    """Clean up child session tracking when a session ends.

    Performs recursive cascade cleanup via BFS walk: if the ending session
    has descendants (children, grandchildren, etc.), they are all removed.
    """
    if not session_id:
        return
    with _lock:
        removed = {session_id}
        frontier = [session_id]
        while frontier:
            direct = [
                cid for cid, info in _child_sessions.items() if info.parent_session_id in frontier
            ]
            removed.update(direct)
            frontier = direct
        for sid in removed:
            _child_sessions.pop(sid, None)


def _on_pre_llm_call(
    session_id: str = "",
    is_first_turn: bool = False,
    **_: Any,
) -> str | None:
    """Inject text-report delivery guidance on the child's first turn.

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
        "## Text Report Delivery\n"
        "\n"
        "This guidance applies only to text reports. It does not apply "
        "to source code, tests, project documentation, scripts, data, "
        "logs, build outputs, or any other non-report files.\n"
        "\n"
        "Follow any explicit delivery instructions in the delegated task.\n"
        "\n"
        "- For a concise report, respond directly unless the task "
        "requests a file.\n"
        "- If the report would make the final response long, proactively "
        "save the detailed report to a text file instead of placing most "
        "of it in the final response.\n"
        "- Use the report location specified by the delegated task. If "
        "none is specified, save the report under ``/tmp/``.\n"
        "- When a report file is created, keep the final response concise "
        "and include the key findings, decisions, or next steps together "
        "with the report's absolute path.\n"
        "\n"
        "</subagent-output-guide>\n"
    )


# ---------------------------------------------------------------------------
# Plugin registration
# ---------------------------------------------------------------------------


def register(ctx: Any) -> None:
    ctx.register_hook("subagent_start", _on_subagent_start)
    ctx.register_hook("on_session_end", _on_session_end)
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)
