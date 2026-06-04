import json
from langchain_core.messages import SystemMessage, HumanMessage
from geo_agents.agents.base import get_llm
from geo_agents.tools.registry import get_all_tools, get_tool_names
from geo_agents.state import AgentState

EXECUTOR_SYSTEM_PROMPT = """You are an execution agent for a geospatial digital twin platform.

Available tools: {tools}

When given a step to execute, respond with a JSON object describing which tool(s) to call and with what arguments.
Format your response as ONLY valid JSON (no markdown, no explanation):

{{
  "tool_calls": [
    {{"name": "tool_name", "args": {{"param": "value"}}}}
  ],
  "reasoning": "brief explanation"
}}

If no tool is needed, return {{"tool_calls": [], "reasoning": "..."}}."""

TOOL_DESCRIPTIONS = {
    "query_geojson": "Query GIS layer. Args: layer (str), bbox ([min_lon, min_lat, max_lon, max_lat])",
    "get_satellite_imagery": "Get satellite imagery. Args: lat (float), lon (float), date (YYYY-MM-DD)",
    "calculate_area": "Calculate polygon area. Args: polygon ([[lon,lat], ...])",
    "query_postgres": "Query database. Args: table (str), filters (str)",
    "query_timeseries": "Query time series. Args: metric (str), start (ISO), end (ISO)",
    "get_telemetry": "Get sensor readings. Args: device_id (str)",
    "get_gps_data": "Get GPS location. Args: asset_id (str)",
    "weather_api": "Get weather. Args: lat (float), lon (float)",
    "traffic_api": "Get traffic. Args: region (str)",
}


def _build_tool_desc():
    lines = []
    for name, desc in TOOL_DESCRIPTIONS.items():
        lines.append(f"- {name}: {desc}")
    return "\n".join(lines)


def _parse_tool_calls(llm_output: str) -> list[dict]:
    """Parse tool calls from LLM output, handling various formats."""
    text = llm_output.strip()

    # Strip markdown code fences
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                text = part
                break

    # Find JSON object
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        text = text[start:end]

    try:
        data = json.loads(text)
        return data.get("tool_calls", [])
    except json.JSONDecodeError:
        return []


def _execute_tools(tool_calls: list[dict], tools: list) -> list[dict]:
    """Execute tool calls and collect results."""
    results = []
    tool_map = {t.name: t for t in tools}

    for tc in tool_calls:
        name = tc.get("name", "")
        args = tc.get("args", {})
        if name in tool_map:
            try:
                result = tool_map[name].invoke(args)
                results.append({"tool": name, "args": args, "result": result})
            except Exception as e:
                results.append({"tool": name, "args": args, "result": {"error": str(e)}})
        else:
            results.append({"tool": name, "args": args, "result": {"error": f"Unknown tool: {name}"}})

    return results


async def executor_node(state: AgentState) -> dict:
    """Executor agent node. Executes plan steps using tools."""
    llm = get_llm(temperature=0.1)

    current_step = state.get("current_step", 0)
    plan = state.get("current_plan") or []
    step_description = plan[current_step] if current_step < len(plan) else "No more steps"

    # Determine relevant tools based on step keywords
    tool_hints = []
    step_lower = step_description.lower()
    if any(w in step_lower for w in ["weather", "wind", "rain", "temperature", "forecast"]):
        tool_hints.append(("weather_api", {"lat": 40.7128, "lon": -74.0060}))
    if any(w in step_lower for w in ["traffic", "road", "route", "congestion"]):
        tool_hints.append(("traffic_api", {"region": "New York"}))
    if any(w in step_lower for w in ["sensor", "telemetry", "device", "humidity"]):
        tool_hints.append(("get_telemetry", {"device_id": "sensor-001"}))
    if any(w in step_lower for w in ["gps", "location", "position", "asset"]):
        tool_hints.append(("get_gps_data", {"asset_id": "asset-001"}))
    if any(w in step_lower for w in ["satellite", "imagery", "image"]):
        tool_hints.append(("get_satellite_imagery", {"lat": 40.7128, "lon": -74.0060, "date": "2024-01-15"}))
    if any(w in step_lower for w in ["gis", "geojson", "map", "layer", "spatial"]):
        tool_hints.append(("query_geojson", {"layer": "buildings", "bbox": [-74.02, 40.70, -74.00, 40.72]}))
    if any(w in step_lower for w in ["database", "query", "data", "records", "asset"]):
        tool_hints.append(("query_postgres", {"table": "assets", "filters": "status = 'active'"}))
    if any(w in step_lower for w in ["timeseries", "history", "trend", "metric"]):
        tool_hints.append(("query_timeseries", {"metric": "temperature", "start": "2024-01-01T00:00:00Z", "end": "2024-01-02T00:00:00Z"}))
    if any(w in step_lower for w in ["area", "polygon", "calculate", "size"]):
        tool_hints.append(("calculate_area", {"polygon": [[-74.02, 40.70], [-74.00, 40.70], [-74.00, 40.72], [-74.02, 40.72], [-74.02, 40.70]]}))

    # If no keyword matches, ask LLM to pick tools
    if not tool_hints:
        messages = [
            SystemMessage(content=EXECUTOR_SYSTEM_PROMPT.format(tools=_build_tool_desc())),
            HumanMessage(content=f"Execute this step: {step_description}\n\nWhich tools should I call? Respond with JSON only."),
        ]
        response = await llm.ainvoke(messages)
        tool_calls = _parse_tool_calls(response.content)
        tools = get_all_tools()
        tool_results = _execute_tools(tool_calls, tools)
    else:
        # Execute the hinted tools directly
        tools = get_all_tools()
        tool_results = _execute_tools(
            [{"name": name, "args": args} for name, args in tool_hints],
            tools,
        )

    next_step = current_step + 1
    if next_step >= len(plan):
        next_agent = "analyst"
        new_status = "analyzing"
    else:
        next_agent = "executor"
        new_status = "executing"

    return {
        "current_step": next_step,
        "execution_results": state.get("execution_results", []) + tool_results,
        "active_agent": "executor",
        "next_agent": next_agent,
        "status": new_status,
        "iteration": state.get("iteration", 0) + 1,
        "messages": [],
    }
