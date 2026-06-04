from langchain_core.messages import SystemMessage, HumanMessage
from geo_agents.agents.base import get_llm
from geo_agents.state import AgentState

PLANNER_SYSTEM_PROMPT = """You are a mission planning agent for a geospatial digital twin platform.

Break down the user's objective into 3-6 concrete steps. Each step should use one of these tools:
- weather_api: Check weather conditions for a location
- traffic_api: Check traffic in a region
- get_telemetry: Get sensor readings from a device
- get_gps_data: Get GPS location of an asset
- get_satellite_imagery: Get satellite image metadata
- query_geojson: Query GIS map layers
- query_postgres: Query the asset database
- query_timeseries: Query historical metric data
- calculate_area: Calculate area of a region

Respond with ONLY a JSON array of step descriptions (no markdown, no explanation):
["Step 1: ...", "Step 2: ...", "Step 3: ..."]"""


def _parse_plan(llm_output: str) -> list[str]:
    """Parse plan steps from LLM output."""
    text = llm_output.strip()

    # Strip markdown code fences
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("["):
                text = part
                break

    # Find JSON array
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        text = text[start:end]

    try:
        steps = json.loads(text)
        if isinstance(steps, list) and all(isinstance(s, str) for s in steps):
            return steps
    except Exception:
        pass

    # Fallback: split by newlines
    lines = [l.strip().lstrip("0123456789.-) ") for l in llm_output.strip().split("\n") if l.strip()]
    return [l for l in lines if len(l) > 10] or [llm_output.strip()]


import json


async def planner_node(state: AgentState) -> dict:
    """Planner agent node. Breaks down objectives into execution plans."""
    llm = get_llm(temperature=0.2)

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"Objective: {state['objective']}"),
    ]

    response = await llm.ainvoke(messages)
    steps = _parse_plan(response.content)

    return {
        "current_plan": steps,
        "current_step": 0,
        "active_agent": "planner",
        "next_agent": "executor",
        "status": "executing",
        "iteration": state.get("iteration", 0) + 1,
        "messages": [],
    }
