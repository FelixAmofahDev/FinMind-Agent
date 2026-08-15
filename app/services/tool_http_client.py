from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config.settings import settings

logger = logging.getLogger(__name__)


class ToolHttpClient:
    def __init__(
        self,
        user_id: str,
        business_id: str,
        user_role: str,
        base_url: str | None = None,
    ) -> None:
        self._user_id = user_id
        self._business_id = business_id
        self._user_role = user_role
        self._base_url = (base_url or settings.NODE_BACKEND_URL).rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "x-internal-service-key": settings.INTERNAL_SERVICE_KEY,
            "x-on-behalf-of-business": self._business_id,
            "x-on-behalf-of-user": self._user_id,
            "x-on-behalf-of-role": self._user_role,
        }

    async def invoke_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        url = f"{self._base_url}/internal/{tool_name}"
        headers = self._headers()

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(url, params=arguments, headers=headers)
            print(response)
        if response.status_code == 401:
            logger.error("Tool endpoint rejected internal service key")
            return {"error": "Unauthorized access to financial service."}
        if response.status_code == 403:
            logger.error("Tool endpoint rejected role authorization")
            return {"error": "You don't have permission to access this information."}
        if response.status_code == 422:
            logger.error("Tool endpoint validation failed: %s", response.text)

        if response.status_code != 200:
            logger.error("Tool endpoint error %s: %s", response.status_code, response.text)

        try:
            body = response.json()
            if isinstance(body, dict) and body.get("success") is False:
                message = body.get("message") or "An error occurred while processing your request."
                logger.error("Tool endpoint returned business error: %s", message)
                return {"error": message}
            if isinstance(body, dict) and "data" in body:
                return body["data"]
            return body
        except Exception as exc:
            logger.error("Failed to parse tool response: %s", exc)
            return {"error": "Invalid response from tool endpoint"}
