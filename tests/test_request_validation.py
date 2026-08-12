import pytest
from pydantic import ValidationError

from app.schemas.requests import AgentRequest


def test_rejects_missing_or_malformed_ids():
    with pytest.raises(ValidationError):
        AgentRequest(
            userId="not-a-uuid",
            businessId="1234",
            conversationId="bad-id",
            message="hello",
            userRole="owner",
        )

    with pytest.raises(ValidationError):
        AgentRequest(
            userId="",
            businessId="11111111-1111-1111-1111-111111111111",
            conversationId="c123456789012345678901234",
            message="hello",
            userRole="owner",
        )


def test_rejects_invalid_user_role():
    with pytest.raises(ValidationError):
        AgentRequest(
            userId="11111111-1111-1111-1111-111111111111",
            businessId="22222222-2222-2222-2222-222222222222",
            message="hello",
            userRole="admin",
        )
