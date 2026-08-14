from __future__ import annotations

import json
import logging

from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq

from app.graph.nodes.update_state import merge_entities
from app.database.repositories.summary_repository import SummaryRepository
from app.database.repositories.conversation_repository import ConversationRepository
from app.schemas.conversation_extraction import ConversationExtraction, ConversationExtractionWithTitle
from app.config.settings import settings
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def build_llm() -> BaseChatModel:
    if not settings.LLM_API_KEY:
        raise RuntimeError("MODEL_API_KEY is not configured")
    return ChatGroq(model=settings.BOOKKEEPING_LLM_MODEL_NAME, api_key=settings.LLM_API_KEY)


def _build_prompt(
    current_summary: str,
    user_message: str,
    llm_response: str,
    existing_conversation_state: dict,
    last_tool_result,
    is_new: bool,
) -> str:
    title_note = (
        "\n\nAlso produce a title: a short 3-6 word label for this conversation, "
        "no quotes, no trailing punctuation."
        if is_new
        else ""
    )
    existing_entities = existing_conversation_state.get("state", {}).get("entities", {})
    return (
        "You are maintaining a running summary and structured state for a business conversation.\n\n"
        f"Current summary:\n{current_summary or 'No summary yet.'}\n\n"
        f"Current topic: {existing_conversation_state.get('currentTopic', 'general')}\n"
        f"Current intent: {existing_conversation_state.get('currentIntent', 'respond')}\n"
        f"Known entities so far: {json.dumps(existing_entities)}\n\n"
        f"New user message:\n{user_message}\n\n"
        f"New assistant response:\n{llm_response}\n\n"
        f"Result of the tool called this turn (if any):\n"
        f"{json.dumps(last_tool_result) if last_tool_result else 'No tool was called.'}\n\n"
        "Update the summary to incorporate meaningful new information only. Keep it concise, "
        "around 10-20 lines. Include actual figures, entities, and what the user has been trying to do. "
        "If the new exchange does not add important information, return the current summary unchanged.\n\n"
        "Also determine currentTopic and currentIntent for this turn (carry forward the existing "
        "ones if nothing changed), and extract any entities worth remembering for future turns as "
        "entities_json — a JSON-encoded object string, merging with (not replacing) the known "
        "entities above."
        f"{title_note}"
    )


def _parse_entities(entities_json: str) -> dict:
    try:
        parsed = json.loads(entities_json)
        if isinstance(parsed, dict):
            return parsed
        logger.warning(f"entities_json was valid JSON but not an object: {entities_json!r}")
        return {}
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Could not parse entities_json: {entities_json!r}")
        return {}


async def update_summary_state(state: AgentState) -> AgentState:
    session = state["session"]
    conversation_id = state["conversation_id"]
    user_message = state["user_message"]
    llm_response = state.get("llm_response", "")
    tool_name = state.get("tool_name")
    tool_results = state.get("tool_results") or {}
    last_tool_result = tool_results.get(tool_name) if tool_name else None

    existing_conversation_state = state.get("updated_conversation_state") or {}
    current_summary = ""
    current_topics = {}
    is_new = state.get("is_new_conversation")

    try:
        summary_repo = SummaryRepository(session)
        existing = await summary_repo.get_by_conversation_id(conversation_id)
        current_summary = existing.summary if existing else ""
        current_topics = existing.topics if existing else {}

        if is_new is None:
            conversation_repo = ConversationRepository(session)
            conversation = await conversation_repo.get_by_id(conversation_id)
            is_new = conversation is None or not conversation.title
        logger.info(f"is_new={is_new} for conversation {conversation_id}")

        prompt = _build_prompt(
            current_summary, user_message, llm_response,
            existing_conversation_state, last_tool_result, is_new,
        )

        llm = build_llm()
        schema = ConversationExtractionWithTitle if is_new else ConversationExtraction

        try:
            response = await llm.with_structured_output(schema).ainvoke(prompt)
        except Exception as e:
            logger.warning(f"Structured output failed, retrying once: {e}")
            response = await llm.with_structured_output(schema).ainvoke(prompt)

        new_entities = _parse_entities(response.entities_json)

        state["updated_summary"] = response.summary.strip()
        state["updated_topics"] = current_topics

        merged_entities = merge_entities(
            {"entities": existing_conversation_state.get("state", {}).get("entities", {})},
            {"entities": new_entities},
        )
        state["updated_conversation_state"] = {
            **existing_conversation_state,  # keeps lastToolUsed/lastToolResult from response graph
            "currentTopic": response.currentTopic.strip(),
            "currentIntent": response.currentIntent.strip(),
            "state": merged_entities,
        }

        if is_new:
            state["updated_title"] = response.title.strip().strip('"')

        logger.info(f"Updated summary/state for conversation {conversation_id}")
    except Exception:
        logger.exception(f"Error updating summary/state for conversation {conversation_id}")
        state["updated_summary"] = current_summary
        state["updated_topics"] = current_topics
        # updated_conversation_state deliberately left untouched — falls
        # back to whatever the response graph's update_state seeded.

    return state