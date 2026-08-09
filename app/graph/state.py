from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict):
    user_message: str
    user_id: str
    business_id: str
    conversation_id: str

    conversation_state: dict
    state_is_sufficient: bool

    recent_messages: list
    relevant_summary: dict | None

    tool_needed: bool
    tool_name: str | None
    tool_result: dict | None

    llm_context: str
    llm_response: str | None

    updated_conversation_state: dict | None
    updated_summary: str | None
