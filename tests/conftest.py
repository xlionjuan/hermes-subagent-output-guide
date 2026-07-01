"""Shared fixtures for the subagent-output-guide test suite."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_PLUGIN_PATH = str(Path(__file__).resolve().parent.parent / "__init__.py")


def _load_plugin(module_name: str):
    """Import the plugin module and return it with clean state.

    Registers the module in sys.modules so that ``@dataclass`` and other
    decorators that resolve string annotations (PEP 563) can find the
    module's namespace.
    """
    spec = importlib.util.spec_from_file_location(module_name, _PLUGIN_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def plugin():
    """Import the plugin module with clean state before each test."""
    return _load_plugin("subagent_output_guide_test")
