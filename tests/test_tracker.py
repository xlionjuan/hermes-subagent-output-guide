"""Tests for child-session tracking (_on_subagent_start)."""

from __future__ import annotations

import importlib.util
import os
import threading

import pytest

# ---------------------------------------------------------------------------
# Load the plugin module from its __init__.py file path
# ---------------------------------------------------------------------------
_PLUGIN_PATH = os.path.expanduser("~/.hermes/plugins/subagent-output-guide/__init__.py")


@pytest.fixture(autouse=True)
def _plugin():
    """Import the plugin module and reset global state before each test."""
    spec = importlib.util.spec_from_file_location(
        "subagent_output_guide_tracker_test",
        _PLUGIN_PATH,
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Reset tracker state
    mod._child_sessions.clear()
    return mod


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSubagentStart:
    def test_adds_child_session_id(self, _plugin):
        """subagent_start adds the child_session_id to the set."""
        _plugin._on_subagent_start(child_session_id="session-abc")
        assert "session-abc" in _plugin._child_sessions

    def test_does_not_add_empty_id(self, _plugin):
        """A missing or empty child_session_id is NOT added."""
        _plugin._on_subagent_start(child_session_id=None)
        assert len(_plugin._child_sessions) == 0

        _plugin._on_subagent_start(child_session_id="")
        assert len(_plugin._child_sessions) == 0

    def test_multiple_child_sessions(self, _plugin):
        """Multiple distinct child sessions can be tracked concurrently."""
        ids = [f"session-{i}" for i in range(50)]
        for sid in ids:
            _plugin._on_subagent_start(child_session_id=sid)
        assert _plugin._child_sessions == set(ids)

    def test_thread_safety(self, _plugin):
        """Concurrent calls from multiple threads all register correctly."""
        ids = [f"thread-{i}" for i in range(100)]

        def _add(sid: str) -> None:
            _plugin._on_subagent_start(child_session_id=sid)

        threads = [threading.Thread(target=_add, args=(sid,)) for sid in ids]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert _plugin._child_sessions == set(ids)

    def test_additional_kwargs_ignored(self, _plugin):
        """Extra keyword arguments (child_role, child_goal, etc.) are accepted."""
        _plugin._on_subagent_start(
            child_session_id="session-xyz",
            child_role="researcher",
            child_goal="find the answer",
            extra_arg="ignored",
        )
        assert "session-xyz" in _plugin._child_sessions
