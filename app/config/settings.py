from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from ai_agent/ root (2 levels up from app/config/)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "openai/gpt-oss-120b")
    BOOKKEEPING_LLM_MODEL_NAME: str = os.getenv("BOOKKEEPING_LLM_MODEL_NAME", "openai/gpt-oss-120b")
    CONVERSATION_LIMIT: int = int(os.getenv("CONVERSATION_LIMIT", 10))
    INTERNAL_SERVICE_KEY: str = os.getenv("INTERNAL_SERVICE_KEY", "")
    NODE_BACKEND_URL: str = os.getenv("NODE_BACKEND_URL", "https://localhost:3000")
    LLM_REASONING_EFFORT: str = os.getenv("LLM_REASONING_EFFORT", "low")



settings = Settings()
