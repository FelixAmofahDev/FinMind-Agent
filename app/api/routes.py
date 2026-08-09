from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from app.database.session import AsyncSessionFactory
from app.graph.graph import build_graph
from app.schemas.requests import AgentRequest
from app.schemas.responses import AgentResponse

router = APIRouter()
graph = build_graph()


@router.post("/agent", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest) -> AgentResponse:
    try:
        validated = AgentRequest.model_validate(request.model_dump())
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from exc

    # Create a session for this request
    async with AsyncSessionFactory() as session:
        state = {
            "user_message": validated.message,
            "user_id": validated.userId,
            "business_id": validated.businessId,
            "conversation_id": validated.conversationId,
            "session": session,  # Pass session through state for repository access
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

        try:
            result = await graph.ainvoke(state)
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return AgentResponse(reply=result.get("llm_response", ""), conversationId=validated.conversationId)
