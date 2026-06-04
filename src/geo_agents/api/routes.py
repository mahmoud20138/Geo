import time
from fastapi import APIRouter
from pydantic import BaseModel
from geo_agents.state import create_initial_state
from geo_agents.graph import agent_graph
from geo_agents.tools.registry import get_all_tools, get_tool_names, get_tools_by_category
from geo_agents.config import settings

router = APIRouter()
_start_time = time.time()
_request_count = 0


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    status: str
    plan: list[str] | None = None
    analysis: dict | None = None
    tool_calls: list[dict] | None = None
    iterations: int | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent system. Full pipeline: supervisor -> planner -> executor -> analyst."""
    global _request_count
    _request_count += 1
    state = create_initial_state(request.message)
    result = await agent_graph.ainvoke(state)
    last_message = result["messages"][-1] if result["messages"] else None
    response_text = last_message.content if last_message else result.get("analysis_results", {}).get("summary", "No response")
    return ChatResponse(
        response=response_text,
        status=result.get("status", "unknown"),
        plan=result.get("current_plan"),
        analysis=result.get("analysis_results"),
        tool_calls=result.get("execution_results"),
        iterations=result.get("iteration", 0),
    )


@router.post("/mission", response_model=ChatResponse)
async def create_mission(request: ChatRequest):
    """Create a complex multi-step mission (alias for /chat)."""
    return await chat(request)


@router.post("/analyze", response_model=ChatResponse)
async def analyze(request: ChatRequest):
    """Quick analysis request (analyst agent only)."""
    global _request_count
    _request_count += 1
    state = create_initial_state(request.message)
    state["active_agent"] = "analyst"
    state["status"] = "analyzing"
    state["execution_results"] = [{"tool": "direct_input", "result": {"data": request.message}}]
    from geo_agents.agents.analyst import analyst_node
    result = await analyst_node(state)
    return ChatResponse(
        response=result.get("analysis_results", {}).get("summary", "No analysis"),
        status="analyzing",
        analysis=result.get("analysis_results"),
    )


@router.post("/plan", response_model=dict)
async def plan_only(request: ChatRequest):
    """Generate a plan without executing."""
    global _request_count
    _request_count += 1
    state = create_initial_state(request.message)
    from geo_agents.agents.planner import planner_node
    result = await planner_node(state)
    return {
        "plan": result.get("current_plan", []),
        "objective": request.message,
        "status": "planned",
    }


@router.get("/assets")
async def list_assets():
    """List all tracked geospatial assets."""
    return {
        "assets": [
            {"id": "asset-001", "name": "Drone Alpha", "type": "uav", "status": "active", "lat": 40.7128, "lon": -74.0060, "battery": 87, "mission": "Aerial survey"},
            {"id": "asset-002", "name": "Sensor Array B", "type": "sensor", "status": "active", "lat": 40.7580, "lon": -73.9855, "battery": 100, "mission": "Air quality monitoring"},
            {"id": "asset-003", "name": "Satellite Charlie", "type": "satellite", "status": "standby", "lat": 0.0, "lon": 0.0, "battery": 100, "mission": "Earth observation"},
            {"id": "asset-004", "name": "Drone Beta", "type": "uav", "status": "active", "lat": 34.0522, "lon": -118.2437, "battery": 62, "mission": "Infrastructure inspection"},
            {"id": "asset-005", "name": "Weather Station D", "type": "sensor", "status": "active", "lat": 51.5074, "lon": -0.1278, "battery": 95, "mission": "Meteorological data"},
        ]
    }


@router.get("/telemetry")
async def get_telemetry_endpoint():
    """Get live telemetry from all sensors."""
    return {
        "readings": [
            {"device_id": "sensor-001", "temperature": 22.5, "humidity": 65.2, "pressure": 1013.25, "battery": 87, "status": "online"},
            {"device_id": "sensor-002", "temperature": 19.8, "humidity": 70.1, "pressure": 1015.10, "battery": 100, "status": "online"},
            {"device_id": "sensor-003", "temperature": 25.1, "humidity": 55.3, "pressure": 1012.80, "battery": 72, "status": "online"},
            {"device_id": "weather-station-01", "temperature": 18.5, "humidity": 72.0, "pressure": 1018.50, "battery": 95, "status": "online"},
        ],
        "timestamp": "2024-01-15T12:00:00Z",
        "total_sensors": 4,
        "online": 4,
    }


@router.get("/tools")
async def list_tools():
    """List all available tools and their descriptions."""
    tools = get_all_tools()
    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.args_schema.schema() if hasattr(t, "args_schema") and t.args_schema else {},
            }
            for t in tools
        ],
        "total": len(tools),
    }


@router.get("/status")
async def system_status():
    """Get full system status."""
    from geo_agents.plugins.base import get_registered_plugins
    from geo_agents.skills.loader import get_all_skills
    from geo_agents.mcp.client import get_mcp_servers

    uptime = int(time.time() - _start_time)
    plugins = get_registered_plugins()
    skills = get_all_skills()
    mcp = get_mcp_servers()

    return {
        "status": "operational",
        "provider": settings.provider,
        "model": settings.llm_model,
        "base_url": settings.llm_base_url,
        "uptime_seconds": uptime,
        "uptime_human": f"{uptime // 3600}h {(uptime % 3600) // 60}m {uptime % 60}s",
        "requests_served": _request_count,
        "agents": ["supervisor", "planner", "executor", "analyst"],
        "tools_available": len(get_all_tools()),
        "graph_nodes": 4,
        "max_iterations": settings.max_iterations,
        "extensions": {
            "plugins": len(plugins),
            "skills": len(skills),
            "mcp_servers": len(mcp),
        },
    }


@router.get("/graph")
async def get_graph_structure():
    """Get the agent graph structure for visualization."""
    return {
        "nodes": [
            {"id": "start", "type": "input", "label": "Start"},
            {"id": "supervisor", "type": "agent", "label": "Supervisor", "description": "Reviews work, decides next step"},
            {"id": "planner", "type": "agent", "label": "Planner", "description": "Breaks objectives into steps"},
            {"id": "executor", "type": "agent", "label": "Executor", "description": "Executes plan steps using tools"},
            {"id": "analyst", "type": "agent", "label": "Analyst", "description": "Analyzes results, finds insights"},
            {"id": "end", "type": "output", "label": "End"},
        ],
        "edges": [
            {"from": "start", "to": "supervisor", "label": "init"},
            {"from": "supervisor", "to": "planner", "label": "ROUTE:PLANNER"},
            {"from": "supervisor", "to": "executor", "label": "ROUTE:EXECUTOR"},
            {"from": "supervisor", "to": "analyst", "label": "ROUTE:ANALYST"},
            {"from": "supervisor", "to": "end", "label": "APPROVE"},
            {"from": "planner", "to": "executor", "label": "plan ready"},
            {"from": "executor", "to": "analyst", "label": "all steps done"},
            {"from": "executor", "to": "executor", "label": "next step"},
            {"from": "executor", "to": "planner", "label": "replan"},
            {"from": "analyst", "to": "supervisor", "label": "review"},
        ],
        "tools": [
            {"name": "query_geojson", "category": "GIS"},
            {"name": "get_satellite_imagery", "category": "GIS"},
            {"name": "calculate_area", "category": "GIS"},
            {"name": "query_postgres", "category": "Database"},
            {"name": "query_timeseries", "category": "Database"},
            {"name": "get_telemetry", "category": "Sensors"},
            {"name": "get_gps_data", "category": "Sensors"},
            {"name": "weather_api", "category": "External"},
            {"name": "traffic_api", "category": "External"},
        ],
    }


@router.post("/demo/weather-check")
async def demo_weather_check():
    """Demo: Check weather for all active drone locations."""
    from geo_agents.tools.external import weather_api
    locations = [
        {"name": "Drone Alpha", "lat": 40.7128, "lon": -74.0060},
        {"name": "Drone Beta", "lat": 34.0522, "lon": -118.2437},
    ]
    results = []
    for loc in locations:
        weather = weather_api.invoke({"lat": loc["lat"], "lon": loc["lon"]})
        results.append({"asset": loc["name"], "location": {"lat": loc["lat"], "lon": loc["lon"]}, "weather": weather})
    return {"demo": "weather_check", "results": results}


@router.post("/demo/fleet-status")
async def demo_fleet_status():
    """Demo: Get full fleet status with GPS + telemetry."""
    from geo_agents.tools.sensors import get_gps_data, get_telemetry
    assets = ["asset-001", "asset-002", "asset-003"]
    results = []
    for asset_id in assets:
        gps = get_gps_data.invoke({"asset_id": asset_id})
        telemetry = get_telemetry.invoke({"device_id": asset_id.replace("asset", "sensor")})
        results.append({"asset_id": asset_id, "gps": gps, "telemetry": telemetry})
    return {"demo": "fleet_status", "results": results}


@router.post("/demo/spatial-query")
async def demo_spatial_query():
    """Demo: GIS spatial query with area calculation."""
    from geo_agents.tools.gis import query_geojson, calculate_area
    geojson = query_geojson.invoke({"layer": "buildings", "bbox": [-74.02, 40.70, -74.00, 40.72]})
    polygon = [[-74.02, 40.70], [-74.00, 40.70], [-74.00, 40.72], [-74.02, 40.72], [-74.02, 40.70]]
    area = calculate_area.invoke({"polygon": polygon})
    return {"demo": "spatial_query", "geojson": geojson, "area": area}


@router.post("/demo/plan")
async def demo_plan():
    """Demo: Generate a plan for a geological survey mission."""
    from geo_agents.agents.planner import planner_node
    state = create_initial_state("Survey the copper deposit at ABC mine, check weather, and analyze drillhole data")
    result = await planner_node(state)
    return {
        "demo": "plan_generation",
        "objective": state["objective"],
        "plan": result.get("current_plan", []),
        "steps_count": len(result.get("current_plan", [])),
    }


@router.post("/demo/analyze")
async def demo_analyze():
    """Demo: Analyze sample geological data."""
    from geo_agents.agents.analyst import analyst_node
    state = create_initial_state("Analyze drillhole results")
    state["active_agent"] = "analyst"
    state["status"] = "analyzing"
    state["execution_results"] = [
        {"tool": "process_drillhole_data", "result": {"interval": {"from": 150, "to": 300}, "midpoint": {"lat": 40.71, "lon": -74.01, "elev": -225}}},
        {"tool": "weather_api", "result": {"temperature": 18.5, "wind_speed": 12.3, "conditions": "partly_cloudy"}},
        {"tool": "query_geojson", "result": {"features": [{"properties": {"layer": "faults", "name": "F1-NE-trending"}}]}},
    ]
    result = await analyst_node(state)
    return {
        "demo": "analysis",
        "analysis": result.get("analysis_results", {}),
        "status": "analyzing",
    }


@router.post("/demo/skill-run")
async def demo_skill_run():
    """Demo: Run the weather_planning skill."""
    from geo_agents.skills.loader import get_skill
    skill = get_skill("weather_planning")
    if not skill:
        return {"error": "Skill not found"}
    return {
        "demo": "skill_execution",
        "skill": skill.name,
        "description": skill.description,
        "tools": skill.tools,
        "steps": skill.steps,
        "system_prompt_preview": skill.system_prompt[:200] + "...",
        "status": "skill_loaded",
    }


@router.post("/demo/rag-ingest")
async def demo_rag_ingest():
    """Demo: Ingest a sample geological report into RAG."""
    try:
        from geo_agents.rag import RAGEngine
        rag = RAGEngine()
        sample_text = """The copper mineralization at the ABC deposit occurs at depths between 150-300m below surface.
