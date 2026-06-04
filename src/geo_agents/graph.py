from langgraph.graph import StateGraph, START, END
from geo_agents.state import AgentState
from geo_agents.agents.supervisor import supervisor_node
from geo_agents.agents.planner import planner_node
from geo_agents.agents.executor import executor_node
from geo_agents.agents.analyst import analyst_node


def route_from_supervisor(state: AgentState) -> str:
    """Route from supervisor based on next_agent field."""
    return state.get("next_agent", "end")


def route_from_executor(state: AgentState) -> str:
    """Route from executor based on next_agent field."""
    return state.get("next_agent", "supervisor")


def build_graph():
    """Build and compile the LangGraph StateGraph."""
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("analyst", analyst_node)

    graph.add_edge(START, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "planner": "planner",
            "executor": "executor",
            "analyst": "analyst",
            "end": END,
        },
    )

    graph.add_edge("planner", "executor")

    graph.add_conditional_edges(
        "executor",
        route_from_executor,
        {
            "analyst": "analyst",
            "planner": "planner",
            "supervisor": "supervisor",
        },
    )

    graph.add_edge("analyst", "supervisor")

    return graph.compile()


agent_graph = build_graph()
