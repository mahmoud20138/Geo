"""Plugin base classes and decorators for geo-agents."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
from langchain_core.tools import tool


@dataclass
class PluginInfo:
    """Metadata for a registered plugin tool."""

    name: str
    description: str
    func: Callable = field(repr=False)
    category: str = "Custom"
    source: str = ""  # file path where defined
    version: str = "1.0.0"
    enabled: bool = True


# Global plugin registry
_plugins: dict[str, PluginInfo] = {}


def register_tool(
    name: str,
    description: str,
    category: str = "Custom",
    version: str = "1.0.0",
) -> Callable:
    """Decorator to register a function as a plugin tool.

    Usage:
        @register_tool(name="my_tool", description="Does X", category="GIS")
        def my_tool(param: str) -> dict:
            return {"result": param}
    """

    def decorator(func: Callable) -> Callable:
        # Ensure function has a docstring (required by LangChain @tool)
        if not func.__doc__:
            func.__doc__ = description

        # Wrap with LangChain @tool for schema generation
        lc_tool = tool(func)
        lc_tool.name = name
        lc_tool.description = description

        info = PluginInfo(
            name=name,
            description=description,
            category=category,
            func=lc_tool,
            version=version,
        )
        _plugins[name] = info
        return func

    return decorator


def get_registered_plugins() -> dict[str, PluginInfo]:
    """Return all registered plugins."""
    return dict(_plugins)


def get_plugin_tools() -> list:
    """Return registered plugin tools as LangChain tool objects."""
    return [p.func for p in _plugins.values() if p.enabled]


def get_plugin_names() -> list[str]:
    """Return names of all registered plugins."""
    return [p.name for p in _plugins.values() if p.enabled]


def clear_plugins() -> None:
    """Clear all registered plugins (for testing)."""
    _plugins.clear()
