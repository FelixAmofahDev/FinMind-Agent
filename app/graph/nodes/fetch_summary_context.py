from __future__ import annotations

from app.graph.state import AgentState


def fetch_summary_context(state: AgentState) -> AgentState:
    state["relevant_summary"] = None
    return state
