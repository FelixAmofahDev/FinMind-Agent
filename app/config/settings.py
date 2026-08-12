from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from ai_agent/ root (2 levels up from app/config/)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    INTERNAL_SERVICE_KEY: str = os.getenv("INTERNAL_SERVICE_KEY", "")
    NODE_BACKEND_URL: str = os.getenv("NODE_BACKEND_URL", "https://localhost:3000")


settings = Settings()
