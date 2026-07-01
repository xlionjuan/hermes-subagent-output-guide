"""Tests for child-session tracking (_on_subagent_start)."""

from __future__ import annotations

import threading


class TestSubagentStart:
    def test_adds_child_session_id(self, plugin):
        """subagent_start adds the child_session_id as a dict key."""
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
        assert set(plugin._child_sessions) == set(ids)

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

        assert set(plugin._child_sessions) == set(ids)

    def test_additional_kwargs_ignored(self, plugin):
        """Extra keyword arguments (child_role, child_goal, etc.) are accepted."""
        plugin._on_subagent_start(
            child_session_id="session-xyz",
            child_role="researcher",
            child_goal="find the answer",
            extra_arg="ignored",
        )
        assert "session-xyz" in plugin._child_sessions

    def test_stores_child_info_with_parent_relation(self, plugin):
        """The stored ChildInfo contains the parent relationship metadata."""
        plugin._on_subagent_start(
            child_session_id="child-1",
            child_role="researcher",
            child_goal="find answer",
            parent_session_id="parent-42",
            parent_turn_id="turn-1",
        )
        info = plugin._child_sessions["child-1"]
        assert info.parent_session_id == "parent-42"
        assert info.parent_turn_id == "turn-1"
        assert info.child_session_id == "child-1"
        assert info.child_role == "researcher"
        assert info.child_goal == "find answer"

    def test_stores_child_info_with_defaults(self, plugin):
        """When parent_session_id and parent_turn_id are omitted, defaults are stored."""
        plugin._on_subagent_start(child_session_id="child-default")
        info = plugin._child_sessions["child-default"]
        assert info.parent_session_id == ""
        assert info.parent_turn_id == ""
        assert info.child_session_id == "child-default"
        assert info.child_role is None
        assert info.child_goal == ""


