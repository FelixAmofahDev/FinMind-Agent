from __future__ import annotations

from langchain_core.tools import StructuredTool

from app.services.tool_http_client import ToolHttpClient
from app.tools.http_tools import create_tools


def create_tool_registry(
    client: ToolHttpClient,
) -> list[StructuredTool]:
    """
    Build the real, request-scoped tools. Call this once per request
    (see tool_node.py) with a ToolHttpClient carrying the actual
    user_id / business_id / user_role for that request. This is what
    actually executes tool calls.
    """
    return create_tools(client)


class _UnboundToolHttpClient:
    """
    Placeholder client used ONLY so we can build tool objects for
    their schemas (name, description, args_schema) at import time,
    before we know who's making the request.

    If anything actually calls .invoke_tool() on this, it means a
    tool from TOOLS got executed directly instead of going through
    tool_node's request-scoped tools — that's a bug, so we fail loudly
    instead of silently hitting the API with no real user/business
    context.
    """

    async def invoke_tool(self, *args, **kwargs):
        raise RuntimeError(
            "A tool from the TOOLS constant was invoked directly. "
            "TOOLS is for LLM schema-binding only (see call_llm.py). "
            "Real tool execution must go through "
            "create_tool_registry(client) inside tool_node."
        )


# Fixed list of tool schemas for the LLM to see when deciding what to
# call (e.g. llm.bind_tools(TOOLS) in call_llm.py). Built once at
# import time — safe because the LLM only reads name/description/
# args_schema off these, it never actually runs them.
TOOLS: list[StructuredTool] = create_tools(_UnboundToolHttpClient())