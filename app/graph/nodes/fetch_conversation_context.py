from __future__ import annotations

from app.graph.state import AgentState


def fetch_conversation_context(state: AgentState) -> AgentState:
    state["recent_messages"] = []
    return state
