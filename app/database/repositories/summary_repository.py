from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ConversationSummary


class SummaryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_conversation_id(self, conversation_id: str) -> ConversationSummary | None:
        """Fetch the summary for a conversation."""
        result = await self.session.execute(
            select(ConversationSummary).where(ConversationSummary.conversationId == conversation_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, summary: ConversationSummary) -> None:
        """Insert or update a ConversationSummary."""
        self.session.add(summary)
