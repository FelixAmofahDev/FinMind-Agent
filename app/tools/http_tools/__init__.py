from __future__ import annotations

import logging
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.services.tool_http_client import ToolHttpClient

logger = logging.getLogger(__name__)


# ============================================================
# Input Schemas
# ============================================================

class ProfitLossInput(BaseModel):
    from_date: str = Field(
        description="Start date in YYYY-MM-DD format"
    )
    to_date: str = Field(
        description="End date in YYYY-MM-DD format"
    )


class ProductSearchInput(BaseModel):
    search: str | None = Field(
        default=None,
        description="Product name or keyword to search for"
    )
    categoryId: str | None = Field(
        default=None,
        description="Filter by category UUID (optional)"
    )
    isActive: str | None = Field(
        default=None,
        description="Filter by active status: 'true' for active, 'false' for deactivated (optional)"
    )


class ExpenseFilterInput(BaseModel):
    category: str | None = Field(
        default=None,
        description="Filter by expense category, e.g. rent, wages, transport"
    )
    from_date: str | None = Field(
        default=None,
        description="Start date in YYYY-MM-DD format"
    )
    to_date: str | None = Field(
        default=None,
        description="End date in YYYY-MM-DD format"
    )


class DateRangeInput(BaseModel):
    from_date: str | None = Field(
        default=None,
        description="Start date in YYYY-MM-DD format (optional)"
    )
    to_date: str | None = Field(
        default=None,
        description="End date in YYYY-MM-DD format (optional)"
    )


class NoInput(BaseModel):
    """Schema for tools that take no arguments at all.

    Newer langchain_core versions require every StructuredTool to
    have an explicit args_schema — it no longer infers an empty one
    for zero-argument tools automatically. This model exists purely
    to satisfy that requirement.
    """
    pass


# ============================================================
# Tool Factory
# ============================================================
#
# IMPORTANT:
#
# The ToolHttpClient is injected here.
#
# The LLM NEVER receives the client as a tool argument.
#
# Example:
#
#     client = ToolHttpClient(...)
#     tools = create_tools(client)
#
# The tools then internally use the client.
#
# ============================================================

