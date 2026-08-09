from __future__ import annotations

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.database.repositories.message_repository import MessageRepository
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def fetch_conversation_context(state: AgentState) -> AgentState:
    """Fetch recent messages for conversation context."""
    session: AsyncSession = state["session"]
    conversation_id = state["conversation_id"]

    try:
        repo = MessageRepository(session)
        messages = await repo.get_recent_by_conversation_id(conversation_id, limit=5)

        formatted_messages = []
        for msg in messages:
            role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            if role == "user":
                formatted_messages.append(HumanMessage(content=msg.content))
            elif role == "assistant":
                formatted_messages.append(AIMessage(content=msg.content))
            elif role == "system":
                formatted_messages.append(SystemMessage(content=msg.content))

        state["recent_messages"] = formatted_messages
        logger.debug(f"Fetched {len(formatted_messages)} recent messages for {conversation_id}")
    except Exception as e:
        logger.error(f"Error fetching conversation context: {e}")
        state["recent_messages"] = []

    return state
