# app/schemas/conversation_extraction.py
from __future__ import annotations
from pydantic import BaseModel, Field


class ConversationExtraction(BaseModel):
    summary: str = Field(description="Updated running summary of the conversation.")
    currentTopic: str = Field(description="Short label (1-3 words) for what this turn is about.")
    currentIntent: str = Field(description="Short label (1-3 words) for what the user is trying to do.")
    entities_json: str = Field(
        description=(
            "A JSON-encoded object (as a string) of entity values worth remembering for future "
            "turns, e.g. '{\"businessName\": \"Acme\", \"location\": \"Accra\"}'. Must be valid "
            "JSON. Use '{}' if there is nothing new to remember."
        )
    )


class ConversationExtractionWithTitle(ConversationExtraction):
    title: str = Field(description="Short 3-6 word title for this conversation. No quotes, no trailing punctuation.")