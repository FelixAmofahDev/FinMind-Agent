from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ConversationState


class StateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_conversation_id(self, conversation_id: str) -> ConversationState | None:
        """Fetch the current ConversationState for a conversation."""
        result = await self.session.execute(
            select(ConversationState).where(ConversationState.conversationId == conversation_id)
        )
        return result.scalar_one_or_none()

 