from __future__ import annotations

from app.graph.state import AgentState


def plan_tool(state: AgentState) -> AgentState:
    state["tool_needed"] = False
    state["tool_name"] = None
    return state
