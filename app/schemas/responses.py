from __future__ import annotations

from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    reply: str = Field(..., description="Assistant reply")
    conversationId: str | None = Field(default=None)
