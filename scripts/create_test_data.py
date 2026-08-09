from __future__ import annotations

import asyncio
import os
import sys
from uuid import uuid4

import asyncpg
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    conn = await asyncpg.connect(database_url.replace("postgresql+asyncpg://", "postgresql://"))
    try:
        # Create business first (if needed)
        business = await conn.fetchrow('SELECT "id" FROM "businesses" WHERE "name" = $1', "FinMind Agent Test Business")
        if not business:
            business_id = str(uuid4())
            await conn.execute(
                'INSERT INTO "businesses" ("id", "name", "type", "ownerName", "phoneNumber", "locationRegion", "locationDistrict", "recordingMode", "tier", "currency", "isActive", "onboardingComplete", "createdAt", "updatedAt") VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, true, true, NOW(), NOW())',
                business_id,
                "FinMind Agent Test Business",
                "provision_store",
                "Agent Owner",
                "0550000000",
                "Greater Accra",
                "Accra",
                "daily_summary",
                "tier1",
                "GHS",
            )
        else:
            business_id = str(business["id"])

        # Create user with the business ID
        user = await conn.fetchrow('SELECT "id" FROM "users" WHERE "email" = $1', "agent-test@finmind.dev")
        if not user:
            user_id = str(uuid4())
            await conn.execute(
                'INSERT INTO "users" ("id", "businessId", "fullName", "email", "phoneNumber", "passwordHash", "role", "createdAt", "updatedAt") VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())',
                user_id,
                business_id,
                "Agent Test",
                "agent-test@finmind.dev",
                None,
                "test-hash",
                "owner",
            )
        else:
            user_id = str(user["id"])

        conversation = await conn.fetchrow('SELECT "id" FROM "conversations" WHERE "userId" = $1 AND "businessId" = $2', user_id, business_id)
        if not conversation:
            conversation_id = "c" + "a" * 24
            await conn.execute(
                'INSERT INTO "conversations" ("id", "userId", "businessId", "title", "status", "createdAt", "updatedAt") VALUES ($1, $2, $3, $4, $5, NOW(), NOW())',
                conversation_id,
                user_id,
                business_id,
                "FinMind Agent Test Conversation",
                "active",
            )
        else:
            conversation_id = str(conversation["id"])

        print(f"USER_ID={user_id}")
        print(f"BUSINESS_ID={business_id}")
        print(f"CONVERSATION_ID={conversation_id}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
