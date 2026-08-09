from __future__ import annotations

from langchain_core.tools import tool


@tool
def get_profit_report(period: str) -> dict:
    """Return profit for a given period. Currently returns mock data."""
    return {"period": period, "profit": 4500, "currency": "GHS"}
