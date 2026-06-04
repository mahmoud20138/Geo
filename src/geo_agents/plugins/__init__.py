"""Plugin system for geo-agents.

Provides dynamic tool registration and discovery. Plugins are Python files
placed in a plugins/ directory that use @register_tool to expose tools.

Usage:
    from geo_agents.plugins.base import register_tool

    @register_tool(name="my_tool", description="...", category="Custom")
    def my_tool(param: str) -> dict:
        return {"result": param}
"""

from geo_agents.plugins.base import (
    register_tool,
    get_registered_plugins,
    get_plugin_tools,
    get_plugin_names,
    clear_plugins,
    PluginInfo,
)
from geo_agents.plugins.loader import discover_plugins, reload_plugins

__all__ = [
    "register_tool",
    "get_registered_plugins",
    "get_plugin_tools",
    "get_plugin_names",
    "clear_plugins",
    "PluginInfo",
    "discover_plugins",
    "reload_plugins",
]
