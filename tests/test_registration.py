"""Tests for register() — plugin registration with the context."""

from __future__ import annotations

from unittest.mock import MagicMock


class TestRegister:
    def test_register_calls_register_hook_two_times(self, plugin):
        """register(ctx) calls ctx.register_hook exactly two times."""
        ctx = MagicMock()
        plugin.register(ctx)
        assert ctx.register_hook.call_count == 2

    def test_register_subagent_start_hook(self, plugin):
        """One of the registrations is for the 'subagent_start' hook."""
        ctx = MagicMock()
        plugin.register(ctx)
        hook_names = [call.args[0] for call in ctx.register_hook.call_args_list]
        assert "subagent_start" in hook_names

    def test_register_pre_llm_call_hook(self, plugin):
        """One of the registrations is for the 'pre_llm_call' hook."""
        ctx = MagicMock()
        plugin.register(ctx)
        hook_names = [call.args[0] for call in ctx.register_hook.call_args_list]
        assert "pre_llm_call" in hook_names

    def test_register_with_correct_callbacks(self, plugin):
        """The callbacks registered match the expected internal functions."""
        ctx = MagicMock()
        plugin.register(ctx)
        names_and_funcs = {call.args[0]: call.args[1] for call in ctx.register_hook.call_args_list}
        assert names_and_funcs["subagent_start"] is plugin._on_subagent_start
        assert names_and_funcs["pre_llm_call"] is plugin._on_pre_llm_call
