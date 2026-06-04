from typing import TypedDict, Literal, Annotated
from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    objective: str
    current_plan: list[str] | None
    current_step: int
    active_agent: Literal["planner", "executor", "analyst", "supervisor"]
    next_agent: Literal["planner", "executor", "analyst", "end"] | None
    execution_results: list[dict]
    analysis_results: dict | None
    status: Literal["planning", "executing", "analyzing", "reviewing", "complete", "error"]
    supervisor_approved: bool
    error: str | None
    iteration: int


def create_initial_state(objective: str) -> AgentState:
    """Create a fresh AgentState with sensible defaults."""
    return AgentState(
        messages=[],
        objective=objective,
        current_plan=None,
        current_step=0,
        active_agent="supervisor",
        next_agent=None,
        execution_results=[],
        analysis_results=None,
        status="planning",
        supervisor_approved=False,
        error=None,
        iteration=0,
    )
