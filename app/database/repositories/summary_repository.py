from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ConversationSummary


class SummaryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_conversation_id(self, conversation_id: str) -> Con