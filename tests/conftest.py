"""Shared fixtures for the subagent-output-guide test suite."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_PLUGIN_PATH = str(Path(__file__).resolve().parent.parent / "__init__.py")


def _load_plugin(module_name: str):
    """Import the plugin module and return it with clean state."""
    spec = importlib.util.spec_from_file_location(module_name, _PLUGIN_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def plugin():
    """Import the plugin module with clean state before each test."""
    return _load_plugin("subagent_output_guide_test")


def make_child(plugin, session_id: str = "child-1") -> None:
    """Register *session_id* as a known child session."""
    plugin._on_subagent_start(child_session_id=session_id)
