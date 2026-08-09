from __future__ import annotations

from langchain_core.tools import tool


@tool
def get_inventory_status(product: str) -> dict:
    """Return inventory status for a given product. Currently returns mock data."""
    return {"product": product, "stock": 25, "status": "in_stock"}
