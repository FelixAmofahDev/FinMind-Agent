from __future__ import annotations

from app.tools.http_tools import (
    get_business_name,
    get_inventory_status,
    get_profit_report,
)

TOOLS = [get_profit_report, get_inventory_status, get_business_name]
