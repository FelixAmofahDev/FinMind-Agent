from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    # Request context
    user_message: str
    user_id: str
    business_id: str
    conversation_id: str
    session: Any  # AsyncSession from SQLAlchemy

    # State and context
    conversation_state: dict
    state_is_sufficient: bool
    recent_messages: list
    relevant_summary: dict | None

    # Tool execution
    tool_needed: bool
    tool_name: str | None
    tool_result: dict | None

    # LLM
    llm_context: str
    llm_response: str | None

    # Output
    updated_conversation_state: dict | None
    updated_summary: str | None
