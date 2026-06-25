"""Tests for pre_llm_call output (_on_pre_llm_call)."""

from __future__ import annotations

from tests.conftest import make_child


class TestPreLlmCall:
    def test_returns_guidance_when_child_and_first_turn(self, plugin):
        """When the session IS a child AND first turn: returns guidance string."""
        make_child(plugin, "child-1")
        result = plugin._on_pre_llm_call(
            session_id="child-1",
            is_first_turn=True,
        )
        assert result is not None and len(result) > 0

    def test_returns_none_when_child_but_not_first_turn(self, plugin):
        """When the session IS a child but NOT first turn: returns None."""
        make_child(plugin, "child-1")
        assert (
            plugin._on_pre_llm_call(
                session_id="child-1",
                is_first_turn=False,
            )
            is None
        )

    def test_returns_none_when_not_a_child_first_turn(self, plugin):
        """When the session is NOT a child: returns None (even if first turn)."""
        assert (
            plugin._on_pre_llm_call(
                session_id="unknown-session",
                is_first_turn=True,
            )
            is None
        )

    def test_returns_none_for_empty_session_id(self, plugin):
        """An empty session_id always returns None."""
        make_child(plugin, "child-1")
        assert (
            plugin._on_pre_llm_call(
                session_id="",
                is_first_turn=True,
            )
            is None
        )

    def test_guidance_mentions_output_location(self, plugin):
        """The returned guidance mentions /tmp/ and output location concepts."""
        make_child(plugin, "child-1")
        result = plugin._on_pre_llm_call(
            session_id="child-1",
            is_first_turn=True,
        )
        assert "/tmp/" in result  # nosec - intentional: verifying guidance content
        assert "output" in result.lower()

    def test_guidance_has_boundary_markers(self, plugin):
        """The guidance has both <subagent-output-guide> and </subagent-output-guide> markers."""
        make_child(plugin, "child-1")
        result = plugin._on_pre_llm_call(
            session_id="child-1",
            is_first_turn=True,
        )
        assert "<subagent-output-guide>" in result
        assert "</subagent-output-guide>" in result
        assert result.index("<subagent-output-guide>") < result.index("</subagent-output-guide>")

    def test_guidance_not_returned_for_different_child(self, plugin):
        """Guidance is only returned for the registered child, not other sessions."""
        make_child(plugin, "child-1")
        assert (
            plugin._on_pre_llm_call(
                session_id="child-2",
                is_first_turn=True,
            )
            is None
        )

    def test_additional_kwargs_ignored(self, plugin):
        """Extra keyword arguments are accepted and don't affect logic."""
        make_child(plugin, "child-1")
        result = plugin._on_pre_llm_call(
            session_id="child-1",
            is_first_turn=True,
            extra_param="should be ignored",
        )
        assert result is not None and len(result) > 0

    def test_full_flow(self, plugin):
        """Integration: subagent_start + pre_llm_call chain works end-to-end."""
        # Simulate delegation: spawn child, then child's first turn
        child_id = "integration-test-session"
        plugin._on_subagent_start(child_session_id=child_id, child_role="researcher")
        result = plugin._on_pre_llm_call(
            session_id=child_id,
            is_first_turn=True,
        )
        assert result is not None
        assert "<subagent-output-guide>" in result
        assert "/tmp/" in result

        # Second turn should NOT inject again
        assert (
            plugin._on_pre_llm_call(
                session_id=child_id,
                is_first_turn=False,
            )
            is None
        )
