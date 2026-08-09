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

    for call in tool_calls:
        tool_name = call["name"]
        arguments = call.get("args", {})
        tool_call_id = call.get("id")
        last_tool_name = tool_name

        tool_fn = _TOOL_REGISTRY.get(tool_name)
        if not tool_fn:
            logger.error(f"Unknown tool: {tool_name}")
            results[tool_name] = {"error": f"Unknown tool: {tool_name}"}
            continue

        try:
            result = await tool_fn.ainvoke(arguments)
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
