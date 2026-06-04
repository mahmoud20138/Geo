from langchain_core.messages import SystemMessage, HumanMessage
from geo_agents.agents.base import get_llm
from geo_agents.state import AgentState
from geo_agents.config import settings

SUPERVISOR_SYSTEM_PROMPT = """You are a supervisor agent for a geospatial digital twin platform.
Review the current state and decide the next action.

Respond with ONLY one of these exact words (no explanation):
- APPROVE if the work is complete
- PLANNER if the plan needs revision
- EXECUTOR if more execution steps remain
- ANALYST if analysis is needed"""


async def supervisor_node(state: AgentState) -> dict:
    """Supervisor agent node. Reviews and routes."""
    if state.get("iteration", 0) >= settings.max_iterations:
        return {
            "active_agent": "supervisor",
            "next_agent": "end",
            "status": "complete",
            "supervisor_approved": True,
            "messages": [],
        }

    llm = get_llm(temperature=0.0)

    plan = state.get("current_plan") or []
    results = state.get("execution_results") or []
    analysis = state.get("analysis_results") or {}
    current_step = state.get("current_step", 0)

    # Auto-approve if all steps executed and analysis done
    if current_step >= len(plan) and results and analysis:
        return {
            "active_agent": "supervisor",
            "next_agent": "end",
            "status": "complete",
            "supervisor_approved": True,
            "iteration": state.get("iteration", 0) + 1,
            "messages": [],
        }

    context = f"""Objective: {state.get('objective', 'Unknown')}
Plan: {len(plan)} steps
Steps completed: {current_step}/{len(plan)}
Tool results: {len(results)}
Analysis: {'done' if analysis else 'not yet'}
Iteration: {state.get('iteration', 0)}/{settings.max_iterations}"""

    messages = [
        SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
        HumanMessage(content=context),
    ]

    response = await llm.ainvoke(messages)
    decision = response.content.strip().upper()

    if "APPROVE" in decision:
        next_agent = "end"
        status = "complete"
        approved = True
    elif "PLANNER" in decision:
        next_agent = "planner"
        status = "planning"
        approved = False
    elif "ANALYST" in decision:
        next_agent = "analyst"
        status = "analyzing"
        approved = False
    else:
        next_agent = "executor"
        status = "executing"
        approved = False

    return {
        "active_agent": "supervisor",
        "next_agent": next_agent,
        "status": status,
        "supervisor_approved": approved,
        "iteration": state.get("iteration", 0) + 1,
        "messages": [],
    }
