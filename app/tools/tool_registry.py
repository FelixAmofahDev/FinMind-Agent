from __future__ import annotations

from app.tools.mock_tools.get_profit_report import get_profit_report
from app.tools.mock_tools.get_sales_summary import get_sales_summary
from app.tools.mock_tools.get_inventory_status import get_inventory_status

TOOLS = [get_profit_report, get_sales_summary, get_inventory_status]
