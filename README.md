# Mini ChatGPT API

A minimal REST API that lets users create chat sessions, send messages, and receive AI-generated responses — built with FastAPI, SQLAlchemy, SQLite, and the Anthropic Claude API.

---

## Project Overview

| | |
|---|---|
| **Language** | Python 3.12 |
| **Framework** | FastAPI |
| **Database** | SQLite via SQLAlchemy ORM |
| **LLM** | Claude (claude-opus-4-8) via Anthropic SDK |
| **Architecture** | Single service, single database, synchronous request/response |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT                                 │
│                  (curl / browser / frontend)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP REST
                            │ X-API-Key: <key>          [V2.0]
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI APP (main.py)                      │
│         Global exception handler · load_dotenv · DB init       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [V2.0] AUTH                      dependencies.py       │   │
│  │  verify_api_key → 401 missing key / 403 wrong key       │   │
│  └───────────────────────────┬─────────────────────────────┘   │
│                              │ authenticated                    │
│  ┌───────────────────────────▼─────────────────────────────┐   │
│  │  [V2.0] RATE LIMITER                      slowapi       │   │
│  │  10 requests / min per API key → 429                    │   │
│  └──────────────┬────────────────────────────┬─────────────┘   │
│                 │ under limit                │ under limit     │
│  ┌──────────────▼────────────┐  ┌────────────▼─────────────┐   │
│  │    routers/sessions.py    │  │   routers/messages.py    │   │
│  │                           │  │                          │   │
│  │  POST /sessions           │  │  POST /sessions/{id}/    │   │
│  │  GET  /sessions/{id}      │  │       messages  [V2.0]▶  │   │
│  │                           │  │  GET  /sessions/{id}/    │   │
│  │                           │  │       messages           │   │
│  └──────────┬────────────────┘  └───────────┬──────────────┘   │
│             │                               │                   │
│             │               ┌───────────────▼──────────────┐   │
│             │               │  [V2.0] LLM RESILIENCE       │   │
│             │               │  services/llm.py             │   │
│             │               │  max_retries=3 + backoff     │   │
│             │               │  timeout=30s per attempt     │   │
│             │               │  all retries fail → 503      │   │
│             │               └───────────────┬──────────────┘   │
└─────────────┼───────────────────────────────┼───────────────────┘
              │ SQLAlchemy ORM                │ HTTPS
              ▼                               ▼
┌──────────────────────┐          ┌───────────────────────┐
│   SQLITE (chat.db)   │          │    ANTHROPIC API       │
│  sessions + messages │          │    claude-opus-4-8     │
└──────────────────────┘          │    retry 1 → 2 → 3    │
                                  └───────────────────────┘

  [V2.0] TEST SUITE                          pytest / 20 tests
  ┌───────────────────────────────────────────────────────────┐
  │  conftest.py — in-memory SQLite · mocked LLM · auth key  │
  │  test_health.py · test_sessions.py · test_messages.py    │
  │  test_auth.py  · test_rate_limit.py                      │
  │  0 real API calls · 0 disk writes                        │
  └───────────────────────────────────────────────────────────┘
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/sessions` | Create a new chat session |
| `GET` | `/sessions/{id}` | Get session metadata |
| `POST` | `/sessions/{id}/messages` | Send a message and get an AI reply |
| `GET` | `/sessions/{id}/messages` | Retrieve full conversation history |

---

## Database Schema

```
sessions
────────────────────────
id          STRING  PK   (UUID)
title       STRING       (optional)
created_at  DATETIME

messages
────────────────────────
id          STRING  PK   (UUID)
session_id  STRING  FK → sessions.id
role        STRING       ("user" | "assistant")
content     TEXT
created_at  DATETIME
```

---

## Project Structure

```
mini_chatgpt/
├── main.py              # App entry point, router registration, global error handler
├── database.py          # SQLAlchemy engine, session factory, init_db
├── models.py            # ORM models: Session, Message
├── schemas.py           # Pydantic request/response schemas + validators
├── dependencies.py      # Auth (verify_api_key) + rate limiter instance  [V2.0]
├── requirements.txt
├── routers/
│   ├── sessions.py      # POST /sessions, GET /sessions/{id}
│   └── messages.py      # POST + GET /sessions/{id}/messages
├── services/
│   └── llm.py           # Anthropic API call, max_retries=3, timeout=30s [V2.0]
└── tests/                                                                 [V2.0]
    ├── conftest.py      # Fixtures: in-memory DB, mocked LLM, auth headers
    ├── test_health.py
    ├── test_sessions.py
    ├── test_messages.py
    ├── test_auth.py
    └── test_rate_limit.py
