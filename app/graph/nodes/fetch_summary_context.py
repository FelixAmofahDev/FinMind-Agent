from __future__ import annotations

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.summary_repository import SummaryRepository
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


async def fetch_summary_context(state: AgentState) -> AgentState:
    """Fetch conversation summary if it exists."""
    session: AsyncSession = state["session"]
    conversation_id = state["conversation_id"]

    try:
        repo = SummaryRepository(session)
        summary = await repo.get_by_conversation_id(conversation_id)

        if summary:
            state["relevant_summary"] = {
                "summary": summary.summary,
                "topics": summary.topics,
            }
            logger.debug(f"Loaded summary for {conversation_id}")
        else:
            state["relevant_summary"] = None
            logger.debug(f"No summary found for {conversation_id}")
    except Exception as e:
        logger.error(f"Error fetching summary context: {e}")
        state["relevant_summary"] = None

    return state
