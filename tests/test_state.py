import pytest
from geo_agents.state import create_initial_state, AgentState


def test_create_initial_state():
    state = create_initial_state("Test objective")
    assert state["objective"] == "Test objective"
    assert state["current_plan"] is None
    assert state["current_step"] == 0
    assert state["active_agent"] == "supervisor"
    assert state["next_agent"] is None
    assert state["execution_results"] == []
    assert state["analysis_results"] is None
    assert state["status"] == "planning"
    assert state["supervisor_approved"] is False
    assert state["error"] is None
    assert state["iteration"] == 0


def test_state_is_dict():
    state = create_initial_state("test")
    assert isinstance(state, dict)


def test_state_messages_is_list():
    state = create_initial_state("test")
    assert isinstance(state["messages"], list)


def test_create_initial_state_different_objectives():
    s1 = create_initial_state("objective A")
    s2 = create_initial_state("objective B")
    assert s1["objective"] != s2["objective"]
    assert s1["iteration"] == s2["iteration"] == 0
