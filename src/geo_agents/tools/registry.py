"""Central tool registry — merges core tools, plugins, MCP tools, and skill tools."""

from geo_agents.tools.gis import query_geojson, get_satellite_imagery, calculate_area
from geo_agents.tools.database import query_postgres, query_timeseries
from geo_agents.tools.sensors import get_telemetry, get_gps_data
from geo_agents.tools.external import weather_api, traffic_api


def _get_core_tools() -> list:
    """Return built-in tools."""
    return [
        query_geojson,
        get_satellite_imagery,
        calculate_area,
        query_postgres,
        query_timeseries,
        get_telemetry,
        get_gps_data,
        weather_api,
        traffic_api,
    ]


def _get_plugin_tools() -> list:
    """Return tools from loaded plugins."""
    try:
        from geo_agents.plugins.base import get_plugin_tools
        return get_plugin_tools()
    except Exception:
        return []


def _get_mcp_tools() -> list:
    """Return tools from MCP servers."""
    try:
        from geo_agents.mcp.client import get_mcp_tools
        return get_mcp_tools()
    except Exception:
        return []


def _get_rag_tools() -> list:
    """Return RAG tools if available."""
    try:
        from geo_agents.rag import RAGEngine
        rag = RAGEngine()
        return rag.as_tools()
    except Exception:
        return []


def get_all_tools(include_rag: bool = True) -> list:
    """Return all available tools from all sources.

    Merges: core tools + plugin tools + MCP tools + RAG tools.
    Deduplicates by tool name (first wins).
    """
    seen = set()
    tools = []

    sources = [_get_core_tools(), _get_plugin_tools(), _get_mcp_tools()]
    if include_rag:
        sources.append(_get_rag_tools())

    for source_tools in sources:
        for t in source_tools:
            if t.name not in seen:
                seen.add(t.name)
                tools.append(t)

    return tools


def get_tool_names() -> list[str]:
    """Return names of all available tools."""
    return [t.name for t in get_all_tools()]


def get_tools_by_category() -> dict[str, list[dict]]:
    """Return tools grouped by category with metadata."""
    categories: dict[str, list[dict]] = {}

    # Core tools by file
    core_map = {
        "GIS": [query_geojson, get_satellite_imagery, calculate_area],
        "Database": [query_postgres, query_timeseries],
        "Sensors": [get_telemetry, get_gps_data],
        "External": [weather_api, traffic_api],
    }

    for cat, tools in core_map.items():
        categories[cat] = [
            {"name": t.name, "description": t.description.split("\n")[0], "source": "core"}
            for t in tools
        ]

    # Plugin tools
    try:
        from geo_agents.plugins.base import get_registered_plugins
        for name, info in get_registered_plugins().items():
            cat = info.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "name": info.name,
                "description": info.description,
                "source": "plugin",
                "version": info.version,
            })
    except Exception:
        pass

    # MCP tools
    try:
        from geo_agents.mcp.client import get_mcp_servers, get_mcp_tool_names
        servers = get_mcp_servers()
        mcp_tools = get_mcp_tool_names()
        if mcp_tools:
            categories["MCP"] = [
                {"name": n, "description": f"MCP tool", "source": "mcp"}
                for n in mcp_tools
            ]
    except Exception:
        pass

    return categories
