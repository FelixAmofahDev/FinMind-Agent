from __future__ import annotations

from app.graph.state import AgentState


def check_state_sufficiency(state: AgentState) -> AgentState:
    state["state_is_sufficient"] = bool(state.get("conversation_state"))
    return state
