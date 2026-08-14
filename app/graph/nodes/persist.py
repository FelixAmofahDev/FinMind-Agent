from __future__ import annotations

import logging
import re
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Conversation, ConversationMessage, ConversationMessageRole, ConversationState, ConversationSummary
from app.database.repositories.conversation_repository import ConversationRepository
from app.database.repositories.message_repository import MessageRepository
from app.database.repositories.state_repository import StateRepository
from app.database.repositories.summary_repository import SummaryRepository
from app.graph.state import AgentState

logger = logging.getLogger(__name__)




def _fallback_title(text: str, max_chars: int = 60) -> str:
    """Deterministic backstop, used only if the LLM didn't produce a title
    (e.g. update_summary failed) so a conversation is never left untitled."""
    text = re.sub(r"\s+", " ", text).strip()
    for sep in [".", "!", "?", "\n"]:
        if sep in text:
            text = text.split(sep)[0] + sep
            break
    return text[:max_chars].strip()

async def persist(state: AgentState) -> AgentState:
    """Persist user message, assistant message, conversation, state, and summary."""
    session: AsyncSession = state["session"]
    conversation_id = state["conversation_id"]
    user_id = state["user_id"]
    business_id = state.get("business_id")
    user_message = state["user_message"]
    llm_response = state.get("llm_response", "")
    updated_state_dict = state.get("updated_conversation_state") or {}
    updated_summary = state.get("updated_summary")
    updated_topics = state.get("updated_topics") or {}
    updated_title = state.get("updated_title")


    try:
        conversation_repo = ConversationRepository(session)
        conversation = await conversation_repo.get_by_id(conversation_id)

        if not conversation:
            conversation = Conversation(
                id=conversation_id,
                userId=user_id,
                businessId=business_id,
                title=updated_title or _fallback_title(user_message),
                status="active",
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow(),
            )
            session.add(conversation)
            await session.flush()
        elif not conversation.title:
            conversation.title = updated_title or _fallback_title(user_message)
            conversation.updatedAt = datetime.utcnow()
            print(f"conversation title: {state.get("updated_title")}")

        # Save user message
        user_msg = ConversationMessage(
            id=str(uuid4()),
            conversationId=conversation_id,
            role=ConversationMessageRole.user,
            content=user_message,
            createdAt=datetime.utcnow(),
        )

        # Save assistant message
        assistant_msg = ConversationMessage(
            id=str(uuid4()),
            conversationId=conversation_id,
            role=ConversationMessageRole.assistant,
            content=llm_response,
            createdAt=datetime.utcnow(),
        )

        msg_repo = MessageRepository(session)
        await msg_repo.add_message(user_msg)
        await msg_repo.add_message(assistant_msg)

        # Update or create conversation state
        state_repo = StateRepository(session)
        existing_state = await state_repo.get_by_conversation_id(conversation_id)

        if existing_state:
            if updated_state_dict:
                existing_state.currentTopic = updated_state_dict.get("currentTopic", existing_state.currentTopic)
                existing_state.currentIntent = updated_state_dict.get("currentIntent", existing_state.currentIntent)
                existing_state.state = updated_state_dict.get("state", existing_state.state)
                existing_state.lastToolUsed = updated_state_dict.get("lastToolUsed", existing_state.lastToolUsed)
                existing_state.lastToolResult = updated_state_dict.get("lastToolResult", existing_state.lastToolResult)
            existing_state.updatedAt = datetime.utcnow()
        else:
            new_state = ConversationState(
                id=str(uuid4()),
                conversationId=conversation_id,
                currentTopic=updated_state_dict.get("currentTopic"),
                currentIntent=updated_state_dict.get("currentIntent"),
                state=updated_state_dict.get("state", {}),
                lastToolUsed=updated_state_dict.get("lastToolUsed"),
                lastToolResult=updated_state_dict.get("lastToolResult"),
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow(),
            )
            await state_repo.upsert(new_state)

        # Update or create conversation summary
        if updated_summary is not None:
            summary_repo = SummaryRepository(session)
            existing_summary = await summary_repo.get_by_conversation_id(conversation_id)

            if existing_summary:
                existing_summary.summary = updated_summary
                existing_summary.topics = updated_topics
                existing_summary.updatedAt = datetime.utcnow()
            else:
                new_summary = ConversationSummary(
                    id=str(uuid4()),
                    conversationId=conversation_id,
                    summary=updated_summary,
                    topics=updated_topics,
                    createdAt=datetime.utcnow(),
                    updatedAt=datetime.utcnow(),
                )
                await summary_repo.upsert(new_summary)

        # Commit all changes in a single transaction
        await session.commit()
        logger.info(f"Persisted messages, state, and summary for conversation {conversation_id}")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error persisting conversation data: {e}")
        raise

    return state
