from langchain_core.tools import tool


@tool
def query_postgres(table: str, filters: str) -> dict:
    """Query a PostgreSQL database table with filters. Returns mock rows.

    Args:
        table: Name of the database table to query.
        filters: Filter expression as a string (e.g. "status = 'active'").
    """
    return {
        "table": table,
        "rows": [
            {"id": 1, "name": "Asset Alpha", "status": "active", "lat": 40.7128, "lon": -74.0060},
            {"id": 2, "name": "Asset Beta", "status": "inactive", "lat": 34.0522, "lon": -118.2437},
        ],
        "total": 2,
        "filters_applied": filters,
    }


@tool
def query_timeseries(metric: str, start: str, end: str) -> dict:
    """Query time series data for a metric between two timestamps.

    Args:
        metric: Name of the metric to query (e.g. "temperature").
        start: Start timestamp in ISO 8601 format.
        end: End timestamp in ISO 8601 format.
    """
    return {
        "metric": metric,
        "start": start,
        "end": end,
        "data_points": [
            {"timestamp": start, "value": 23.5},
            {"timestamp": "2024-01-01T00:01:00Z", "value": 24.1},
            {"timestamp": end, "value": 22.8},
        ],
        "unit": "celsius",
    }
