"""Tests for the MCP integration."""

import json
import pytest
from pathlib import Path
from geo_agents.mcp.client import (
    load_mcp_servers,
    get_mcp_tools,
    get_mcp_servers,
    get_mcp_tool_names,
    clear_mcp,
    MCPServerConfig,
    MCPToolWrapper,
)


@pytest.fixture(autouse=True)
def clean_mcp():
    """Clear MCP state before and after each test."""
    clear_mcp()
    yield
    clear_mcp()


@pytest.fixture
def mcp_config_file(tmp_path):
    """Create a temporary MCP config file."""
    config = {
        "servers": [
            {
                "name": "test-server",
                "transport": "stdio",
                "command": "echo",
                "args": ["hello"],
                "enabled": True,
                "tools": [
                    {
                        "name": "test_tool_1",
                        "description": "First test tool",
                        "input_schema": {
                            "type": "object",
                            "properties": {"param": {"type": "string"}},
                            "required": ["param"],
                        },
                    },
                    {
                        "name": "test_tool_2",
                        "description": "Second test tool",
                    },
                ],
            },
            {
                "name": "sse-server",
                "transport": "sse",
                "url": "http://localhost:3001/sse",
                "enabled": False,
                "tools": [
                    {"name": "sse_tool", "description": "An SSE tool"},
                ],
            },
        ]
    }
    path = tmp_path / "mcp.json"
    path.write_text(json.dumps(config))
    return str(path)


def test_load_mcp_servers(mcp_config_file):
    """load_mcp_servers reads config and registers servers."""
    result = load_mcp_servers(mcp_config_file)
    assert result["count"] == 2
    assert "test-server" in result["servers"]
    assert "sse-server" in result["servers"]


def test_load_mcp_registers_tools(mcp_config_file):
    """load_mcp_servers registers tools from config."""
    load_mcp_servers(mcp_config_file)
    names = get_mcp_tool_names()
    assert "test_tool_1" in names
    assert "test_tool_2" in names
    assert "sse_tool" in names


def test_get_mcp_tools_as_langchain(mcp_config_file):
    """get_mcp_tools returns LangChain-compatible tool objects."""
    load_mcp_servers(mcp_config_file)
    tools = get_mcp_tools()
    assert len(tools) == 3
    names = [t.name for t in tools]
    assert "test_tool_1" in names


def test_get_mcp_servers(mcp_config_file):
    """get_mcp_servers returns server configs."""
    load_mcp_servers(mcp_config_file)
    servers = get_mcp_servers()
    assert "test-server" in servers
    assert servers["test-server"].transport == "stdio"
    assert servers["sse-server"].transport == "sse"


def test_load_nonexistent_config():
    """load_mcp_servers handles missing config file."""
    result = load_mcp_servers("nonexistent_mcp.json")
    assert result["servers"] == []
    assert "note" in result


def test_clear_mcp(mcp_config_file):
    """clear_mcp removes all state."""
    load_mcp_servers(mcp_config_file)
    assert len(get_mcp_tool_names()) > 0
    clear_mcp()
    assert len(get_mcp_tool_names()) == 0
    assert len(get_mcp_servers()) == 0


def test_mcp_tool_wrapper():
    """MCPToolWrapper creates a LangChain tool."""
    wrapper = MCPToolWrapper(
        name="wrapper_tool",
        description="A wrapped tool",
        server_name="test",
        input_schema={"type": "object", "properties": {}},
    )
    lc_tool = wrapper.as_langchain_tool()
    assert lc_tool.name == "wrapper_tool"
    assert "test" in lc_tool.description


def test_mcp_tool_wrapper_idempotent():
    """as_langchain_tool returns the same object on repeated calls."""
    wrapper = MCPToolWrapper(
        name="idempotent_tool",
        description="Test",
        server_name="test",
    )
    tool1 = wrapper.as_langchain_tool()
    tool2 = wrapper.as_langchain_tool()
    assert tool1 is tool2
