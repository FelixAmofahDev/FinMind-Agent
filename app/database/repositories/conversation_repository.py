from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Conversation


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, conversation_id: str) -> Conversation | None:
        result = await self.session.execute(select(Conversation).where(Conversation.id == conversation_id))
        return result.scalar_one_or_none()
