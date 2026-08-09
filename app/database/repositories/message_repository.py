from __future__ import annotations

from datetime import datetime
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ConversationMessage


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_message(self, message: ConversationMessage) -> None:
        """Add a new message to the conversation."""
        self.session.add(message)

    async def get_recent_by_conversation_id(self, conversation_id: str, limit: int = 5) -> list[ConversationMessage]:
        """Fetch recent messages for a conversation (most recent first)."""
        result = await self.session.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversationId == conversation_id)
            .order_by(desc(ConversationMessage.createdAt))
            .limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # Return in chronological order (oldest first)

    async def get_all_by_conversation_id(self, conversation_id: str) -> list[ConversationMessage]:
        """Fetch all messages for a conversation in chronological order."""
        result = await self.session.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversationId == conversation_id)
            .order_by(ConversationMessage.createdAt)
        )
        return list(result.scalars().all())
