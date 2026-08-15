from __future__ import annotations

import logging
import re

from app.graph.state import AgentState

logger = logging.getLogger(__name__)

INTERNAL_TOOL_NAMES = {
    'get_current_date', 'get_profit_report', 'get_cash_position',
    'get_debtors_summary', 'get_creditors_summary', 'list_products',
    'list_users', 'get_business_profile', 'get_my_profile',
    'list_expenses', 'list_owner_deposits', 'list_owner_withdrawals',
}

INTERNAL_PATTERNS = [
    r'Tool\s+\w+',
    r'internal/',
    r'x-internal-service-key',
    r'Traceback \(most recent call last\)',
    r'File ".*", line \d+',
    r'Error: Unable to generate response\.\s*\S+',
]

SYSTEM_ERROR_PATTERNS = [
    r'\b\d{3}\s+[-–]\s+\w+',  # HTTP status codes like "500 - Internal"
    r'status_code=\d+',
    r'response\.text',
    r'httpx\.exceptions',
    r'sqlalchemy',
    r'asyncpg',
    r'Traceback',
]


def _mask_tool_names(text: str) -> str:
    for name in sorted(INTERNAL_TOOL_NAMES, key=len, reverse=True):
        text = re.sub(r'\b' + re.escape(name) + r'\b', '', text, flags=re.IGNORECASE)
    return text


def _remove_internal_patterns(text: str) -> str:
    for pattern in INTERNAL_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text


def _normalize_system_errors(text: str) -> str:
    for pattern in SYSTEM_ERROR_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text


def _clean_whitespace(text: str) -> str:
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def sanitize_response(state: AgentState) -> AgentState:
    raw = state.get('llm_response') or ''

    if not raw:
        return state

    cleaned = raw
    cleaned = _mask_tool_names(cleaned)
    cleaned = _remove_internal_patterns(cleaned)
    cleaned = _normalize_system_errors(cleaned)
    cleaned = _clean_whitespace(cleaned)

    if cleaned != raw:
        logger.info('Sanitized agent response to remove internal references')

    state['llm_response'] = cleaned
    return state
