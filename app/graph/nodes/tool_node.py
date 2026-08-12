from __future__ import annotations

import logging

from langchain_core.messages import ToolMessage

from app.graph.state import AgentState
from app.tools.tool_registry import TOOLS

logger = logging.getLogger(__name__)

_TOOL_REGISTRY = {t.name: t for t in TOOLS}


async def tool_node(state: AgentState) -> AgentState:
    tool_calls = state.get("tool_calls") or []
    results = {}
    last_tool_name = None
    tool_client = state.get("tool_http_client")

    if tool_client is None:
        logger.error("tool_http_client is missing from agent state")
        for call in tool_calls:
            tool_name = call["name"]
            results[tool_name] = {"error": "Tool client not initialized"}
        state["tool_calls"] = None
        state["tool_results"] = results
        return state

    for call in tool_calls:
        tool_name = call["name"]
        arguments = call.get("args", {})
        tool_call_id = call.get("id")
        last_tool_name = tool_name

        tool_entry = _TOOL_REGISTRY.get(tool_name)
        if not tool_entry:
            logger.error(f"Unknown tool: {tool_name}")
            results[tool_name] = {"error": f"Unknown tool: {tool_name}"}
            continue

        try:
            raw_coroutine = getattr(tool_entry, "coroutine", None)
            if raw_coroutine is None:
                logger.error(f"Tool {tool_name} has no coroutine attribute")
                results[tool_name] = {"error": f"Tool {tool_name} is not properly configured"}
                continue

            result = await raw_coroutine(tool_client, **arguments)
            results[tool_name] = result
            logger.info(f"Tool {tool_name} executed successfully")
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            results[tool_name] = {"error": str(e)}

    tool_messages = []
    for call in tool_calls:
        tool_call_id = call.get("id")
        tool_name = call["name"]
        result = results.get(tool_name, {"error": "Unknown error"})
        tool_messages.append(ToolMessage(content=str(result), tool_call_id=tool_call_id))

    state["messages"].extend(tool_messages)
    state["tool_results"] = results
    state["tool_name"] = last_tool_name
    state["tool_calls"] = None

    return state
