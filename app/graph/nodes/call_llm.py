from __future__ import annotations

import logging

from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq

from app.config.settings import settings
from app.graph.state import AgentState
from app.tools.tool_registry import TOOLS

logger = logging.getLogger(__name__)


def build_llm() -> BaseChatModel:
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)


async def call_llm(state: AgentState) -> AgentState:
    try:
        llm = build_llm().bind_tools(TOOLS)
        response = await llm.ainvoke(state["messages"])

        state["messages"].append(response)

        tool_calls = getattr(response, "tool_calls", None)
        state["tool_calls"] = tool_calls

        if tool_calls:
            state["llm_response"] = ""
            logger.info(f"LLM requested {len(tool_calls)} tool call(s) for conversation {state['conversation_id']}")
        else:
            state["llm_response"] = response.content if hasattr(response, "content") else str(response)
            logger.info(f"LLM call succeeded for conversation {state['conversation_id']}")
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        state["llm_response"] = f"Error: Unable to generate response. {str(e)}"
        state["tool_calls"] = None

    return state
