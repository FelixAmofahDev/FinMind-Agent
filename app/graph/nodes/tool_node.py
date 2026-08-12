from __future__ import annotations

import logging

from langchain_core.messages import ToolMessage

from app.graph.state import AgentState
from app.tools.tool_registry import create_tool_registry

logger = logging.getLogger(__name__)


async def tool_node(state: AgentState) -> AgentState:
    tool_calls = state.get("tool_calls") or []
    tool_client = state.get("tool_http_client")

    # ---------------------------------------------------------
    # results_by_call_id is keyed by tool_call_id, NOT tool_name.
    #
    # The LLM can call the same tool more than once in a single
    # turn (e.g. get_profit_report for two different date ranges).
    # Keying results by tool_name means the second call silently
    # overwrites the first, and BOTH ToolMessages sent back to the
    # model would end up carrying the second call's result. This
    # dict exists specifically to keep each call's result distinct
    # so the right ToolMessage gets the right content.
    # ---------------------------------------------------------

    if tool_client is None:
        logger.error("tool_http_client is missing from agent state")

        results_by_call_id = {
            call.get("id"): {"error": "Tool client not initialized"}
            for call in tool_calls
        }

        # Every tool_use block the LLM produced still needs a matching
        # tool_result, even in this failure path — otherwise the next
        # LLM call will be rejected for having unanswered tool_calls.
        tool_messages = [
            ToolMessage(
                content=str(results_by_call_id[call.get("id")]),
                tool_call_id=call.get("id"),
            )
            for call in tool_calls
        ]

        state["messages"].extend(tool_messages)
        state["tool_calls"] = None
        state["tool_results"] = {
            call["name"]: results_by_call_id[call.get("id")]
            for call in tool_calls
        }
        state["tool_name"] = tool_calls[-1]["name"] if tool_calls else None

        return state

    # ---------------------------------------------------------
    # Create request-specific tools.
    #
    # The ToolHttpClient is injected into the tools here.
    # The LLM never sees it.
    # ---------------------------------------------------------

    tools = create_tool_registry(tool_client)

    tool_lookup = {
        tool.name: tool
        for tool in tools
    }

    # ---------------------------------------------------------
    # Execute each tool call
    # ---------------------------------------------------------

    results_by_call_id: dict[str, dict] = {}
    results_by_name: dict[str, dict] = {}
    last_tool_name = None

    for call in tool_calls:

        tool_name = call["name"]
        call_id = call.get("id")
        arguments = call.get("args") or {}
        last_tool_name = tool_name

        if call_id is None:
            logger.error("Tool call for %s is missing an id", tool_name)

        tool = tool_lookup.get(tool_name)

        if tool is None:
            logger.error(
                "Unknown tool requested: %s",
                tool_name,
            )

            error_result = {"error": f"Unknown tool: {tool_name}"}
            results_by_call_id[call_id] = error_result
            results_by_name[tool_name] = error_result

            continue

        try:
            logger.info(
                "Executing tool=%s arguments=%s",
                tool_name,
                arguments,
            )

            # IMPORTANT:
            #
            # Do NOT do:
            #
            # await tool.coroutine(tool_client, **arguments)
            #
            # The client has already been bound to the tool.
            #
            result = await tool.ainvoke(arguments)

            results_by_call_id[call_id] = result
            results_by_name[tool_name] = result

            logger.info(
                "Tool %s executed successfully",
                tool_name,
            )

        except Exception as exc:

            logger.exception(
                "Error executing tool %s",
                tool_name,
            )

            error_result = {"error": str(exc)}
            results_by_call_id[call_id] = error_result
            results_by_name[tool_name] = error_result

    # ---------------------------------------------------------
    # Convert results to ToolMessages
    #
    # One ToolMessage per tool_call, matched by call_id — this is
    # the fix for the bug where duplicate tool names caused every
    # ToolMessage for that tool to carry the same (wrong) result.
    # ---------------------------------------------------------

    tool_messages = []

    for call in tool_calls:

        call_id = call.get("id")

        result = results_by_call_id.get(
            call_id,
            {"error": "Unknown error"},
        )

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=call_id,
            )
        )

    # ---------------------------------------------------------
    # Update state
    # ---------------------------------------------------------

    state["messages"].extend(tool_messages)

    # NOTE: kept name-keyed for state["tool_results"] to match the
    # original shape (in case downstream nodes read it by tool name).
    # If the same tool is called twice in one turn, this will only
    # show the *last* of those calls' results — the correct
    # per-call results are what actually get sent to the LLM via
    # the ToolMessages above. If any downstream node needs to see
    # every individual call's result, switch this to
    # results_by_call_id instead and update that node accordingly.
    state["tool_results"] = results_by_name
    state["tool_name"] = last_tool_name
    state["tool_calls"] = None

    return state