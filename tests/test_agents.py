import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from geo_agents.state import create_initial_state


@pytest.fixture
def mock_llm_response():
    mock = AsyncMock()
    mock.ainvoke.return_value = MagicMock(
        content='{"plan": ["Step 1: Gather data", "Step 2: Analyze patterns"], "reasoning": "Systematic approach"}'
    )
    return mock


@pytest.fixture
def mock_executor_response():
    mock = MagicMock()
    llm_with_tools = MagicMock()
    llm_with_tools.ainvoke = AsyncMock(
        return_value=MagicMock(
            content='{"step_result": "Data gathered successfully", "tools_used": ["query_geojson"], "status": "complete"}',
            tool_calls=[],
        )
    )
    mock.bind_tools.return_value = llm_with_tools
    return mock


@pytest.fixture
def mock_analyst_response():
    mock = AsyncMock()
    mock.ainvoke.return_value = MagicMock(
        content='{"summary": "Analysis complete", "patterns": ["trend A"], "risks": [], "recommendations": ["Rec A"]}'
    )
    return mock


@pytest.fixture
def mock_supervisor_response():
    mock = AsyncMock()
    mock.ainvoke.return_value = MagicMock(content="APPROVE")
    return mock


@pytest.mark.asyncio
async def test_planner_node(mock_llm_response):
    with patch("geo_agents.agents.planner.get_llm", return_value=mock_llm_response):
        from geo_agents.agents.planner import planner_node

        state = create_initial_state("Analyze traffic around airports")
        result = await planner_node(state)
        assert result["active_agent"] == "planner"
        assert result["next_agent"] == "executor"
        assert result["current_plan"] is not None
        assert len(result["current_plan"]) > 0
        assert result["status"] == "executing"


@pytest.mark.asyncio
async def test_executor_node(mock_executor_response):
    with patch("geo_agents.agents.executor.get_llm", return_value=mock_executor_response):
        from geo_agents.agents.executor import executor_node

        state = create_initial_state("Test objective")
        state["current_plan"] = ["Step 1: Gather data", "Step 2: Analyze"]
        state["current_step"] = 0
        result = await executor_node(state)
        assert result["active_agent"] == "executor"
        assert result["current_step"] == 1
        assert result["status"] == "executing"


@pytest.mark.asyncio
async def test_executor_node_last_step(mock_executor_response):
    with patch("geo_agents.agents.executor.get_llm", return_value=mock_executor_response):
        from geo_agents.agents.executor import executor_node

        state = create_initial_state("Test objective")
        state["current_plan"] = ["Step 1: Gather data"]
        state["current_step"] = 0
        result = await executor_node(state)
        assert result["next_agent"] == "analyst"
        assert result["status"] == "analyzing"


@pytest.mark.asyncio
async def test_analyst_node(mock_analyst_response):
    with patch("geo_agents.agents.analyst.get_llm", return_value=mock_analyst_response):
        from geo_agents.agents.analyst import analyst_node

        state = create_initial_state("Test objective")
        state["execution_results"] = [{"tool": "query_geojson", "result": {"data": "test"}}]
        result = await analyst_node(state)
        assert result["active_agent"] == "analyst"
        assert result["next_agent"] == "supervisor"
        assert result["analysis_results"] is not None
        assert result["status"] == "reviewing"


@pytest.mark.asyncio
async def test_supervisor_approve(mock_supervisor_response):
    with patch("geo_agents.agents.supervisor.get_llm", return_value=mock_supervisor_response):
        from geo_agents.agents.supervisor import supervisor_node

        state = create_initial_state("Test objective")
        state["current_plan"] = ["Step 1"]
        state["current_step"] = 1
        state["execution_results"] = [{"tool": "test", "result": {}}]
        state["analysis_results"] = {"summary": "All good"}
        result = await supervisor_node(state)
        assert result["next_agent"] == "end"
        assert result["status"] == "complete"
        assert result["supervisor_approved"] is True


@pytest.mark.asyncio
async def test_supervisor_iteration_limit():
    from geo_agents.agents.supervisor import supervisor_node

    state = create_initial_state("Test objective")
    state["iteration"] = 100
    result = await supervisor_node(state)
    assert result["next_agent"] == "end"
    assert result["status"] == "complete"
    assert result["supervisor_approved"] is True