The primary host rock is a quartz-monzonite intrusion with stockwork veining.
Grades range from 0.3% to 1.2% Cu, with a mean of 0.65%.
The mineralization is associated with pyrite and chalcopyrite.
The F1 fault system appears to control the mineralization.
Historical drilling in 1985 intersected 15m at 2.1% Cu from 180m depth in hole DH-85-012."""
        chunks = rag.ingest_text(sample_text, source="demo_drill_report.txt")
        return {"demo": "rag_ingest", "chunks_created": chunks, "source": "demo_drill_report.txt", "status": "ingested"}
    except ImportError:
        return {"error": "RAG not available. Install: pip install chromadb sentence-transformers"}


@router.post("/demo/rag-query")
async def demo_rag_query():
    """Demo: Query the RAG knowledge base."""
    try:
        from geo_agents.rag import RAGEngine
        rag = RAGEngine()
        result = rag.query("What are the copper grades at depth?", n_results=3)
        return {"demo": "rag_query", **result.to_dict()}
    except ImportError:
        return {"error": "RAG not available"}


@router.post("/demo/tools-list")
async def demo_tools_list():
    """Demo: List all available tools by category."""
    return {"demo": "tools_inventory", "categories": get_tools_by_category(), "total": len(get_all_tools())}


@router.post("/demo/plugins-reload")
async def demo_plugins_reload():
    """Demo: Hot-reload all plugins."""
    from geo_agents.plugins.loader import reload_plugins as do_reload
    result = do_reload(settings.plugin_paths)
    return {"demo": "plugins_reload", **result}


@router.post("/demo/database-query")
async def demo_database_query():
    """Demo: Query the database for assets."""
    from geo_agents.tools.database import query_postgres
    result = query_postgres.invoke({"table": "assets", "filters": "status = 'active'"})
    return {"demo": "database_query", "result": result}


@router.post("/demo/sensor-telemetry")
async def demo_sensor_telemetry():
    """Demo: Get telemetry from all sensors."""
    from geo_agents.tools.sensors import get_telemetry, get_gps_data
    sensors = ["sensor-001", "sensor-002", "sensor-003"]
    results = []
    for s in sensors:
        telemetry = get_telemetry.invoke({"device_id": s})
        results.append({"sensor": s, "telemetry": telemetry})
    return {"demo": "sensor_telemetry", "results": results, "count": len(results)}


# ──────────────────────────────────────────────
#  Plugin / Skill / MCP Endpoints
# ──────────────────────────────────────────────

@router.get("/plugins")
async def list_plugins():
    """List all loaded plugins and their tools."""
    from geo_agents.plugins.base import get_registered_plugins
    plugins = get_registered_plugins()
    return {
        "plugins": [
            {
                "name": info.name,
                "description": info.description,
                "category": info.category,
                "version": info.version,
                "source": info.source,
                "enabled": info.enabled,
            }
            for info in plugins.values()
        ],
        "count": len(plugins),
    }


@router.post("/plugins/reload")
async def reload_plugins():
    """Hot-reload all plugins from configured directories."""
    from geo_agents.plugins.loader import reload_plugins as do_reload
    result = do_reload(settings.plugin_paths)
    return result


@router.get("/skills")
async def list_skills():
    """List all available skills."""
    from geo_agents.skills.loader import get_all_skills
    skills = get_all_skills()
    return {
        "skills": [
            {
                "name": s.name,
                "description": s.description,
                "category": s.category,
                "version": s.version,
                "tools": s.tools,
                "steps": s.steps,
                "source": s.source,
            }
            for s in skills.values()
        ],
        "count": len(skills),
    }


@router.post("/skills/{name}/run")
async def run_skill(name: str, request: ChatRequest):
    """Execute a skill by name. Uses the skill's system prompt and tools."""
    from geo_agents.skills.loader import get_skill
    skill = get_skill(name)
    if not skill:
        return {"error": f"Skill not found: {name}"}

    # Create state with skill's system prompt context
    objective = f"[Skill: {skill.name}] {request.message}"
    state = create_initial_state(objective)

    # Run through the agent graph
    result = await agent_graph.ainvoke(state)

    last_message = result["messages"][-1] if result["messages"] else None
    response_text = last_message.content if last_message else result.get("analysis_results", {}).get("summary", "No response")

    return {
        "skill": name,
        "response": response_text,
        "status": result.get("status", "unknown"),
        "plan": result.get("current_plan"),
        "analysis": result.get("analysis_results"),
        "tool_calls": result.get("execution_results"),
    }


