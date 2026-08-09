from __future__ import annotations

from app.graph.state import AgentState


def load_state(state: AgentState) -> AgentState:
    state["conversation_state"] = {}
    state["state_is_sufficient"] = True
    return state
