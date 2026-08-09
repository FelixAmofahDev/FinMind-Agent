from app.graph.state import AgentState


def test_state_has_expected_keys():
    state: AgentState = {
        "user_message": "hello",
        "user_id": "11111111-1111-1111-1111-111111111111",
        "business_id": "22222222-2222-2222-2222-222222222222",
        "conversation_id": "c123456789012345678901234",
        "conversation_state": {},
        "state_is_sufficient": True,
        "recent_messages": [],
        "relevant_summary": None,
        "tool_needed": False,
        "tool_name": None,
        "tool_result": None,
        "llm_context": "",
        "llm_response": None,
        "updated_conversation_state": None,
        "updated_summary": None,
    }

    assert state["user_message"] == "hello"
    assert state["state_is_sufficient"] is True
