from __future__ import annotations

from typing import Literal

from langgraph.graph import StateGraph, END

from app.graph.state import AgentState
from app.graph.nodes.load_state import load_state
from app.graph.nodes.check_state_sufficiency import check_state_sufficiency
from app.graph.nodes.fetch_conversation_context import fetch_conversation_context
from app.graph.nodes.fetch_summary_context import fetch_summary_context
from app.graph.nodes.plan_tool import plan_tool
from app.graph.nodes.execute_tool import execute_tool
from app.graph.nodes.update_state import update_state
from app.graph.nodes.build_context import build_context
from app.graph.nodes.call_llm import call_llm
from app.graph.nodes.persist import persist


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("load_state", load_state)
    workflow.add_node("check_state_sufficiency", check_state_sufficiency)
    workflow.add_node("fetch_conversation_context", fetch_conversation_context)
    workflow.add_node("fetch_summary_context", fetch_summary_context)
    workflow.add_node("plan_tool", plan_tool)
    workflow.add_node("execute_tool", execute_tool)
    workflow.add_node("update_state", update_state)
    workflow.add_node("build_context", build_context)
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("persist", persist)

    workflow.set_entry_point("load_state")
    workflow.add_edge("load_state", "check_state_sufficiency")

    workflow.add_conditional_edges(
        "check_state_sufficiency",
        lambda state: "build_context" if state["state_is_sufficient"] else "fetch_conversation_context",
        {
            "build_context": "build_context",
            "fetch_conversation_context": "fetch_conversation_context",
        },
    )

    workflow.add_edge("fetch_conversation_context", "fetch_summary_context")

    workflow.add_conditional_edges(
        "fetch_summary_context",
        lambda state: "plan_tool",
        {"plan_tool": "plan_tool"},
    )

    workflow.add_conditional_edges(
        "plan_tool",
        lambda state: "execute_tool" if state.get("tool_needed") else "update_state",
        {
            "execute_tool": "execute_tool",
            "update_state": "update_state",
        },
    )

    workflow.add_edge("execute_tool", "update_state")
    workflow.add_edge("update_state", "build_context")
    workflow.add_edge("build_context", "call_llm")
    workflow.add_edge("call_llm", "persist")
    workflow.add_edge("persist", END)

    return workflow.compile()
