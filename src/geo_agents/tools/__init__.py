"""Tools for the geo-agents system.

Core tools are organized by category:
- GIS: query_geojson, get_satellite_imagery, calculate_area
- Database: query_postgres, query_timeseries
- Sensors: get_telemetry, get_gps_data
- External: weather_api, traffic_api

Additional tools are loaded dynamically from:
- plugins/ directory (@register_tool decorator)
- MCP servers (mcp_servers.json config)

Usage:
    from geo_agents.tools import get_all_tools, get_tool_names
    from geo_agents.tools.registry import get_tools_by_category
"""

from geo_agents.tools.registry import get_all_tools, get_tool_names, get_tools_by_category
from geo_agents.tools.gis import query_geojson, get_satellite_imagery, calculate_area
from geo_agents.tools.database import query_postgres, query_timeseries
from geo_agents.tools.sensors import get_telemetry, get_gps_data
from geo_agents.tools.external import weather_api, traffic_api

__all__ = [
    "get_all_tools",
    "get_tool_names",
    "get_tools_by_category",
    "query_geojson",
    "get_satellite_imagery",
    "calculate_area",
    "query_postgres",
    "query_timeseries",
    "get_telemetry",
    "get_gps_data",
    "weather_api",
    "traffic_api",
]
