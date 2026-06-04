"""Example plugin for geo-agents.

Copy this file and modify to create your own plugins.
Place .py files in the plugins/ directory and they will be auto-discovered.
"""

from geo_agents.plugins.base import register_tool


@register_tool(
    name="geocode_address",
    description="Convert an address to latitude/longitude coordinates.",
    category="GIS",
    version="1.0.0",
)
def geocode_address(address: str) -> dict:
    """Geocode an address to lat/lon coordinates.

    Args:
        address: Street address or place name to geocode.
    """
    # Mock implementation — replace with real geocoding API
    mock_results = {
        "times square, new york": {"lat": 40.7580, "lon": -73.9855},
        "golden gate bridge": {"lat": 37.8199, "lon": -122.4783},
        "eiffel tower": {"lat": 48.8584, "lon": 2.2945},
    }
    key = address.lower().strip()
    if key in mock_results:
        coords = mock_results[key]
        return {
            "address": address,
            "lat": coords["lat"],
            "lon": coords["lon"],
            "confidence": 0.95,
            "source": "mock_geocoder",
        }
    return {
        "address": address,
        "lat": 40.7128,
        "lon": -74.0060,
        "confidence": 0.5,
        "source": "mock_geocoder (fallback)",
    }


@register_tool(
    name="calculate_distance",
    description="Calculate the distance between two geographic points in kilometers.",
    category="GIS",
    version="1.0.0",
)
def calculate_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> dict:
    """Calculate great-circle distance between two points using Haversine formula.

    Args:
        lat1: Latitude of point 1.
        lon1: Longitude of point 1.
        lat2: Latitude of point 2.
        lon2: Longitude of point 2.
    """
    import math

    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    distance_km = round(R * c, 2)

    return {
        "from": {"lat": lat1, "lon": lon1},
        "to": {"lat": lat2, "lon": lon2},
        "distance_km": distance_km,
        "distance_miles": round(distance_km * 0.621371, 2),
    }


@register_tool(
    name="noaa_tides",
    description="Get tide predictions for a coastal location.",
    category="External",
    version="1.0.0",
)
def noaa_tides(station_id: str, date: str) -> dict:
    """Get tide predictions from NOAA for a station.

    Args:
        station_id: NOAA station ID (e.g., "8518750" for The Battery, NY).
        date: Date in YYYY-MM-DD format.
    """
    return {
        "station_id": station_id,
        "date": date,
        "predictions": [
            {"time": "02:15", "type": "L", "height_ft": 0.8},
            {"time": "08:30", "type": "H", "height_ft": 5.2},
            {"time": "14:45", "type": "L", "height_ft": 0.5},
            {"time": "20:50", "type": "H", "height_ft": 4.8},
        ],
        "units": "feet",
        "source": "NOAA (mock)",
    }
