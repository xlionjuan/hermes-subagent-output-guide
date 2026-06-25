"""Tests for child-session tracking (_on_subagent_start)."""

from __future__ import annotations

import threading


class TestSubagentStart:
    def test_adds_child_session_id(self, plugin):
        """subagent_start adds the child_session_id to the set."""
        plugin._on_subagent_start(child_session_id="session-abc")
        assert "session-abc" in plugin._child_sessions

    def test_does_not_add_empty_id(self, plugin):
        """A missing or empty child_session_id is NOT added."""
        plugin._on_subagent_start(child_session_id=None)
        assert len(plugin._child_sessions) == 0

        plugin._on_subagent_start(child_session_id="")
        assert len(plugin._child_sessions) == 0

    def test_multiple_child_sessions(self, plugin):
        """Multiple distinct child sessions can be tracked concurrently."""
        ids = [f"session-{i}" for i in range(50)]
        for sid in ids:
            plugin._on_subagent_start(child_session_id=sid)
        assert plugin._child_sessions == set(ids)

    def test_thread_safety(self, plugin):
        """Concurrent calls from multiple threads all register correctly."""
        ids = [f"thread-{i}" for i in range(100)]

        def _add(sid: str) -> None:
            plugin._on_subagent_start(child_session_id=sid)

        threads = [threading.Thread(target=_add, args=(sid,)) for sid in ids]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert plugin._child_sessions == set(ids)

    def test_additional_kwargs_ignored(self, plugin):
        """Extra keyword arguments (child_role, child_goal, etc.) are accepted."""
        plugin._on_subagent_start(
            child_session_id="session-xyz",
            child_role="researcher",
            child_goal="find the answer",
            extra_arg="ignored",
        )
        assert "session-xyz" in plugin._child_sessions
