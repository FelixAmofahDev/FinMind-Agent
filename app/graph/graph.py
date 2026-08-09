from __future__ import annotations

from typing import Literal

from langgraph.graph import StateGraph, END

from app.graph.state import AgentState
from app.graph.nodes.load_state import load_state
from app.graph.nodes.check_state_sufficiency import check_state_sufficiency
from app.graph.nodes.fetch_conversation_context import fetch_conversation_context
from app.graph.nodes.fetch_summary_context import fetch_summary_context
from app.graph.nodes.build_context import build_context
from app.graph.nodes.call_llm import call_llm
from app.graph.nodes.tool_node import tool_node
from app.graph.nodes.update_state import update_state
from app.graph.nodes.update_summary import update_summary
from app.graph.nodes.persist import persist


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("load_state", load_state)
    workflow.add_node("check_state_sufficiency", check_state_sufficiency)
    workflow.add_node("fetch_conversation_context", fetch_conversation_context)
    workflow.add_node("fetch_summary_context", fetch_summary_context)
    workflow.add_node("build_context", build_context)
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("update_state", update_state)
    workflow.add_node("update_summary", update_summary)
    workflow.add_node("persist", persist)

    workflow.set_entry_point("load_state")
    workflow.add_edge("load_state", "check_state_sufficiency")
    workflow.add_edge("check_state_sufficiency", "fetch_conversation_context")
    workflow.add_edge("fetch_conversation_context", "fetch_summary_context")
    workflow.add_edge("fetch_summary_context", "build_context")
    workflow.add_edge("build_context", "call_llm")

    workflow.add_conditional_edges(
        "call_llm",
        lambda state: "tool_node" if state.get("tool_calls") else "update_state",
        {
            "tool_node": "tool_node",
            "update_state": "update_state",
        },
    )

    workflow.add_edge("tool_node", "call_llm")
    workflow.add_edge("update_state", "update_summary")
    workflow.add_edge("update_summary", "persist")
    workflow.add_edge("persist", END)

    return workflow.compile()
