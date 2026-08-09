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
    state["updated_conversation_state"] = {
        "currentTopic": "general",
        "currentIntent": "respond",
        "state": merge_entities({}, {}),
        "lastToolUsed": None,
        "lastToolResult": None,
    }
    state["updated_summary"] = "No summary yet"
    return state
