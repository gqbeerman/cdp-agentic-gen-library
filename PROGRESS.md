# Progress

Track your progress through the masterclass. Update this file as you complete modules - Claude Code reads this to understand where you are in the project.

## Convention
- `[ ]` = Not started
- `[-]` = In progress
- `[x]` = Completed

## Modules

### Module 1: App Shell + Observability
- [x] Frontend scaffold (React + Vite + TS + Tailwind + shadcn/ui)
- [x] Backend scaffold (Python + FastAPI + venv)
- [x] Supabase `user_threads` table with RLS
- [x] Auth flow (frontend context + login page + JWT middleware)
- [x] OpenAI Responses API integration (threads, messages, streaming)
- [x] Chat API endpoints (threads CRUD + chat SSE)
- [x] Chat UI (thread sidebar + message list + chat input)
- [x] LangSmith tracing setup
- [x] Auto-generated thread titles (first message → AI-generated title via SSE)
- [x] File citation resolution (OpenAI file annotations → actual filenames)
- [x] Animated thinking indicator (CSS-only responsive generator with spinning turbine, rem units, oklch theme colors)
- [x] Manual verification (auth flow, chat flow, thread management)

### Module 2: BYO Retrieval + Memory
- [x] Provider abstraction layer (OpenAI, OpenRouter, Ollama, LM Studio via `provider_config.py`)
- [x] Chat Completions API migration (`completions_service.py` replaces Responses API)
- [x] Self-managed chat history (`chat_messages` table + `message_service.py`)
- [x] Removed `openai_service.py` (Option A: full replace)
- [x] Refactored routers (threads no longer call OpenAI, messages stored in Supabase)
- [x] LangSmith tracing with model/provider metadata
- [x] Ingestion UI + file storage
- [x] Document chunking + embeddings + pgvector
- [x] Retrieval tool + tool calling
- [x] Realtime ingestion status
- [x] Multi-provider API key management (OpenAI, Google, xAI, OpenRouter UI)
- [x] Settings UX refactor (fixed width, scrollable, Save/Cancel buttons)
- [x] Atomic settings persistence (only save to storage on explicit action)
- [x] Model-aware system prompt (assistant knows which model it is using)
- [x] Document ingestion reliability (re-entrancy guards + event stop propagation)