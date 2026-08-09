from __future__ import annotations

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.state_repository import StateRepository
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def load_state(state: AgentState) -> AgentState:
    """Load the current ConversationState from the database."""
    session: AsyncSession = state["session"]
    conversation_id = state["conversation_id"]

    try:
        repo = StateRepository(session)
        conversation_state = await repo.get_by_conversation_id(conversation_id)

        if conversation_state:
            state["conversation_state"] = {
                "currentTopic": conversation_state.currentTopic,
                "currentIntent": conversation_state.currentIntent,
                "entities": conversation_state.state.get("entities", {}),
                "lastToolUsed": conversation_state.lastToolUsed,
                "lastToolResult": conversation_state.lastToolResult,
            }
            logger.debug(f"Loaded conversation state for {conversation_id}")
        else:
            state["conversation_state"] = {}
            logger.debug(f"No existing conversation state for {conversation_id}")
    except Exception as e:
        logger.error(f"Error loading conversation state: {e}")
        state["conversation_state"] = {}

    return state
