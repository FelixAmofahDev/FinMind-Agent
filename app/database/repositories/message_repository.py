from __future__ import annotations

from datetime import datetime
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ConversationMessage


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_message(self, message