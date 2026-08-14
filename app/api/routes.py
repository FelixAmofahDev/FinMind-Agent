from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Header, status
from pydantic import BaseModel, Field, ValidationError

from app.config.settings import settings
from app.database.session import AsyncSessionFactory
from app.graph.graph import build_bookkeeping_graph, build_response_graph
from app.graph.state import AgentState
from app.schemas.requests import generate_cuid
from app.services.tool_http_client import ToolHttpClient

logger = logging.getLogger(__name__)

router = APIRouter()
response_graph = build_response_graph()
bookkeeping_graph = build_bookkeeping_graph()


class AskRequest(BaseModel):
    message: str = Field(..., min_length=1)
    businessId: str = Field(..., min_length=1)
    userId: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    conversationId: str | None = Field(default=None, min_length=1)


async def _run_bookkeeping(state: AgentState) -> None:
    """
    Runs update_summary + persist AFTER the response has already been
    sent back to the user.

    IMPORTANT: this must open its OWN database session. The session
    used for the main request (state["session"]) belongs to the
    `async with AsyncSessionFactory() as session:` block in
    invoke_agent, which has already closed by the time this background
    task runs — reusing it here would raise on a closed session.
    """
    try:
        async with AsyncSessionFactory() as session:
            state["session"] = session
            await bookkeeping_graph.ainvoke(state)
    except Exception:
        # This runs after the response was already returned, so there's
        # no request to fail — just log it. A failure here means the
        # conversation summary didn't update and/or the turn wasn't
        # persisted; worth alerting on if this shows up repeatedly.
        logger.exception(
            "Bookkeeping (update_summary/persist) failed for conversation %s",
            state.get("conversation_id"),
        )


@router.post("/ask", response_model=dict)
async def invoke_agent(
    request: AskRequest,
    background_tasks: BackgroundTasks,
    x_internal_service_key: str | None = Header(default=None, alias="X-Internal-Service-Key"),
) -> dict:
    if not x_internal_service_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-Internal-Service-Key header")

    if not settings.INTERNAL_SERVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL_SERVICE_KEY is not configured on the agent service",
        )

    if x_internal_service_key != settings.INTERNAL_SERVICE_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal service key")

    try:
        validated = AskRequest.model_validate(request.model_dump())
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from exc

    conversation_id = validated.conversationId or generate_cuid()
    tool_client = ToolHttpClient(
        user_id=validated.userId,
        business_id=validated.businessId,
        user_role=validated.role,
    )

    async with AsyncSessionFactory() as session:
        state: AgentState = {
            "user_message": validated.message,
            "user_id": validated.userId,
            "business_id": validated.businessId,
            "user_role": validated.role,
            "conversation_id": conversation_id,
            "internal_service_key": x_internal_service_key,
            "tool_http_client": tool_client,
            "session": session,
            "conversation_state": {},
            "state_is_sufficient": True,
            "recent_messages": [],
            "relevant_summary": None,
            "messages": [],
            "tool_name": None,
            "tool_calls": None,
            "tool_results": None,
            "llm_response": None,
            "updated_conversation_state": None,
            "updated_summary": None,
            "updated_topics": None,
            "is_new_conversation": None,
            "updated_title": None,
        }

        try:
            result = await response_graph.ainvoke(state)
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    # Summary generation (an extra LLM call) and DB persistence happen
    # AFTER the response is sent — the user doesn't need to wait on
    # bookkeeping to get their answer.
    background_tasks.add_task(_run_bookkeeping, result)

    return {"conversationId": conversation_id, "answer": result.get("llm_response", "")}