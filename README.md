# AI Customer Support Assistant (E-commerce)

Production-minded reference app with **FastAPI + LangChain + React + PostgreSQL** (defaulted to Groq via OpenAI-compatible API).

## 1) High-level Architecture
- **Frontend (React + Vite + Tailwind)**: Chat UI with dark mode, optimistic rendering, and streaming text updates.
- **Backend (FastAPI async)**: Async API, middleware logging, CORS, rate limiting, dependency injection.
- **Agent Layer (LangChain)**:
  - Intent + response orchestration via modern `create_agent` (LangChain v1 API)
  - LLM provider abstraction through OpenAI-compatible interface (`LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`) with Groq defaults
  - Async custom tools (`order_status_checker`, `product_search`, `faq_retriever`)
  - RAG context injected from FAISS retrieval service
  - `ConversationBufferMemory` for conversational continuity
- **Persistence**: PostgreSQL (`SQLAlchemy 2.0 async + asyncpg`) stores chat history.
- **Cache**: Redis connection configured for future token/session cache use.

### Agent architecture and flow
1. API receives chat message with `session_id`.
2. Retrieval service fetches relevant docs from FAISS and returns compact context.
3. Agent prompt receives `chat_history`, `context`, and user `input`.
4. Agent chooses whether to call tools.
5. Final answer is returned and persisted in PostgreSQL.


## Provider configuration (Groq by default)
- This project uses `ChatOpenAI` with an **OpenAI-compatible endpoint**, so Groq works out of the box.
- Defaults in `.env.example` target Groq free/dev usage:
  - `LLM_BASE_URL=https://api.groq.com/openai/v1`
  - `LLM_MODEL=llama-3.1-8b-instant`
- Set your key in `LLM_API_KEY`.
- Backward-compatible env aliases are also accepted: `OPENAI_*` and `GROQ_*`.

## 2) Folder Structure

```text
backend/
  app/
    agents/         # LangChain agent factory
    core/           # settings + logging
    db/             # SQLAlchemy base/session/models
    middleware/     # request logging middleware
    routers/        # FastAPI routers
    schemas/        # Pydantic request/response
    services/       # chat, retrieval, repository
    tools/          # async LangChain tools
  tests/
frontend/
  src/
    components/     # chat window + composer
    lib/            # API client streaming helper
```

## 3) Backend highlights
- Async-only endpoints (`async def`) and async SQLAlchemy session usage.
- OpenAPI docs include endpoint summaries/tags.
- Streaming endpoint (`/api/v1/chat/stream`) using `StreamingResponse`.
- Rate limiting via `slowapi`.
- Structured logging middleware.

## 4) Frontend highlights
- Tailwind-based modern chat UI.
- Dark mode toggle.
- Streaming token rendering using `ReadableStream` reader.
- User-friendly loading and error states.

## 5) Run locally

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs

## 6) Local dev without Docker

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 7) Testing
```bash
cd backend
pytest
```

## 8) Production deployment notes
- Put backend behind reverse proxy (Nginx/Traefik).
- Use managed Postgres + Redis, enable TLS.
- Use async workers (`gunicorn -k uvicorn.workers.UvicornWorker`).
- Add observability (OpenTelemetry traces + metrics).
- Externalize vector index (PGVector) for horizontal scaling.

## 9) Scalability improvements
- Replace in-memory conversation memory with Redis/session memory.
- Introduce task queue for long-running jobs.
- Add auth + tenant isolation.
- Add robust eval pipeline for agent quality and hallucination checks.
