import pytest
from geo_agents.graph import build_graph, route_from_supervisor, route_from_executor


def test_build_graph():
    graph = build_graph()
    assert graph is not None


def test_graph_has_nodes():
    graph = build_graph()
    node_names = set(graph.get_graph().nodes)
    assert "supervisor" in node_names
    assert "planner" in node_names
    assert "executor" in node_names
    assert "analyst" in node_names


def test_route_from_supervisor_planner():
    state = {"next_agent": "planner"}
    assert route_from_supervisor(state) == "planner"


def test_route_from_supervisor_end():
    state = {"next_agent": "end"}
    assert route_from_supervisor(state) == "end"


def test_route_from_supervisor_executor():
    state = {"next_agent": "executor"}
    assert route_from_supervisor(state) == "executor"


def test_route_from_supervisor_analyst():
    state = {"next_agent": "analyst"}
    assert route_from_supervisor(state) == "analyst"


def test_route_from_supervisor_default():
    state = {}
    assert route_from_supervisor(state) == "end"


def test_route_from_executor_analyst():
    state = {"next_agent": "analyst"}
    assert route_from_executor(state) == "analyst"


def test_route_from_executor_planner():
    state = {"next_agent": "planner"}
    assert route_from_executor(state) == "planner"


def test_route_from_executor_supervisor():
    state = {"next_agent": "supervisor"}
    assert route_from_executor(state) == "supervisor"


def test_route_from_executor_default():
    state = {}
    assert route_from_executor(state) == "supervisor"


from unittest.mock import AsyncMock, patch, MagicMock
from contextlib import ExitStack
from langchain_core.messages import AIMessage
from geo_agents.state import create_initial_state

AGENT_MODULES = [
    "geo_agents.agents.supervisor.get_llm",
    "geo_agents.agents.planner.get_llm",
    "geo_agents.agents.executor.get_llm",
    "geo_agents.agents.analyst.get_llm",
]


def _make_mock_llm(mock_llm_factory):
    mock = MagicMock()
    ainvoke_mock = AsyncMock(side_effect=mock_llm_factory)
    mock.ainvoke = ainvoke_mock
    llm_with_tools = MagicMock()
    llm_with_tools.ainvoke = ainvoke_mock
    mock.bind_tools.return_value = llm_with_tools
    return mock


def _patch_all_agents(mock_llm_factory):
    stack = ExitStack()
    for mod_path in AGENT_MODULES:
        stack.enter_context(patch(mod_path, side_effect=lambda *a, **kw: _make_mock_llm(mock_llm_factory)))
    return stack


@pytest.mark.asyncio
async def test_full_graph_flow():
    """Test that the graph can be invoked end-to-end with mocked LLM calls.

    Flow: supervisor -> planner -> executor -> analyst -> supervisor -> end
    """
    call_count = {"value": 0}

    def mock_llm_factory(messages):
        call_count["value"] += 1
        last_msg = messages[-1].content if messages else ""

        if "supervisor" in last_msg.lower() or "objective" in last_msg.lower():
            if call_count["value"] <= 2:
                return AIMessage(content="ROUTE:planner")
            else:
                return AIMessage(content="APPROVE")
        elif "planning" in last_msg.lower() or "objective:" in last_msg.lower():
            return AIMessage(
                content='{"plan": ["Step 1: Query GIS data", "Step 2: Analyze results"], "reasoning": "Test"}'
            )
        elif "execute" in last_msg.lower() or "current step" in last_msg.lower():
            return AIMessage(
                content="Step completed successfully",
                tool_calls=[],
            )
        elif "analy" in last_msg.lower() or "execution results" in last_msg.lower():
            return AIMessage(
                content='{"summary": "Analysis complete", "patterns": [], "risks": [], "recommendations": []}'
            )
        else:
            return AIMessage(content="APPROVE")

    with _patch_all_agents(mock_llm_factory):
        from geo_agents.graph import agent_graph

        state = create_initial_state("Analyze urban heat islands using satellite data")
        result = await agent_graph.ainvoke(state)

        assert result["status"] in ("complete", "reviewing", "executing", "analyzing")
        assert result["iteration"] > 0
        assert result["messages"] is not None


@pytest.mark.asyncio
async def test_full_graph_flow_with_tools():
    """Test the graph flow with tool calls mocked."""
    from geo_agents.tools.gis import query_geojson

    def mock_llm_factory(messages):
        last_msg = messages[-1].content if messages else ""

        if "objective:" in last_msg.lower():
            return AIMessage(content="ROUTE:planner")
        elif "planning" in last_msg.lower():
            return AIMessage(
                content='{"plan": ["Query buildings layer"], "reasoning": "Direct query"}'
            )
        elif "execute" in last_msg.lower() or "current step" in last_msg.lower():
            return AIMessage(
                content="Querying GIS data",
                tool_calls=[
                    {
                        "name": "query_geojson",
                        "args": {"layer": "buildings", "bbox": [10.0, 20.0, 30.0, 40.0]},
                        "id": "call_1",
                    }
                ],
            )
        elif "analy" in last_msg.lower():
            return AIMessage(
                content='{"summary": "Found buildings", "patterns": [], "risks": [], "recommendations": []}'
            )
        else:
            return AIMessage(content="APPROVE")

    with _patch_all_agents(mock_llm_factory):
        from geo_agents.graph import agent_graph

        state = create_initial_state("Map all buildings in the downtown area")
        result = await agent_graph.ainvoke(state)

        assert result["iteration"] > 0
        assert result["current_plan"] is not None
