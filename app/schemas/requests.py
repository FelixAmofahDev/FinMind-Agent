from __future__ import annotations

import re
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


UUID_PATTERN = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
CUID_PATTERN = re.compile(r"^c[a-z0-9]{24}$")


def generate_cuid() -> str:
    import secrets
    import string

    alphabet = string.ascii_lowercase + string.digits
    return "c" + "".join(secrets.choice(alphabet) for _ in range(24))


class AgentRequest(BaseModel):
    userId: Annotated[str, Field(min_length=1)]
    businessId: Annotated[str, Field(min_length=1)]
    conversationId: Annotated[str | None, Field(default=None, min_length=1)]
    message: Annotated[str, Field(min_length=1)]

    @field_validator("userId", "businessId")
    @classmethod
    def validate_uuid_ids(cls, value: str) -> str:
        if not UUID_PATTERN.fullmatch(value):
            raise ValueError("userId and businessId must be UUIDs")
        return value

    @field_validator("conversationId")
    @classmethod
    def validate_conversation_id(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not CUID_PATTERN.fullmatch(value):
            raise ValueError("conversationId must use the Prisma cuid format")
        return value
