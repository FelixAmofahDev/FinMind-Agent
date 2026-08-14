from __future__ import annotations

from copy import deepcopy

from app.graph.state import AgentState


def merge_entities(existing_state: dict, incoming_state: dict) -> dict:
    existing_entities = existing_state.get("entities", {})
    incoming_entities = incoming_state.get("entities", {})
    merged = deepcopy(existing_entities)

    for key, value in incoming_entities.items():
        merged[key] = value

    return {"entities": merged}


def update_state(state: AgentState) -> AgentState:
    """
    Deterministic seed for `updated_conversation_state`, run in the response
    graph right after call_llm finishes.

    - lastToolUsed / lastToolResult are computed here deterministically —
      they don't need an LLM.
    - currentTopic / currentIntent / entities are carried forward unchanged
      from the previously persisted state. update_summary (bookkeeping
      graph) is responsible for actually updating them via LLM extraction,
      after the response has already been sent to the user.

    This means: if the bookkeeping LLM call fails for any reason, persist.py
    still has a coherent, non-null conversation state to write — just a
    stale one — rather than nulls or a crash.
    """
    existing_state = state.get("conversation_state") or {}
    tool_name = state.get("tool_name")
    tool_results = state.get("tool_results") or {}
    last_tool_result = tool_results.get(tool_name) if tool_name else None

    state["updated_conversation_state"] = {
        "currentTopic": existing_state.get("currentTopic", "general"),
        "currentIntent": existing_state.get("currentIntent", "respond"),
        "state": {"entities": deepcopy(existing_state.get("entities", {}))},
        "lastToolUsed": tool_name or existing_state.get("lastToolUsed"),
        "lastToolResult": last_tool_result or existing_state.get("lastToolResult"),
    }
    return state