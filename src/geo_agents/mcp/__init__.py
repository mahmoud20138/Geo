"""MCP (Model Context Protocol) integration for geo-agents.

Connects to MCP servers and wraps their tools as LangChain tools.

Usage:
    from geo_agents.mcp import load_mcp_servers, get_mcp_tools

    load_mcp_servers("mcp_servers.json")
    tools = get_mcp_tools()
"""

from geo_agents.mcp.client import (
    load_mcp_servers,
    get_mcp_tools,
    get_mcp_servers,
    get_mcp_tool_names,
    clear_mcp,
    MCPServerConfig,
    MCPToolWrapper,
)

__all__ = [
    "load_mcp_servers",
    "get_mcp_tools",
    "get_mcp_servers",
    "get_mcp_tool_names",
    "clear_mcp",
    "MCPServerConfig",
    "MCPToolWrapper",
]
