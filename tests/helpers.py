"""Test helpers for the subagent-output-guide test suite."""

from __future__ import annotations


def make_child(plugin, session_id: str = "child-1") -> None:
    """Register *session_id* as a known child session."""
    plugin._on_subagent_start(child_session_id=session_id)
