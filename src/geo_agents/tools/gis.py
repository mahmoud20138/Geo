from langchain_core.tools import tool


@tool
def query_geojson(layer: str, bbox: list[float]) -> dict:
    """Query a GIS layer within a bounding box. Returns GeoJSON features.

    Args:
        layer: Name of the GIS layer to query.
        bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat].
    """
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [bbox[0], bbox[1]]},
                "properties": {"layer": layer, "name": f"Sample from {layer}", "value": 42},
            }
        ],
    }


@tool
def get_satellite_imagery(lat: float, lon: float, date: str) -> dict:
    """Get satellite imagery metadata for a location and date.

    Args:
        lat: Latitude of the location.
        lon: Longitude of the location.
        date: Acquisition date in YYYY-MM-DD format.
    """
    return {
        "url": f"https://mock-satellite.example.com/imagery/{lat}/{lon}/{date}.tif",
        "resolution": "0.5m",
        "cloud_cover": 12.3,
        "bands": ["red", "green", "blue", "nir"],
        "acquisition_date": date,
    }


@tool
def calculate_area(polygon: list[list[float]]) -> dict:
    """Calculate the area of a polygon in square kilometers.

    Args:
        polygon: List of [lon, lat] coordinates forming a closed polygon.
    """
    n = len(polygon)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += polygon[i][0] * polygon[j][1]
        area -= polygon[j][0] * polygon[i][1]
    area = abs(area) / 2.0
    return {"area_sq_km": round(area * 111.32 * 111.32, 2), "unit": "sq_km"}