```

---

## Design Decisions

**FastAPI** — automatic request validation via Pydantic, auto-generated Swagger UI at `/docs`, minimal boilerplate.

**SQLAlchemy ORM** — database-agnostic; switching from SQLite to Postgres requires only changing `DATABASE_URL`.

**Full conversation history per request** — every message sent to the LLM includes the entire prior conversation for that session, giving Claude memory across turns.

**`services/llm.py` isolation** — the Anthropic call lives in one place, making it easy to swap models, add retries, or mock in tests without touching routing logic.

**Pydantic validators** — empty/whitespace-only messages are rejected at the schema layer before hitting the DB or LLM.

---

## Tradeoffs

| Area | MVP (V1.0) | V2.0 (current) | Production |
|---|---|---|---|
| Auth | None | Shared `X-API-Key` | Per-user JWT or API keys with `user_id` scoping |
| Rate limiting | None | 10 req/min per key, in-memory | Redis-backed, per-user quotas |
| LLM reliability | No retry | 3 retries + 30s timeout | Circuit breaker + alerting |
| Tests | None | 20 tests, mocked LLM, in-memory DB | CI pipeline + integration tests |
| Database | SQLite | SQLite | Postgres with connection pooling |
| Concurrency | Synchronous | Synchronous | `async def` + `AsyncSession` |
| LLM context | Full history | Full history | Sliding window or summarization |
| Response delivery | Blocking JSON | Blocking JSON | Server-Sent Events with streaming |
| Observability | None | None | Structured logging + request tracing |

---

## How to Run

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Set your Anthropic API key**
```bash
# Create a .env file in the project root
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

**3. Start the server**
```bash
uvicorn main:app --reload
```

**4. Open API docs** — http://localhost:8000/docs

---

## Example curl Commands

```bash
# Health check (no auth required)
curl http://localhost:8000/health

# Create a session
curl -s -X POST http://localhost:8000/sessions \
  -H "X-API-Key: secret" \
  -H "Content-Type: application/json" \
  -d '{"title": "My first chat"}' | python3 -m json.tool

# Send a message (replace <session_id>)
curl -s -X POST http://localhost:8000/sessions/<session_id>/messages \
  -H "X-API-Key: secret" \
  -H "Content-Type: application/json" \
  -d '{"content": "What is the capital of France?"}' | python3 -m json.tool

# Follow-up — Claude remembers the conversation
curl -s -X POST http://localhost:8000/sessions/<session_id>/messages \
  -H "X-API-Key: secret" \
  -H "Content-Type: application/json" \
  -d '{"content": "What is the population of that city?"}' | python3 -m json.tool

# Retrieve full conversation history
curl -s http://localhost:8000/sessions/<session_id>/messages \
  -H "X-API-Key: secret" | python3 -m json.tool

# Auth errors
curl -s http://localhost:8000/sessions/<session_id>/messages    # 401 no key
curl -s -H "X-API-Key: wrong" http://localhost:8000/sessions/<session_id>/messages  # 403
```

---

## Future Improvements

- **Streaming** — Anthropic streaming API + FastAPI `StreamingResponse` for real-time token delivery
- **Per-user auth** — replace shared key with JWT or per-user API keys; add `user_id` to sessions and scope all queries
- **Postgres** — replace SQLite for concurrent writes and horizontal scaling
- **Redis rate limiting** — swap in-memory limiter storage for Redis so limits survive restarts and work across multiple workers
- **Context window management** — track token counts per session; apply sliding window or summarization when history grows long
- **Async I/O** — convert routes to `async def` with `AsyncSession` for non-blocking DB access under load
- **Observability** — structured JSON logging, `X-Request-ID` tracing, Prometheus `/metrics` endpoint