class TestConcurrency:
    """Stress tests for concurrent access to _child_sessions."""

    def test_concurrent_subagent_start_and_pre_llm_call(self, plugin):
        """Concurrent registration and reads do not lose data."""
        ids = [f"stress-{i}" for i in range(50)]
        errors: list[Exception | None] = [None] * len(ids)

        def register_then_read(idx: int) -> None:
            try:
                sid = ids[idx]
                plugin._on_subagent_start(child_session_id=sid)
                # Immediately try to read it back
                result = plugin._on_pre_llm_call(session_id=sid, is_first_turn=True)
                assert result is not None
                assert "/tmp/" in result  # nosec B108
            except Exception as e:
                errors[idx] = e

        threads = [threading.Thread(target=register_then_read, args=(i,)) for i in range(len(ids))]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        failures = [(i, e) for i, e in enumerate(errors) if e is not None]
        assert not failures, f"Concurrent read/write failures: {failures}"

    def test_concurrent_subagent_start_and_session_end(self, plugin):
        """Concurrent add+remove of distinct IDs: _child_sessions ends empty
        and pre_llm_call returns None for all previously-removed IDs."""
        ids = [f"addrm-{i}" for i in range(50)]
        errors: list[Exception | None] = [None] * len(ids)

        def add_then_remove(idx: int) -> None:
            try:
                sid = ids[idx]
                # Add the session (subagent_start)
                plugin._on_subagent_start(child_session_id=sid)
                # Immediately remove it (on_session_end)
                plugin._on_session_end(session_id=sid)
                # After removal, pre_llm_call must return None
                assert plugin._on_pre_llm_call(session_id=sid, is_first_turn=True) is None
            except Exception as e:
                errors[idx] = e

        threads = [threading.Thread(target=add_then_remove, args=(i,)) for i in range(len(ids))]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        failures = [(i, e) for i, e in enumerate(errors) if e is not None]
        assert not failures, f"Concurrent add/remove failures: {failures}"
        # All IDs must have been removed
        assert len(plugin._child_sessions) == 0

    def test_concurrent_session_end_on_same_id(self, plugin):
        """Multiple threads calling on_session_end on the same ID must not
        crash — pop is idempotent under the lock."""
        sid = "contested-session"
        # Register it once
        plugin._on_subagent_start(child_session_id=sid)
        assert sid in plugin._child_sessions

        errors: list[Exception | None] = [None] * 20

        def remove_same_id(idx: int) -> None:
            try:
                plugin._on_session_end(session_id=sid)
            except Exception as e:
                errors[idx] = e

        threads = [threading.Thread(target=remove_same_id, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        failures = [(i, e) for i, e in enumerate(errors) if e is not None]
        assert not failures, f"Concurrent pop on same ID crashed: {failures}"
        # After all threads, the ID must be gone (pop succeeded)
        assert sid not in plugin._child_sessions


class TestSessionEnd:
    def test_on_session_end_removes_child_id(self, plugin):
        """on_session_end removes the session_id from _child_sessions."""
        plugin._on_subagent_start(child_session_id="session-to-clean")
        assert "session-to-clean" in plugin._child_sessions
        plugin._on_session_end(session_id="session-to-clean")
        assert "session-to-clean" not in plugin._child_sessions

    def test_on_session_end_noop_for_unknown_id(self, plugin):
        """on_session_end does nothing for an untracked session_id."""
        plugin._on_session_end(session_id="never-tracked")
        assert len(plugin._child_sessions) == 0

    def test_on_session_end_empty_string_noop(self, plugin):
        """on_session_end(session_id="") is a no-op — does not remove
        any registered child session because the guard ``if session_id:``
        prevents an empty string from entering the critical section."""
        # Register a real child session first
        plugin._on_subagent_start(child_session_id="real-child")
        assert "real-child" in plugin._child_sessions
        # Calling on_session_end with an empty string must NOT remove it
        plugin._on_session_end(session_id="")
        assert "real-child" in plugin._child_sessions


class TestCascadeCleanup:
    """Tests for cascade cleanup: when a parent session ends, its children
    are automatically removed from tracking."""

    def test_cascade_removes_direct_children(self, plugin):
        """When a parent session ends, all its direct children are cleaned up."""
        plugin._on_subagent_start(
            child_session_id="child-1",
            parent_session_id="parent-session",
        )
        plugin._on_subagent_start(
            child_session_id="child-2",
            parent_session_id="parent-session",
        )
        plugin._on_subagent_start(
            child_session_id="other-child",
            parent_session_id="other-parent",
        )
        assert "child-1" in plugin._child_sessions
        assert "child-2" in plugin._child_sessions
        assert "other-child" in plugin._child_sessions

        # End the parent session — triggers cascade
        plugin._on_session_end(session_id="parent-session")

        assert "child-1" not in plugin._child_sessions
        assert "child-2" not in plugin._child_sessions
        # Unrelated child is untouched
        assert "other-child" in plugin._child_sessions

    def test_cascade_also_removes_parent_itself_if_child(self, plugin):
        """If the ending session is both a child of another session AND a parent,
        it is removed along with its own children."""
        # Grandparent → parent → child chain; all three registered
        plugin._on_subagent_start(
            child_session_id="grandparent-session",
        )
        plugin._on_subagent_start(
            child_session_id="parent-session",
            parent_session_id="grandparent-session",
        )
        plugin._on_subagent_start(
            child_session_id="child-session",
            parent_session_id="parent-session",
        )
        assert "grandparent-session" in plugin._child_sessions
        assert "parent-session" in plugin._child_sessions
        assert "child-session" in plugin._child_sessions

        # End parent — removes parent itself AND child; grandparent untouched
        plugin._on_session_end(session_id="parent-session")

        assert "parent-session" not in plugin._child_sessions
        assert "child-session" not in plugin._child_sessions
        # Grandparent still tracked
        assert "grandparent-session" in plugin._child_sessions

    def test_cascade_noop_for_session_with_no_children(self, plugin):
        """Ending a session that is not a parent does not affect other sessions."""
        plugin._on_subagent_start(
            child_session_id="child-1",
            parent_session_id="parent-session",
        )
        plugin._on_subagent_start(
            child_session_id="child-2",
            parent_session_id="parent-session",
        )
        # End an unrelated session with no children
        plugin._on_session_end(session_id="unrelated-session")
        # All existing children remain
        assert "child-1" in plugin._child_sessions
        assert "child-2" in plugin._child_sessions

    def test_cascade_empty_parent_session_id(self, plugin):
        """Empty session_id guard still works — no cascade for empty string."""
        plugin._on_subagent_start(
            child_session_id="child-1",
            parent_session_id="parent-session",
        )
        plugin._on_session_end(session_id="")
        assert "child-1" in plugin._child_sessions

    def test_cascade_preserves_pre_llm_call_for_remaining_children(self, plugin):
        """Cascade-cleanup ensures surviving children still receive guidance."""
        plugin._on_subagent_start(
            child_session_id="child-to-keep",
            parent_session_id="parent-a",
        )
        plugin._on_subagent_start(
            child_session_id="child-to-clean",
            parent_session_id="parent-b",
        )
        # End parent-b — removes child-to-clean
        plugin._on_session_end(session_id="parent-b")

        assert "child-to-keep" in plugin._child_sessions
        assert plugin._on_pre_llm_call(session_id="child-to-keep", is_first_turn=True) is not None
        assert plugin._on_pre_llm_call(session_id="child-to-clean", is_first_turn=True) is None
