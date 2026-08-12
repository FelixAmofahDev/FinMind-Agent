from __future__ import annotations

from langchain_core.tools import tool


@tool
def get_business_name() -> dict:
    """Return the name of the business."""
    return {"business_name": "Acme Corp"}