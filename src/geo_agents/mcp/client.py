"""MCP client for connecting to MCP servers and wrapping their tools."""

from __future__ import annotations
import json
import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from langchain_core.tools import tool


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""

    name: str
    transport: str  # "stdio" or "sse"
    command: str = ""
    args: list[str] = field(default_factory=list)
    url: str = ""
    env: dict[str, str] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class MCPToolWrapper:
    """Wraps an MCP tool as a LangChain-compatible tool."""

    name: str
    description: str
    server_name: str
    input_schema: dict = field(default_factory=dict)
    _lc_tool: Any = field(repr=False, default=None)

    def as_langchain_tool(self) -> Any:
        """Convert to a LangChain tool object."""
        if self._lc_tool is not None:
            return self._lc_tool

        schema = self.input_schema
        tool_name = self.name
        tool_desc = self.description
        server = self.server_name

        # Create a closure that captures the tool info
        def make_tool_func(tname, tdesc, tserver, tschema):
            async def tool_func(**kwargs) -> dict:
                return {
                    "tool": tname,
                    "server": tserver,
                    "args": kwargs,
                    "result": f"[MCP:{tserver}] {tname} called with {kwargs}",
                    "note": "MCP tool execution requires a running MCP server connection",
                }

            tool_func.__name__ = tname
            tool_func.__doc__ = tdesc
            return tool_func

        func = make_tool_func(tool_name, tool_desc, server, schema)
        lc_tool = tool(func)
        lc_tool.name = tool_name
        lc_tool.description = f"[MCP:{server}] {tool_desc}"
        self._lc_tool = lc_tool
        return lc_tool


# Global state
_servers: dict[str, MCPServerConfig] = {}
_tools: dict[str, MCPToolWrapper] = {}


def load_mcp_servers(config_path: str = "mcp_servers.json") -> dict:
    """Load MCP server configurations from a JSON file.

    Args:
        config_path: Path to the MCP servers config file.

    Returns:
        Dict with loaded server count and names.
    """
    path = Path(config_path)
    if not path.exists():
        return {"servers": [], "tools": [], "note": f"Config file not found: {config_path}"}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    servers = data.get("servers", [])
    loaded_servers = []
    loaded_tools = []

    for srv in servers:
        config = MCPServerConfig(
            name=srv["name"],
            transport=srv.get("transport", "stdio"),
            command=srv.get("command", ""),
            args=srv.get("args", []),
            url=srv.get("url", ""),
            env=srv.get("env", {}),
            enabled=srv.get("enabled", True),
        )
        _servers[config.name] = config

        # Register declared tools from config
        for tool_def in srv.get("tools", []):
            wrapper = MCPToolWrapper(
                name=tool_def["name"],
                description=tool_def.get("description", f"MCP tool from {config.name}"),
                server_name=config.name,
                input_schema=tool_def.get("input_schema", {}),
            )
            _tools[wrapper.name] = wrapper
            loaded_tools.append(wrapper.name)

        loaded_servers.append(config.name)

    return {
        "servers": loaded_servers,
        "tools": loaded_tools,
        "count": len(loaded_servers),
    }


def get_mcp_tools() -> list:
    """Return MCP tools as LangChain tool objects."""
    return [w.as_langchain_tool() for w in _tools.values()]


def get_mcp_tool_names() -> list[str]:
    """Return names of all MCP tools."""
    return list(_tools.keys())


def get_mcp_servers() -> dict[str, MCPServerConfig]:
    """Return all configured MCP servers."""
    return dict(_servers)


def clear_mcp() -> None:
    """Clear all MCP state (for testing)."""
    _servers.clear()
    _tools.clear()
