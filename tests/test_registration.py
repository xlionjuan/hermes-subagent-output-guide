"""Tests for register() — plugin registration with the context."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Load the plugin module
# ---------------------------------------------------------------------------
_PLUGIN_PATH = str(Path(__file__).resolve().parent.parent / "__init__.py")


@pytest.fixture(autouse=True)
def _plugin():
    spec = importlib.util.spec_from_file_location(
        "subagent_output_guide_reg_test",
        _PLUGIN_PATH,
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod._child_sessions.clear()
    return mod


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestRegister:
    def test_register_calls_register_hook_twice(self, _plugin):
        """register(ctx) calls ctx.register_hook exactly twice."""
        ctx = MagicMock()
        _plugin.register(ctx)
        assert ctx.register_hook.call_count == 2

    def test_register_subagent_start_hook(self, _plugin):
        """One of the registrations is for the 'subagent_start' hook."""
        ctx = MagicMock()
        _plugin.register(ctx)
        hook_names = [call.args[0] for call in ctx.register_hook.call_args_list]
        assert "subagent_start" in hook_names

    def test_register_pre_llm_call_hook(self, _plugin):
        """One of the registrations is for the 'pre_llm_call' hook."""
        ctx = MagicMock()
        _plugin.register(ctx)
        hook_names = [call.args[0] for call in ctx.register_hook.call_args_list]
        assert "pre_llm_call" in hook_names

    def test_register_with_correct_callbacks(self, _plugin):
        """The callbacks registered match the expected internal functions."""
        ctx = MagicMock()
        _plugin.register(ctx)

        call_1 = ctx.register_hook.call_args_list[0]
        call_2 = ctx.register_hook.call_args_list[1]

        names_and_funcs = {
            call_1.args[0]: call_1.args[1],
            call_2.args[0]: call_2.args[1],
        }

        assert names_and_funcs["subagent_start"] is _plugin._on_subagent_start
        assert names_and_funcs["pre_llm_call"] is _plugin._on_pre_llm_call
