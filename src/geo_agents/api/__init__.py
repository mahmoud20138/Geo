"""FastAPI routes and WebSocket management.

Provides the HTTP API for the geo-agents system.

Usage:
    from geo_agents.api.routes import router
    from geo_agents.api.websocket import manager
"""

from geo_agents.api.routes import router
from geo_agents.api.websocket import manager

__all__ = ["router", "manager"]
