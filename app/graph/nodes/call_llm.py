from __future__ import annotations

import logging
from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq

from app.config.settings import settings
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def build_llm() -> BaseChatModel:
    """Initialize the Groq LLM."""
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)


async def call_llm(state: AgentState) -> AgentState:
    """Call the Groq LLM with the built context."""
    try:
        llm = build_llm()
        response = llm.invoke(state["llm_context"])
        state["llm_response"] = response.content if hasattr(response, "content") else str(response)
        logger.info(f"LLM call succeeded for conversation {state['conversation_id']}")
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        state["llm_response"] = f"Error: Unable to generate response. {str(e)}"

    return state
