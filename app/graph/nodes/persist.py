from __future__ import annotations

import logging
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ConversationMessage, ConversationState
from app.database.repositories.message_repository import MessageRepository
from app.database.repositories.state_repository import StateRepository
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def persist(state: AgentState) -> AgentState:
    """Persist user message, assistant message, and updated conversation state."""
    session: AsyncSession = state["session"]
    conversation_id = state["conversation_id"]
    user_id = state["user_id"]
    user_message = state["user_message"]
    llm_response = state.get("llm_response", "")
    updated_state_dict = state.get("updated_conversation_state", {})

    try:
        # Save user message
        user_msg = ConversationMessage(
            id=str(uuid4()),
            conversationId=conversation_id,
            role="user",
            content=user_message,
            createdAt=datetime.utcnow(),
        )

        # Save assistant message
        assistant_msg = ConversationMessage(
            id=str(uuid4()),
            conversationId=conversation_id,
            role="assistant",
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
            # Update existing state
            existing_state.currentTopic = updated_state_dict.get("currentTopic")
            existing_state.currentIntent = updated_state_dict.get("currentIntent")
            existing_state.state = updated_state_dict.get("state", {})
            existing_state.lastToolUsed = updated_state_dict.get("lastToolUsed")
            existing_state.lastToolResult = updated_state_dict.get("lastToolResult")
            existing_state.updatedAt = datetime.utcnow()
        else:
            # Create new state
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

        # Commit all changes in a single transaction
        await session.commit()
        logger.info(f"Persisted messages and state for conversation {conversation_id}")
    except Exception as e:
        await session.rollback()
        logger.error(f"Error persisting conversation data: {e}")
        raise

    return state
