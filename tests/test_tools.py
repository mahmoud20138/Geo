import pytest
from geo_agents.tools.gis import query_geojson, get_satellite_imagery, calculate_area
from geo_agents.tools.database import query_postgres, query_timeseries
from geo_agents.tools.sensors import get_telemetry, get_gps_data
from geo_agents.tools.external import weather_api, traffic_api
from geo_agents.tools.registry import get_all_tools, get_tool_names


def test_query_geojson_returns_features():
    result = query_geojson.invoke({"layer": "buildings", "bbox": [10.0, 20.0, 30.0, 40.0]})
    assert result["type"] == "FeatureCollection"
    assert len(result["features"]) > 0
    assert result["features"][0]["type"] == "Feature"
    assert "geometry" in result["features"][0]
    assert "properties" in result["features"][0]


def test_get_satellite_imagery_returns_metadata():
    result = get_satellite_imagery.invoke({"lat": 40.7128, "lon": -74.0060, "date": "2024-01-01"})
    assert "url" in result
    assert "resolution" in result
    assert "cloud_cover" in result
    assert "bands" in result
    assert result["acquisition_date"] == "2024-01-01"
    assert len(result["bands"]) == 4


def test_calculate_area_returns_area():
    polygon = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]
    result = calculate_area.invoke({"polygon": polygon})
    assert "area_sq_km" in result
    assert result["unit"] == "sq_km"
    assert result["area_sq_km"] > 0


def test_query_postgres_returns_rows():
    result = query_postgres.invoke({"table": "assets", "filters": "status = 'active'"})
    assert "table" in result
    assert "rows" in result
    assert "total" in result
    assert result["table"] == "assets"
    assert result["total"] == 2
    assert len(result["rows"]) == 2
    assert result["filters_applied"] == "status = 'active'"


def test_query_timeseries_returns_data_points():
    result = query_timeseries.invoke({
        "metric": "temperature",
        "start": "2024-01-01T00:00:00Z",
        "end": "2024-01-01T00:02:00Z",
    })
    assert result["metric"] == "temperature"
    assert "data_points" in result
    assert len(result["data_points"]) == 3
    assert result["unit"] == "celsius"


def test_get_telemetry_returns_readings():
    result = get_telemetry.invoke({"device_id": "sensor-001"})
    assert result["device_id"] == "sensor-001"
    assert "readings" in result
    assert "temperature" in result["readings"]
    assert "humidity" in result["readings"]
    assert "pressure" in result["readings"]
    assert "battery" in result["readings"]
    assert result["status"] == "online"


def test_get_gps_data_returns_location():
    result = get_gps_data.invoke({"asset_id": "asset-001"})
    assert result["asset_id"] == "asset-001"
    assert "lat" in result
    assert "lon" in result
    assert "altitude" in result
    assert "speed" in result
    assert "heading" in result
    assert "accuracy" in result


def test_weather_api_returns_weather():
    result = weather_api.invoke({"lat": 40.7128, "lon": -74.0060})
    assert "location" in result
    assert "temperature" in result
    assert "humidity" in result
    assert "wind_speed" in result
    assert "conditions" in result
    assert "forecast" in result
    assert result["location"]["lat"] == 40.7128


def test_traffic_api_returns_conditions():
    result = traffic_api.invoke({"region": "downtown"})
    assert result["region"] == "downtown"
    assert "congestion_level" in result
    assert "average_speed_kmh" in result
    assert "incidents" in result
    assert len(result["incidents"]) > 0
    assert "type" in result["incidents"][0]


def test_get_all_tools_returns_all_tools():
    tools = get_all_tools()
    assert len(tools) == 9
    tool_names = {t.name for t in tools}
    expected = {
        "query_geojson", "get_satellite_imagery", "calculate_area",
        "query_postgres", "query_timeseries",
        "get_telemetry", "get_gps_data",
        "weather_api", "traffic_api",
    }
    assert tool_names == expected


def test_get_tool_names_returns_names():
    names = get_tool_names()
    assert len(names) == 9
    assert "query_geojson" in names
    assert "weather_api" in names
    assert all(isinstance(n, str) for n in names)
