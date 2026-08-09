from __future__ import annotations

import logging

from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq

from app.config.settings import settings
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def build_llm() -> BaseChatModel:
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)


async def update_summary(state: AgentState) -> AgentState:
    session = state["session"]
    conversation_id = state["conversation_id"]
    user_message = state["user_message"]
    llm_response = state.get("llm_response", "")
    current_summary = ""
    current_topics = {}

    try:
        from app.database.repositories.summary_repository import SummaryRepository

        summary_repo = SummaryRepository(session)
        existing = await summary_repo.get_by_conversation_id(conversation_id)
        current_summary = existing.summary if existing else ""
        current_topics = existing.topics if existing else {}

        if not current_summary and not user_message:
            state["updated_summary"] = ""
            state["updated_topics"] = {}
            return state

        prompt = (
            "You are maintaining a running summary of a business conversation.\n\n"
            f"Current summary:\n{current_summary or 'No summary yet.'}\n\n"
            f"New user message:\n{user_message}\n\n"
            f"New assistant response:\n{llm_response}\n\n"
            "Update the summary to incorporate meaningful new information only. "
            "Keep it concise, around 10-20 lines depending on how much detail is necessary. "
            "Include actual figures, entities, and what the user has been trying to do. "
            "If the new exchange does not add important information, return the current summary unchanged. "
            "Return ONLY the updated summary text, nothing else."
        )

        llm = build_llm()
        response = await llm.ainvoke(prompt)
        updated_summary = response.content if hasattr(response, "content") else str(response)

        state["updated_summary"] = updated_summary.strip()
        state["updated_topics"] = current_topics
        logger.info(f"Updated summary for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"Error updating summary: {e}")
        state["updated_summary"] = current_summary
        state["updated_topics"] = current_topics

    return state
