from __future__ import annotations

from datetime import datetime, timezone

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.graph.state import AgentState


def build_context(state: AgentState) -> AgentState:
    summary = state.get("relevant_summary")
    summary_text = summary.get("summary") if isinstance(summary, dict) else ""
    conversation_state = state.get("conversation_state", {})
    user_role = state.get("user_role", "unknown")
    now = datetime.now(timezone.utc)

    system_content = (
        "You are FinMind's AI accountant.\n\n"
        f"Current date/time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        f"Today is: {now.strftime('%A, %d %B %Y')}\n\n"
        f"Current user role: {user_role}\n\n"
        "Your role is to act as an intelligent accounting assistant for the business owner.\n\n"
        "You can:\n"
        "- Analyze sales, expenses, profit, cash position, inventory, debtors, and creditors.\n"
        "- Answer questions about the business's financial performance.\n"
        "- Retrieve accurate business data.\n"
        "- Perform calculations when necessary.\n"
        "- Explain financial information clearly to the business owner.\n\n"
        "Important rules:\n"
        "- All financial figures are in Ghana cedis (GHS).\n"
        "- Never invent financial figures.\n"
        "- When financial data is required, use the service.\n"
        "- Always base financial answers on the data returned by services.\n"
        "- Do not assume values that are not provided.\n"
        "- You are only authorized to access the business context provided to you.\n"
        "- Use direct, simple, and easy-to-understand words. Avoid unnecessary technical or accounting jargon.\n"
        "- Speak directly to the business owner using the the buiness name or the second-person point of view, such as 'you' and 'your business,' whenever appropriate.\n"
        "- Keep explanations clear, concise, and focused on what matters to the business owner.\n"
        "- Respect role-based access: cashiers and stock managers have limited access to certain financial data.\n"
        "- Only provide detailed financial reports to owners and managers.\n"
        "- For relative date references like 'last month', 'this week', 'yesterday', "
        "use the current date above to compute the exact YYYY-MM-DD dates before calling any tool.\n"
        "- All tool date parameters MUST be in YYYY-MM-DD format.\n"
        "- Never pass relative phrases or ambiguous dates to tools — always resolve them first.\n"
        "## Conversation Summary\n"
        f"Summary: {summary_text or 'No summary yet.'}\n"
        "### Conversation State\n"
        f"Conversation state: {conversation_state}"
    )

    messages = [SystemMessage(content=system_content)]

    for msg in state.get("recent_messages", []):
        if isinstance(msg, HumanMessage):
            messages.append(msg)
        elif isinstance(msg, AIMessage):
            messages.append(msg)
        elif isinstance(msg, SystemMessage):
            messages.append(msg)

    messages.append(HumanMessage(content=state["user_message"]))

    state["messages"] = messages
    return state
