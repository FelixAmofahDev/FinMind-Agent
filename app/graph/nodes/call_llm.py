from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq

from app.config.settings import settings
from app.graph.state import AgentState


def build_llm() -> BaseChatModel:
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)


def call_llm(state: AgentState) -> AgentState:
    llm = build_llm()
    response = llm.invoke(state["llm_context"])
    state["llm_response"] = response.content if hasattr(response, "content") else str(response)
    return state
