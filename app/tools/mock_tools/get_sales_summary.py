from __future__ import annotations

from langchain_core.tools import tool


@tool
def get_sales_summary(period: str) -> dict:
    """Return sales data for a given period. Currently returns mock data."""
    return {"period": period, "sales": 12000, "currency": "GHS"}
