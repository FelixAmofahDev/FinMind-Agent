from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.graph.state import AgentState


def build_context(state: AgentState) -> AgentState:
    summary = state.get("relevant_summary")
    summary_text = summary.get("summary") if isinstance(summary, dict) else ""
    conversation_state = state.get("conversation_state", {})

    system_content = (
        "You are an accounting assistant for a business.\n"
        f"Summary: {summary_text or 'No summary yet.'}\n"
        f"Conversation state: {conversation_state}"
    )

    messages = [SystemMessage(content=system_content)]

    for msg in state.get("recent_messages", []):
        if isinstance(msg, HumanMessage):
            messages.append(msg)
        elif isinstance(msg, AIMessage):
            messages.append(msg)
        elif isinstance(msg, SystemMessage):
            messages.append(msg)

    messages.append(HumanMessage(content=state["user_message"]))

    state["messages"] = messages
    return state
