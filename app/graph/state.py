from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    # Request context
    user_message: str
    user_id: str
    business_id: str
    user_role: str
    conversation_id: str
    internal_service_key: str
    tool_http_client: Any  # ToolHttpClient instance bound to the current request identity
    session: Any  # AsyncSession from SQLAlchemy

    # State and context
    conversation_state: dict
    state_is_sufficient: bool
    recent_messages: list
    relevant_summary: dict | None
    messages: list

    # Tool execution
    tool_name: str | None
    tool_calls: list | None
    tool_results: dict | None

    # LLM
    llm_response: str | None

    # Output
    updated_conversation_state: dict | None
    updated_summary: str | None
    updated_topics: dict | None
