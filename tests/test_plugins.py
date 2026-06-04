"""Tests for the plugin system."""

import pytest
from geo_agents.plugins.base import (
    register_tool,
    get_registered_plugins,
    get_plugin_tools,
    get_plugin_names,
    clear_plugins,
    PluginInfo,
)
from geo_agents.plugins.loader import discover_plugins, reload_plugins, _load_module


@pytest.fixture(autouse=True)
def clean_plugins():
    """Clear plugins before and after each test."""
    clear_plugins()
    yield
    clear_plugins()


def test_register_tool_decorator():
    """@register_tool registers a function as a plugin."""

    @register_tool(name="test_tool", description="A test tool", category="Test")
    def test_tool(x: str) -> dict:
        return {"result": x}

    plugins = get_registered_plugins()
    assert "test_tool" in plugins
    assert plugins["test_tool"].description == "A test tool"
    assert plugins["test_tool"].category == "Test"


def test_register_tool_creates_langchain_tool():
    """@register_tool creates a LangChain-compatible tool."""

    @register_tool(name="lc_tool", description="LangChain tool", category="Test")
    def lc_tool(param: str) -> dict:
        return {"param": param}

    tools = get_plugin_tools()
    assert len(tools) == 1
    assert tools[0].name == "lc_tool"


def test_get_plugin_names():
    """get_plugin_names returns names of registered plugins."""

    @register_tool(name="tool_a", description="A", category="X")
    def tool_a() -> dict:
        return {}

    @register_tool(name="tool_b", description="B", category="Y")
    def tool_b() -> dict:
        return {}

    names = get_plugin_names()
    assert "tool_a" in names
    assert "tool_b" in names
    assert len(names) == 2


def test_clear_plugins():
    """clear_plugins removes all registered plugins."""

    @register_tool(name="temp_tool", description="Temporary", category="Test")
    def temp_tool() -> dict:
        return {}

    assert len(get_registered_plugins()) == 1
    clear_plugins()
    assert len(get_registered_plugins()) == 0


def test_plugin_info_fields():
    """PluginInfo stores all metadata correctly."""

    @register_tool(
        name="info_tool",
        description="Has info",
        category="GIS",
        version="2.0.0",
    )
    def info_tool() -> dict:
        return {}

    info = get_registered_plugins()["info_tool"]
    assert info.name == "info_tool"
    assert info.description == "Has info"
    assert info.category == "GIS"
    assert info.version == "2.0.0"
    assert info.enabled is True


def test_reload_plugins():
    """reload_plugins clears and reloads from directories."""
    result = reload_plugins(["plugins"])
    assert "plugins" in result
    assert "count" in result
    assert isinstance(result["plugins"], list)


def test_discover_plugins_nonexistent_dir():
    """discover_plugins handles nonexistent directories gracefully."""
    loaded = discover_plugins(["nonexistent_dir_xyz"])
    assert loaded == []


def test_load_module(tmp_path):
    """_load_module loads a Python file as a module."""
    plugin_file = tmp_path / "test_mod.py"
    plugin_file.write_text('X = 42\n')

    _load_module("test_mod_tmp", plugin_file)
    import sys
    assert sys.modules["test_mod_tmp"].X == 42
    del sys.modules["test_mod_tmp"]
