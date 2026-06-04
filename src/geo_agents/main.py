"""Geo-Agents API Server.

FastAPI application with middleware, health checks, and extension loading.

Usage:
    uvicorn geo_agents.main:app --host 0.0.0.0 --port 8084
    python -m geo_agents.main
"""

import time
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from geo_agents.api.routes import router
from geo_agents.api.websocket import manager
from geo_agents.config import settings
from geo_agents.exceptions import GeoAgentsError

# ── Logging ──────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("geo_agents")

# ── Metrics ──────────────────────────────────────────────────

_metrics = {
    "requests_total": 0,
    "requests_ok": 0,
    "requests_error": 0,
    "start_time": time.time(),
}

# ── Lifespan ─────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load extensions on startup."""
    from geo_agents.plugins.loader import discover_plugins
    from geo_agents.skills.loader import load_skills
    from geo_agents.mcp.client import load_mcp_servers

    plugins = discover_plugins(settings.plugin_paths)
    skills = load_skills(settings.skills_paths)
    mcp = load_mcp_servers(settings.mcp_config)

    logger.info(
        f"Startup: {len(plugins)} plugin modules, "
        f"{len(skills)} skills, "
        f"{mcp.get('count', 0)} MCP servers"
    )
    yield
    logger.info("Shutdown: cleaning up")


# ── App ──────────────────────────────────────────────────────

DASHBOARD_PATH = Path(__file__).resolve().parent.parent.parent / "dashboard.html"

app = FastAPI(
    title="Geo-Agents API",
    version="0.2.0",
    description="Multi-agent orchestration for geospatial digital twin platforms",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track request metrics and logging."""
    _metrics["requests_total"] += 1
    start = time.time()

    try:
        response = await call_next(request)
        duration = time.time() - start

        if response.status_code < 400:
            _metrics["requests_ok"] += 1
        else:
            _metrics["requests_error"] += 1

        # Log API requests (skip health/dashboard)
        if request.url.path.startswith("/api/"):
            logger.info(
                f"{request.method} {request.url.path} "
                f"→ {response.status_code} ({duration:.3f}s)"
            )

        response.headers["X-Process-Time"] = f"{duration:.3f}"
        return response

    except Exception as e:
        _metrics["requests_error"] += 1
        logger.error(f"{request.method} {request.url.path} → ERROR: {e}")
        raise


# ── Error Handlers ───────────────────────────────────────────

@app.exception_handler(GeoAgentsError)
async def geo_agents_error_handler(request: Request, exc: GeoAgentsError):
    """Handle SDK errors with structured JSON responses."""
    return JSONResponse(
        status_code=400,
        content={
            "error": type(exc).__name__,
            "message": str(exc),
            "path": request.url.path,
        },
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "path": request.url.path,
        },
    )


# ── Routes ───────────────────────────────────────────────────

app.include_router(router, prefix="/api")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "provider": settings.provider,
        "model": settings.llm_model,
        "base_url": settings.llm_base_url,
        "version": "0.2.0",
    }


@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    uptime = time.time() - _metrics["start_time"]
    return {
        "uptime_seconds": int(uptime),
        "uptime_human": f"{int(uptime) // 3600}h {(int(uptime) % 3600) // 60}m {int(uptime) % 60}s",
        "requests_total": _metrics["requests_total"],
        "requests_ok": _metrics["requests_ok"],
        "requests_error": _metrics["requests_error"],
        "error_rate": round(_metrics["requests_error"] / max(_metrics["requests_total"], 1), 3),
    }


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard UI."""
    if DASHBOARD_PATH.exists():
        return HTMLResponse(content=DASHBOARD_PATH.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Dashboard not found</h1>", status_code=404)


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon if exists."""
    fav = Path(__file__).parent / "favicon.ico"
    if fav.exists():
        return FileResponse(fav, media_type="image/x-icon")
    return Response(status_code=204)


# ── Provider Management ──────────────────────────────────────

@app.get("/api/providers")
async def list_providers():
    """List all available providers and their status."""
    providers = {}
    for name in ["xiaomi", "ollama", "openrouter"]:
        url = getattr(settings, f"{name}_base_url")
        key = getattr(settings, f"{name}_api_key")
        model = getattr(settings, f"{name}_model")
        providers[name] = {
            "base_url": url,
            "model": model,
            "has_key": bool(key),
            "active": settings.provider == name,
        }
    return {"current": settings.provider, "providers": providers}


@app.post("/api/providers/{name}")
async def switch_provider(name: str):
    """Switch the active LLM provider at runtime."""
    if name not in ["xiaomi", "ollama", "openrouter"]:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unknown provider: {name}. Use: xiaomi, ollama, openrouter"},
        )
    settings.provider = name
    logger.info(f"Provider switched to: {name}")
    return {
        "switched_to": name,
        "model": settings.llm_model,
        "base_url": settings.llm_base_url,
    }


# ── WebSocket ────────────────────────────────────────────────

@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time agent updates."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Received: {data}")
    except Exception:
        manager.disconnect(websocket)


# ── CLI ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "geo_agents.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info",
    )
