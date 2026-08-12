from __future__ import annotations

import logging
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.services.tool_http_client import ToolHttpClient

logger = logging.getLogger(__name__)


class ProfitLossInput(BaseModel):
    from_date: str = Field(description="Start date in YYYY-MM-DD format")
    to_date: str = Field(description="End date in YYYY-MM-DD format")


async def _get_profit_report_impl(client: ToolHttpClient, from_date: str, to_date: str) -> dict:
    return await client.invoke_tool(
        "reports/profit-loss",
        {"from": from_date, "to": to_date},
    )


get_profit_report = StructuredTool(
    name="get_profit_report",
    description="Return the profit and loss report for a date range. Requires from_date and to_date in YYYY-MM-DD format.",
    coroutine=_get_profit_report_impl,
    args_schema=ProfitLossInput,
)


class ProductSearchInput(BaseModel):
    search: str = Field(description="Product name or keyword to search for")


async def _get_inventory_status_impl(client: ToolHttpClient, search: str) -> dict:
    return await client.invoke_tool(
        "products",
        {"search": search},
    )


get_inventory_status = StructuredTool(
    name="get_inventory_status",
    description="Return product inventory details. Search by product name or keyword.",
    coroutine=_get_inventory_status_impl,
    args_schema=ProductSearchInput,
)


async def _get_business_name_impl(client: ToolHttpClient) -> dict:
    return await client.invoke_tool("business", {})


get_business_name = StructuredTool(
    name="get_business_name",
    description="Return the registered name and profile of the business.",
    coroutine=_get_business_name_impl,
    args_schema=None,
)
