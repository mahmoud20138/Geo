"""Geo-Agents: Multi-agent orchestration SDK for geospatial digital twin platforms.

A LangGraph-based multi-agent system with pluggable tools, skills, and MCP server support.

Usage:
    # As SDK (programmatic)
    from geo_agents import GeoAgentsSDK
    sdk = GeoAgentsSDK()
    result = await sdk.run("Check weather for drone flight")

    # As API server
    uvicorn geo_agents.main:app

    # As CLI
    python -m geo_agents.main
"""

__version__ = "0.2.0"

from geo_agents.client import GeoAgentsSDK
from geo_agents.config import Settings, settings
from geo_agents.state import AgentState, create_initial_state
from geo_agents.graph import agent_graph, build_graph
from geo_agents.exceptions import (
    GeoAgentsError,
    ProviderError,
    ToolExecutionError,
    PluginLoadError,
    SkillNotFoundError,
    MCPConnectionError,
    MaxIterationsError,
    GraphBuildError,
    ConfigValidationError,
)

__all__ = [
    "GeoAgentsSDK",
    "Settings",
    "settings",
    "AgentState",
    "create_initial_state",
    "agent_graph",
    "build_graph",
    "GeoAgentsError",
    "ProviderError",
    "ToolExecutionError",
    "PluginLoadError",
    "SkillNotFoundError",
    "MCPConnectionError",
    "MaxIterationsError",
    "GraphBuildError",
    "ConfigValidationError",
    "__version__",
]
