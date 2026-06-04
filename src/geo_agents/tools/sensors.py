from langchain_core.tools import tool


@tool
def get_telemetry(device_id: str) -> dict:
    """Get latest telemetry readings from a sensor device.

    Args:
        device_id: Unique identifier of the sensor device.
    """
    return {
        "device_id": device_id,
        "timestamp": "2024-01-01T12:00:00Z",
        "readings": {
            "temperature": 22.5,
            "humidity": 65.2,
            "pressure": 1013.25,
            "battery": 87,
        },
        "status": "online",
    }


@tool
def get_gps_data(asset_id: str) -> dict:
    """Get GPS location data for a tracked asset.

    Args:
        asset_id: Unique identifier of the tracked asset.
    """
    return {
        "asset_id": asset_id,
        "lat": 40.7128,
        "lon": -74.0060,
        "altitude": 10.5,
        "speed": 0.0,
        "heading": 180.0,
        "accuracy": 2.5,
        "timestamp": "2024-01-01T12:00:00Z",
    }
