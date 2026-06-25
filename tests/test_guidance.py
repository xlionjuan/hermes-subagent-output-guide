"""Tests for pre_llm_call output (_on_pre_llm_call)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Load the plugin module
# ---------------------------------------------------------------------------
_PLUGIN_PATH = str(Path(__file__).resolve().parent.parent / "__init__.py")


@pytest.fixture(autouse=True)
def _plugin():
    """Import the plugin module and reset global state before each test."""
    spec = importlib.util.spec_from_file_location(
        "subagent_output_guide_guidance_test",
        _PLUGIN_PATH,
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod._child_sessions.clear()
    return mod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_child(plugin, session_id: str = "child-1") -> None:
    """Register *session_id* as a known child session."""
    plugin._on_subagent_start(child_session_id=session_id)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPreLlmCall:
    def test_returns_guidance_when_child_and_first_turn(self, _plugin):
        """When the session IS a child AND first turn: returns guidance string."""
        _make_child(_plugin, "child-1")
        result = _plugin._on_pre_llm_call(
            session_id="child-1",
            is_first_turn=True,
        )
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_none_when_child_but_not_first_turn(self, _plugin):
        """When the session IS a child but NOT first turn: returns None."""
        _make_child(_plugin, "child-1")
        result = _plugin._on_pre_llm_call(
            session_id="child-1",
            is_first_turn=False,
        )
        assert result is None

    def test_returns_none_when_not_a_child_first_turn(self, _plugin):
        """When the session is NOT a child: returns None (even if first turn)."""
        result = _plugin._on_pre_llm_call(
            session_id="unknown-session",
            is_first_turn=True,
        )
        assert result is None

    def test_returns_none_when_not_a_child_not_first_turn(self, _plugin):
        """When the session is NOT a child and not first turn: returns None."""
        result = _plugin._on_pre_llm_call(
            session_id="unknown-session",
            is_first_turn=False,
        )
        assert result is None

    def test_returns_none_for_empty_session_id(self, _plugin):
        """An empty session_id always returns None."""
        _make_child(_plugin, "child-1")
        result = _plugin._on_pre_llm_call(
            session_id="",
            is_first_turn=True,
        )
        assert result is None

    def test_guidance_mentions_output_location(self, _plugin):
        """The returned guidance mentions /tmp/ and output location concepts."""
        _make_child(_plugin, "child-1")
        result = _plugin._on_pre_llm_call(
            session_id="child-1",
            is_first_turn=True,
        )
        assert "/tmp/" in result  # nosec - intentional: verifying guidance content
        assert "output" in result.lower()

    def test_guidance_has_boundary_markers(self, _plugin):
        """The guidance has both <subagent-output-guide> and </subagent-output-guide> markers."""
        _make_child(_plugin, "child-1")
        result = _plugin._on_pre_llm_call(
            session_id="child-1",
            is_first_turn=True,
        )
        assert "<subagent-output-guide>" in result
        assert "</subagent-output-guide>" in result
        assert result.index("<subagent-output-guide>") < result.index("</subagent-output-guide>")

    def test_guidance_is_non_empty(self, _plugin):
        """The returned string is non-empty."""
        _make_child(_plugin, "child-1")
        result = _plugin._on_pre_llm_call(
            session_id="child-1",
            is_first_turn=True,
        )
        assert result is not None
        assert len(result.strip()) > 0

    def test_guidance_not_returned_for_different_child(self, _plugin):
        """Guidance is only returned for the registered child, not other sessions."""
        _make_child(_plugin, "child-1")
        result = _plugin._on_pre_llm_call(
            session_id="child-2",
            is_first_turn=True,
        )
        assert result is None

    def test_additional_kwargs_ignored(self, _plugin):
        """Extra keyword arguments are accepted and don't affect logic."""
        _make_child(_plugin, "child-1")
        result = _plugin._on_pre_llm_call(
            session_id="child-1",
            is_first_turn=True,
            extra_param="should be ignored",
        )
        assert result is not None
        assert len(result) > 0
