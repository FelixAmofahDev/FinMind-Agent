from __future__ import annotations

from app.graph.state import AgentState


def build_context(state: AgentState) -> AgentState:
    state["llm_context"] = (
        f"User message: {state['user_message']}\n"
        f"Conversation state: {state.get('conversation_state', {})}\n"
        f"Recent messages: {state.get('recent_messages', [])}\n"
        f"Summary: {state.get('relevant_summary')}"
    )
    return state