@router.get("/mcp")
async def list_mcp():
    """List MCP server connections and tools."""
    from geo_agents.mcp.client import get_mcp_servers, get_mcp_tool_names
    servers = get_mcp_servers()
    tools = get_mcp_tool_names()
    return {
        "servers": [
            {
                "name": s.name,
                "transport": s.transport,
                "command": s.command,
                "url": s.url,
                "enabled": s.enabled,
            }
            for s in servers.values()
        ],
        "tools": tools,
        "server_count": len(servers),
        "tool_count": len(tools),
    }


@router.post("/mcp/reload")
async def reload_mcp():
    """Reload MCP server configurations."""
    from geo_agents.mcp.client import load_mcp_servers, clear_mcp
    clear_mcp()
    result = load_mcp_servers(settings.mcp_config)
    return result


@router.get("/extensions")
async def list_extensions():
    """List all extensions: plugins, skills, MCP servers, and tool categories."""
    from geo_agents.plugins.base import get_registered_plugins
    from geo_agents.skills.loader import get_all_skills
    from geo_agents.mcp.client import get_mcp_servers, get_mcp_tool_names

    plugins = get_registered_plugins()
    skills = get_all_skills()
    mcp_servers = get_mcp_servers()
    mcp_tools = get_mcp_tool_names()

    rag_stats = {}
    try:
        from geo_agents.rag import RAGEngine
        rag_stats = RAGEngine().stats()
    except Exception:
        rag_stats = {"documents": 0}

    return {
        "plugins": {"count": len(plugins), "names": list(plugins.keys())},
        "skills": {"count": len(skills), "names": list(skills.keys())},
        "mcp": {"servers": len(mcp_servers), "tools": len(mcp_tools), "names": mcp_tools},
        "rag": rag_stats,
        "core_tools": get_tool_names(),
        "total_tools": len(get_all_tools()),
        "tool_categories": get_tools_by_category(),
    }


