# FinMind Agent

AI agent service powering the FinMind app's conversational assistant. It answers finance and inventory questions by orchestrating tool calls, conversation memory, and a language model.

## Features

- **Conversational AI** — stream answers to user questions with context-aware memory
- **Tool Use** — invokes internal business APIs (profit & loss, cash position, debtors, creditors, products, expenses, owner transactions, etc.)
- **LangGraph Orchestration** — response graph for answering, bookkeeping graph for background persistence
- **Conversation Memory** — per-conversation summary and state tracking across turns
- **Security** — internal service key auth and role forwarding to backend
- **Containerized** — Dockerized with security hardening and health checks

## Tech Stack

- **Runtime:** Python 3.12
- **Framework:** FastAPI
- **LLM:** LangChain + Groq
- **Orchestration:** LangGraph
- **Database:** PostgreSQL via SQLAlchemy + asyncpg
- **HTTP Client:** httpx
- **Config:** pydantic-settings + python-dotenv
- **Testing:** pytest

## Architecture

```
app/
├── main.py                   # FastAPI app entrypoint
├── config/
│   └── settings.py           # Environment-backed config
├── api/
│   └── routes.py             # /ask endpoint
├── graph/
│   ├── graph.py              # LangGraph workflow definitions
│   ├── state.py              # AgentState TypedDict
│   └── nodes/                # Graph nodes
├── tools/
│   ├── tool_registry.py      # LLM tool schemas + request-scoped registry
│   └── http_tools/           # Tool implementations calling internal API
├── services/
│   └── tool_http_client.py   # Authenticated HTTP client for internal calls
└── database/
    ├── models.py             # SQLAlchemy models
    ├── session.py            # Async session factory
    └── repositories/         # Message, conversation, summary, state repos
```

### Graphs

- **response_graph** — load state → check sufficiency → fetch conversation context → fetch summary context → build context → call LLM → tool execution loop → sanitize response → update state
- **bookkeeping_graph** — update summary and state → persist to DB (runs as background task after response is returned)

## Getting Started

1. **Clone and enter the project:**
   ```bash
   cd ai_agent
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv agent_venv
   # Windows
   agent_venv\Scripts\activate
   # macOS/Linux
   source agent_venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   Then fill in:
   - `DATABASE_URL` — PostgreSQL connection string
   - `LLM_API_KEY` / `LL_MODEL_NAME` — LLM provider key/model
   - `NODE_BACKEND_URL` — FinMind backend URL
   - `INTERNAL_SERVICE_KEY` — shared secret for service-to-service auth

5. **Run the app:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

6. **Run tests:**
   ```bash
   pytest
   ```

## Docker

```bash
docker compose up --build
```

Service will be available at `http://localhost:8000`.

## API

### `POST /ask`

Request body:
```json
{
  "message": "How much profit did we make last month?",
  "businessId": "uuid",
  "userId": "uuid",
  "role": "owner|manager",
  "conversationId": "uuid (optional)"
}
```

Headers:
- `X-Internal-Service-Key` — required

Response:
```json
{
  "conversationId": "uuid",
  "answer": "..."
}
```

Bookkeeping (conversation state + summary persistence) happens asynchronously after the response is returned.

## Environment Variables

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string |
| `LLM_API_KEY` | LLM provider API key |
| `LLM_MODEL_NAME` | Model for assistant responses |
| `BOOKKEEPING_LLM_MODEL_NAME` | Model for summary generation |
| `CONVERSATION_LIMIT` | Max recent messages included in context |
| `NODE_BACKEND_URL` | Base URL for internal business APIs |
| `INTERNAL_SERVICE_KEY` | Shared secret for internal requests |
