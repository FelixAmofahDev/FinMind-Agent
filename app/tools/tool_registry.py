from __future__ import annotations

from app.tools.http_tools import (
    get_business_profile,
    get_cash_position,
    get_creditors_summary,
    get_debtors_summary,
    get_my_profile,
    get_profit_report,
    list_products,
    list_users,
)

TOOLS = [
    get_profit_report,
    get_cash_position,
    get_debtors_summary,
    get_creditors_summary,
    list_products,
    list_users,
    get_business_profile,
    get_my_profile,
]
