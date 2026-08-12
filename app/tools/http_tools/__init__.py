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


async def _get_profit_report_impl(
    client: ToolHttpClient,
    from_date: str,
    to_date: str,
) -> dict:
    return await client.invoke_tool(
        "reports/profit-loss",
        {"from": from_date, "to": to_date},
    )


get_profit_report = StructuredTool(
    name="get_profit_report",
    description=(
        "Return the profit and loss report for a date range. "
        "Use this when the user asks about profit, revenue, expenses, or net income. "
        "Requires from_date and to_date in YYYY-MM-DD format."
    ),
    coroutine=_get_profit_report_impl,
    args_schema=ProfitLossInput,
)


async def _get_cash_position_impl(client: ToolHttpClient) -> dict:
    return await client.invoke_tool("reports/cash-position", {})


get_cash_position = StructuredTool(
    name="get_cash_position",
    description=(
        "Return the current cash position — balances across all money accounts "
        "(cash in hand, mobile money, bank) with a grand total. "
        "Use this when the user asks about available money, cash on hand, or account balances. "
        "No parameters needed."
    ),
    coroutine=_get_cash_position_impl,
    args_schema=None,
)


async def _get_debtors_summary_impl(client: ToolHttpClient) -> dict:
    return await client.invoke_tool("reports/debtors-summary", {})


get_debtors_summary = StructuredTool(
    name="get_debtors_summary",
    description=(
        "Return a summary of all customers who owe the business money. "
        "Shows total owed, count, overdue count, and per-debtor breakdown. "
        "Use this when the user asks who owes them money, outstanding debts, or debtors. "
        "No parameters needed."
    ),
    coroutine=_get_debtors_summary_impl,
    args_schema=None,
)


async def _get_creditors_summary_impl(client: ToolHttpClient) -> dict:
    return await client.invoke_tool("reports/creditors-summary", {})


get_creditors_summary = StructuredTool(
    name="get_creditors_summary",
    description=(
        "Return a summary of all suppliers the business owes money to. "
        "Shows total owed, count, overdue count, and per-creditor breakdown. "
        "Use this when the user asks who they owe, creditors, or payables. "
        "No parameters needed."
    ),
    coroutine=_get_creditors_summary_impl,
    args_schema=None,
)


class ProductSearchInput(BaseModel):
    search: str = Field(description="Product name or keyword to search for")
    categoryId: str | None = Field(
        default=None,
        description="Filter by category UUID (optional)",
    )
    isActive: str | None = Field(
        default=None,
        description="Filter by active status: 'true' for active, 'false' for deactivated (optional)",
    )


async def _list_products_impl(
    client: ToolHttpClient,
    search: str | None = None,
    categoryId: str | None = None,
    isActive: str | None = None,
) -> dict:
    arguments: dict[str, Any] = {}
    if search is not None:
        arguments["search"] = search
    if categoryId is not None:
        arguments["categoryId"] = categoryId
    if isActive is not None:
        arguments["isActive"] = isActive
    return await client.invoke_tool("products", arguments)


list_products = StructuredTool(
    name="list_products",
    description=(
        "Return the product catalogue. Use this when the user asks about products, "
        "stock items, inventory catalogue, or wants to look up a product. "
        "All parameters are optional — omit them to get all active products."
    ),
    coroutine=_list_products_impl,
    args_schema=ProductSearchInput,
)


async def _list_users_impl(client: ToolHttpClient) -> dict:
    return await client.invoke_tool("users", {})


list_users = StructuredTool(
    name="list_users",
    description=(
        "Return all users in the current business. "
        "Use this when the user asks about staff, team members, employees, or who has access. "
        "Owner and manager roles only. No parameters needed."
    ),
    coroutine=_list_users_impl,
    args_schema=None,
)


async def _get_business_profile_impl(client: ToolHttpClient) -> dict:
    return await client.invoke_tool("business", {})


get_business_profile = StructuredTool(
    name="get_business_profile",
    description=(
        "Return the business profile — name, type, location, tier, and onboarding status. "
        "Use this when the user asks about their business details or profile. "
        "No parameters needed."
    ),
    coroutine=_get_business_profile_impl,
    args_schema=None,
)


async def _get_my_profile_impl(client: ToolHttpClient) -> dict:
    return await client.invoke_tool("me", {})


get_my_profile = StructuredTool(
    name="get_my_profile",
    description=(
        "Return the current user's profile — name, email, phone, role, and account status. "
        "Use this when the user asks about their own profile, account, or user details. "
        "No parameters needed."
    ),
    coroutine=_get_my_profile_impl,
    args_schema=None,
)
