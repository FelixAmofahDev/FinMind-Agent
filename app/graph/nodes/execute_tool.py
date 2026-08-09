from __future__ import annotations

from app.graph.state import AgentState


def execute_tool(state: AgentState) -> AgentState:
    state["tool_result"] = {"status": "mock"}
    return state
