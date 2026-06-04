from langchain_core.messages import SystemMessage, HumanMessage
from geo_agents.agents.base import get_llm
from geo_agents.state import AgentState

ANALYST_SYSTEM_PROMPT = """You are an analysis agent for a geospatial digital twin platform.

Analyze the execution results and provide insights. Respond with ONLY valid JSON (no markdown):

{{
  "summary": "brief overview of findings",
  "patterns": ["pattern 1", "pattern 2"],
  "risks": ["risk 1", "risk 2"],
  "recommendations": ["recommendation 1", "recommendation 2"],
  "kpis": {{"metric_name": "value"}}
}}"""


async def analyst_node(state: AgentState) -> dict:
    """Analyst agent node. Analyzes execution results."""
    llm = get_llm(temperature=0.2)

    execution_results = state.get("execution_results", [])
    results_text = "\n".join(
        [f"- {r.get('tool', 'unknown')}: {r.get('result', 'no result')}" for r in execution_results]
    )

    if not results_text.strip():
        results_text = "No execution results available yet."

    messages = [
        SystemMessage(content=ANALYST_SYSTEM_PROMPT),
        HumanMessage(content=f"Execution Results:\n{results_text}\n\nAnalyze these results."),
    ]

    response = await llm.ainvoke(messages)

    analysis = {
        "summary": response.content,
        "raw_results": execution_results,
    }

    return {
        "analysis_results": analysis,
        "active_agent": "analyst",
        "next_agent": "supervisor",
        "status": "reviewing",
        "iteration": state.get("iteration", 0) + 1,
        "messages": [],
    }