def create_tools(client: ToolHttpClient) -> list[StructuredTool]:

    # ========================================================
    # PROFIT & LOSS
    # ========================================================

    async def get_profit_report_impl(
        from_date: str,
        to_date: str,
    ) -> dict[str, Any]:

        return await client.invoke_tool(
            "reports/profit-loss",
            {
                "from": from_date,
                "to": to_date,
            },
        )

    get_profit_report = StructuredTool(
        name="get_profit_report",
        description=(
            "Return the profit and loss report for a date range. "
            "Use this when the user asks about profit, revenue, expenses, "
            "costs, or net income. "
            "Requires from_date and to_date in YYYY-MM-DD format."
        ),
        coroutine=get_profit_report_impl,
        args_schema=ProfitLossInput,
    )

    # ========================================================
    # CASH POSITION
    # ========================================================

    async def get_cash_position_impl() -> dict[str, Any]:

        return await client.invoke_tool(
            "reports/cash-position",
            {},
        )

    get_cash_position = StructuredTool(
        name="get_cash_position",
        description=(
            "Return the current cash position across all money accounts, "
            "including cash in hand, mobile money, and bank accounts, "
            "with the grand total. "
            "Use this when the user asks about available money, "
            "cash on hand, or account balances. "
            "No parameters are required."
        ),
        coroutine=get_cash_position_impl,
        args_schema=NoInput,
    )

    # ========================================================
    # DEBTORS
    # ========================================================

    async def get_debtors_summary_impl() -> dict[str, Any]:

        return await client.invoke_tool(
            "reports/debtors-summary",
            {},
        )

    get_debtors_summary = StructuredTool(
        name="get_debtors_summary",
        description=(
            "Return a summary of all customers who owe the business money. "
            "Shows total owed, count, overdue count, and per-debtor breakdown. "
            "Use this when the user asks who owes them money, outstanding "
            "debts, or debtors. "
            "No parameters are required."
        ),
        coroutine=get_debtors_summary_impl,
        args_schema=NoInput,
    )

    # ========================================================
    # CREDITORS
    # ========================================================

    async def get_creditors_summary_impl() -> dict[str, Any]:

        return await client.invoke_tool(
            "reports/creditors-summary",
            {},
        )

    get_creditors_summary = StructuredTool(
        name="get_creditors_summary",
        description=(
            "Return a summary of all suppliers the business owes money to. "
            "Shows total owed, count, overdue count, and per-creditor breakdown. "
            "Use this when the user asks who they owe, creditors, or payables. "
            "No parameters are required."
        ),
        coroutine=get_creditors_summary_impl,
        args_schema=NoInput,
    )

    # ========================================================
    # PRODUCTS
    # ========================================================

    async def list_products_impl(
        search: str | None = None,
        categoryId: str | None = None,
        isActive: str | None = None,
    ) -> dict[str, Any]:

        arguments: dict[str, Any] = {}

        if search is not None:
            arguments["search"] = search

        if categoryId is not None:
            arguments["categoryId"] = categoryId

        if isActive is not None:
            arguments["isActive"] = isActive

        return await client.invoke_tool(
            "products",
            arguments,
        )

    list_products = StructuredTool(
        name="list_products",
        description=(
            "Return the product catalogue. "
            "Use this when the user asks about products, stock items, "
            "inventory catalogue, or wants to look up a product. "
            "All parameters are optional. "
            "Omit them to get all active products."
        ),
        coroutine=list_products_impl,
        args_schema=ProductSearchInput,
    )

    # ========================================================
    # USERS
    # ========================================================

    async def list_users_impl() -> dict[str, Any]:

        return await client.invoke_tool(
            "users",
            {},
        )

    list_users = StructuredTool(
        name="list_users",
        description=(
            "Return all users in the current business, including the owner "
            "and staff. "
            "Use this when the user asks about staff, team members, "
            "employees, or who has access. "
            "Owner and manager roles only. "
            "No parameters are required."
        ),
        coroutine=list_users_impl,
        args_schema=NoInput,
    )

    # ========================================================
    # BUSINESS PROFILE
    # ========================================================

    async def get_business_profile_impl() -> dict[str, Any]:

        return await client.invoke_tool(
            "business",
            {},
        )

    get_business_profile = StructuredTool(
        name="get_business_profile",
        description=(
            "Return the business profile, including business name, type, "
            "location, tier, and onboarding status. "
            "Use this when the user asks about their business details "
            "or profile. "
            "No parameters are required."
        ),
        coroutine=get_business_profile_impl,
        args_schema=NoInput,
    )

    # ========================================================
    # CURRENT USER PROFILE
    # ========================================================

    async def get_my_profile_impl() -> dict[str, Any]:

        return await client.invoke_tool(
            "me",
            {},
        )

    get_my_profile = StructuredTool(
        name="get_my_profile",
        description=(
            "Return the current user's profile, including name, email, "
            "phone, role, and account status. "
            "Use this when the user asks about their own profile, "
            "account, or user details. "
            "No parameters are required."
        ),
        coroutine=get_my_profile_impl,
        args_schema=NoInput,
    )

    # ========================================================
    # EXPENSES
    # ========================================================

    async def list_expenses_impl(
        category: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> dict[str, Any]:

        arguments: dict[str, Any] = {}

        if category is not None:
            arguments["category"] = category

        if from_date is not None:
            arguments["from"] = from_date

        if to_date is not None:
            arguments["to"] = to_date

        return await client.invoke_tool(
            "expenses",
            arguments,
        )

    list_expenses = StructuredTool(
        name="list_expenses",
        description=(
            "Return recorded business expenses with totals. "
            "Use this when the user asks about expenses, spending, costs, "
            "rent, wages, transport, or utilities. "
            "All parameters are optional. "
            "Omit them to get all expenses."
        ),
        coroutine=list_expenses_impl,
        args_schema=ExpenseFilterInput,
    )

    # ========================================================
    # OWNER DEPOSITS
    # ========================================================

    async def list_owner_deposits_impl(
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> dict[str, Any]:

        arguments: dict[str, Any] = {}

        if from_date is not None:
            arguments["from"] = from_date

        if to_date is not None:
            arguments["to"] = to_date

        return await client.invoke_tool(
            "owner/deposits",
            arguments,
        )

    list_owner_deposits = StructuredTool(
        name="list_owner_deposits",
        description=(
            "Return the history of money the owner deposited into the "
            "business, including equity contributions. "
            "These are capital contributions, not business income. "
            "Use this when the user asks about owner deposits, capital "
            "added, or money they put into the business. "
            "All parameters are optional. "
            "Omit them to get all deposits."
        ),
        coroutine=list_owner_deposits_impl,
        args_schema=DateRangeInput,
    )

    # ========================================================
    # OWNER WITHDRAWALS
    # ========================================================

    async def list_owner_withdrawals_impl(
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> dict[str, Any]:

        arguments: dict[str, Any] = {}

        if from_date is not None:
            arguments["from"] = from_date

        if to_date is not None:
            arguments["to"] = to_date

        return await client.invoke_tool(
            "owner/withdrawals",
            arguments,
        )

    list_owner_withdrawals = StructuredTool(
        name="list_owner_withdrawals",
        description=(
            "Return the history of money the owner withdrew from the "
            "business. These are owner drawings, not business expenses. "
            "Use this when the user asks about owner withdrawals, "
            "drawings, money taken out, or personal-use funds. "
            "All parameters are optional. "
            "Omit them to get all withdrawals."
        ),
        coroutine=list_owner_withdrawals_impl,
        args_schema=DateRangeInput,
    )

    # ========================================================
    # RETURN ALL TOOLS
    # ========================================================

    return [
        get_profit_report,
        get_cash_position,
        get_debtors_summary,
        get_creditors_summary,
        list_products,
        list_users,
        get_business_profile,
        get_my_profile,
        list_expenses,
        list_owner_deposits,
        list_owner_withdrawals,
    ]