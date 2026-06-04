from langchain_core.tools import tool


@tool
def weather_api(lat: float, lon: float) -> dict:
    """Get current weather data for a location.

    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.
    """
    return {
        "location": {"lat": lat, "lon": lon},
        "temperature": 18.5,
        "humidity": 72,
        "wind_speed": 12.3,
        "wind_direction": "NW",
        "conditions": "partly_cloudy",
        "visibility_km": 10.0,
        "forecast": "Clear skies expected in the next 6 hours",
    }


@tool
def traffic_api(region: str) -> dict:
    """Get current traffic conditions for a region.

    Args:
        region: Name of the region to query traffic for.
    """
    return {
        "region": region,
        "congestion_level": "moderate",
        "average_speed_kmh": 45,
        "incidents": [
            {
                "type": "accident",
                "location": "Highway 101 North",
                "severity": "minor",
                "delay_minutes": 15,
            }
        ],
        "last_updated": "2024-01-01T12:00:00Z",
    }