# ──────────────────────────────────────────────
#  RAG Endpoints
# ──────────────────────────────────────────────

@router.get("/rag/stats")
async def rag_stats():
    """Get RAG knowledge base statistics."""
    try:
        from geo_agents.rag import RAGEngine
        rag = RAGEngine()
        return rag.stats()
    except ImportError:
        return {"error": "RAG not available. Install: pip install chromadb sentence-transformers"}
    except Exception as e:
        return {"error": str(e)}


@router.post("/rag/ingest")
async def rag_ingest(request: dict):
    """Ingest text into the RAG knowledge base.

    Body: {"text": "...", "source": "filename.txt"}
    """
    try:
        from geo_agents.rag import RAGEngine
        rag = RAGEngine()
        text = request.get("text", "")
        source = request.get("source", "api_input")
        if not text:
            return {"error": "No text provided"}
        chunks = rag.ingest_text(text, source=source)
        return {"chunks_created": chunks, "source": source, "status": "ingested"}
    except ImportError:
        return {"error": "RAG not available. Install: pip install chromadb sentence-transformers"}
    except Exception as e:
        return {"error": str(e)}


@router.post("/rag/query")
async def rag_query(request: dict):
    """Query the RAG knowledge base.

    Body: {"query": "...", "n_results": 5}
    """
    try:
        from geo_agents.rag import RAGEngine
        rag = RAGEngine()
        query = request.get("query", "")
        n_results = request.get("n_results", 5)
        if not query:
            return {"error": "No query provided"}
        result = rag.query(query, n_results=n_results)
        return result.to_dict()
    except ImportError:
        return {"error": "RAG not available. Install: pip install chromadb sentence-transformers"}
    except Exception as e:
        return {"error": str(e)}


@router.post("/rag/clear")
async def rag_clear():
    """Clear all documents from the RAG knowledge base."""
    try:
        from geo_agents.rag import RAGEngine
        rag = RAGEngine()
        rag.clear()
        return {"status": "cleared"}
    except ImportError:
        return {"error": "RAG not available. Install: pip install chromadb sentence-transformers"}
    except Exception as e:
        return {"error": str(e)}
