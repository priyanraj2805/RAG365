<!-- refreshed: 2026-05-14 -->
# Architecture

**Analysis Date:** 2026-05-14

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Admin + Channel Clients                           │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│ Next.js Admin UI         │ Social Webhooks          │ Telegram Webhook      │
│ `.../frontend/src/app`   │ `ChatBotBE/backend/main.py` │ `ChatBotBE/backend/main.py` │
└───────────────┬──────────┴───────────────┬──────────┴──────────────┬────────┘
                │                          │                         │
                ▼                          ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FastAPI Backend                                │
│                      `ChatBotBE/backend/main.py`                            │
└───────────────┬──────────────────────────┬──────────────────────────┬───────┘
                │                          │                          │
                ▼                          ▼                          ▼
┌─────────────────────────────┐  ┌─────────────────────────────┐  ┌─────────────────────────────┐
│ SQLAlchemy data layer       │  │ RAG orchestration layer      │  │ Async indexing workers       │
│ `database.py`, `models.py`  │  │ `rag_model/rag_utils.py`     │  │ `index_handler.py` + Lambda  │
└───────────────┬─────────────┘  └───────────────┬─────────────┘  └───────────────┬─────────────┘
                │                                │                                │
                ▼                                ▼                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PostgreSQL + S3 + S3 Vectors + SQS + Bedrock                               │
│ `docker-compose.yml`, `rag_model/rag_utils.py`, `index_handler.py`         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Next.js root app | Global providers, auth guard, nav shell | `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/src/app/layout.tsx` |
| Dashboard module | Tenant selection, knowledge CRUD, chat orchestration in one context | `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/src/app/dashboard/layout.tsx` |
| Auth boundary | Token persistence/validation and login state | `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/src/contexts/AuthContext.tsx` |
| API surface | Auth, tenant APIs, chat APIs, webhook handlers, config APIs | `ChatBotBE/backend/main.py` |
| Domain persistence | ORM entities and DB session lifecycle | `ChatBotBE/backend/models.py`, `ChatBotBE/backend/database.py` |
| RAG pipeline | Retrieval, chain construction, fallback strategy, indexing trigger | `ChatBotBE/backend/rag_model/rag_utils.py` |
| Conversation storage | S3-first history and local fallback utilities | `ChatBotBE/backend/rag_model/chat_data_utils.py` |
| Index worker | SQS-driven tenant indexing into tenant-scoped vector indexes | `ChatBotBE/backend/index_handler.py` |
| Runtime config | Per-tenant RAG config cache + S3/local persistence | `ChatBotBE/backend/rag_model/config_manager.py` |

## Pattern Overview

**Overall:** Layered monolith with sidecar serverless indexing.

**Key Characteristics:**
- One large HTTP entrypoint (`main.py`) coordinates multiple concerns directly.
- RAG logic is extracted into `rag_model/` modules and called synchronously from API handlers.
- Indexing is decoupled from request path by SQS + Lambda (`trigger_reindexing` → `index_handler.py`).

## Layers

**Presentation Layer:**
- Purpose: Render admin UI and collect operator actions.
- Location: `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/src/app/**`
- Contains: Route pages, dashboard shell, form handling.
- Depends on: `src/contexts/AuthContext.tsx`, `src/lib/api.ts`, `axios`.
- Used by: Browser users (admin panel).

**API Layer:**
- Purpose: Enforce auth, expose CRUD/chat/webhook/config endpoints.
- Location: `ChatBotBE/backend/main.py`
- Contains: FastAPI route handlers (`@app.*` routes at lines 105–1507).
- Depends on: `database.py`, `models.py`, `schemas.py`, `rag_model/*`.
- Used by: Frontend dashboard, public `/rag/ask/{tenant_id}`, external webhook providers.

**RAG Service Layer:**
- Purpose: Retrieval and response generation across multi-stage fallback.
- Location: `ChatBotBE/backend/rag_model/rag_utils.py`
- Contains: `retrieve_s3_vectors` (line 393), `get_rag_chain` (line 577), `answer_question_modern` (line 608).
- Depends on: Bedrock, S3 Vectors, S3, intelligent/advanced helper modules.
- Used by: Chat endpoints and webhook handlers in `main.py`.

**Persistence & Integration Layer:**
- Purpose: Store structured data and unstructured artifacts.
- Location: `ChatBotBE/backend/database.py`, `ChatBotBE/backend/models.py`, `ChatBotBE/backend/rag_model/chat_data_utils.py`
- Contains: SQLAlchemy models, DB sessions, conversation history IO.
- Depends on: PostgreSQL (`docker-compose.yml`), S3.
- Used by: API routes and background analysis (`/admin/run_analysis/`).

**Async Indexing Layer:**
- Purpose: Build/update vector indexes after knowledge changes.
- Location: `ChatBotBE/backend/index_handler.py`
- Contains: `lambda_handler` (line 300), `index_tenant_files` (line 196), vector upload batching.
- Depends on: SQS event payloads, S3 source files, Bedrock embeddings, S3 Vectors.
- Used by: SQS + Lambda runtime and API-triggered queue messages via `trigger_reindexing` in `rag_utils.py:75`.

## Data Flow

### Primary Request Path

1. Dashboard sends chat request to backend (`src/app/dashboard/layout.tsx:893-900`).
2. FastAPI `/chatbot/ask` route accepts tenant + message (`main.py:927-969`) and calls `answer_question_modern` (`main.py:942`).
3. RAG service runs intelligent → advanced → enhanced fallback chain (`rag_utils.py:608-779`) and returns response payload.
4. UI appends assistant message in dashboard state (`src/app/dashboard/layout.tsx:904-913`).

### Knowledge Indexing Flow

1. Frontend uploads URL/file to tenant knowledge endpoint (`src/app/dashboard/layout.tsx:752-771`).
2. FastAPI creates `KnowledgeBaseFile` DB record and uploads file/URL data (`main.py:608-685`).
3. Backend enqueues tenant reindex event (`main.py:684`, `rag_utils.py:75-85`).
4. Lambda `index_handler.lambda_handler` consumes SQS message (`index_handler.py:300-339`) and writes vectors into `tenant-{id}-index` (`index_handler.py:44-88`, `149-193`).

**State Management:**
- Frontend uses React context as a dashboard-wide mutable store (`src/app/dashboard/layout.tsx:271-1033`).
- Backend uses DB state for users/tenants/files and S3/S3 Vectors for chat artifacts and retrieval indexes.

## Key Abstractions

**Tenant-Scoped Vector Index:**
- Purpose: Hard tenant isolation for retrieval and indexing.
- Examples: `rag_model/rag_utils.py:41-48`, `index_handler.py:44-51`.
- Pattern: Index-per-tenant naming (`tenant-{tenant_id}-index`) instead of shared-index filtering.

**Conversation History Store:**
- Purpose: Preserve turn history for contextual replies and analytics.
- Examples: `rag_model/chat_data_utils.py:114-241`.
- Pattern: S3 primary storage with local `./uploads/conversation_history` fallback.

**Tenant Configuration Manager:**
- Purpose: Runtime tuning of chunking/retrieval/context/quality without code deploy.
- Examples: `rag_model/config_manager.py:18-337`, API routes in `main.py:1277-1538`.
- Pattern: Cached singleton manager with S3 + local mirrored persistence.

## Entry Points

**Admin Web App Entry:**
- Location: `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/src/app/layout.tsx`
- Triggers: Next.js app router bootstrap.
- Responsibilities: Provider composition and route guard wrapping.

**Backend API Entry:**
- Location: `ChatBotBE/backend/main.py`
- Triggers: `uvicorn main:app` (`ChatBotBE/backend/Dockerfile:53`).
- Responsibilities: All HTTP route registration and request orchestration.

**Indexer Worker Entry:**
- Location: `ChatBotBE/backend/index_handler.py`
- Triggers: AWS Lambda SQS invocation.
- Responsibilities: Parse queue payload, rebuild tenant vector data.

## Architectural Constraints

- **Threading:** FastAPI async handlers call blocking SDK/DB operations (boto3 + SQLAlchemy sync sessions) in-process (`main.py`, `rag_utils.py`), so throughput is constrained by worker/process settings.
- **Global state:** Module-level mutable/shared state exists in `main.py` (`SECRET_KEY`, token globals, tenant dicts) and `rag_utils.py` (global AWS clients); config singleton in `config_manager.py:318-327`.
- **Circular imports:** No explicit circular chain detected; defensive comment in `rag_utils.py:30` indicates import-order sensitivity.
- **Boundary constraint:** Routing, auth, webhooks, and config APIs remain in one file (`main.py`) instead of isolated routers/modules.

## Anti-Patterns

### God-Module API Layer

**What happens:** A single `main.py` file contains auth, tenant CRUD, KB CRUD, chat, webhooks, admin analysis, and config endpoints (`main.py:105-1507`).
**Why it's wrong:** Feature coupling increases regression risk and blocks isolated testing/refactoring.
**Do this instead:** Add bounded routers (for example `routers/auth.py`, `routers/tenants.py`, `routers/chat.py`) and keep `main.py` as composition root only.

### Mixed Storage Semantics in Same Handlers

**What happens:** Handlers mix S3-centric and local filesystem paths in single flows (`main.py:365-390`, `784-797`, `837-861`) while `chat_data_utils.py` already encapsulates fallback behavior.
**Why it's wrong:** Duplicated storage logic creates inconsistent behavior between environments.
**Do this instead:** Route all history/source file read-write through dedicated adapter utilities (`rag_model/chat_data_utils.py`, plus a matching KB storage utility).

## Error Handling

**Strategy:** Fail-fast with `HTTPException` at API boundary, and broad `try/except` fallback chains in RAG/indexing internals.

**Patterns:**
- API validation and authorization checks with direct HTTP status returns (`main.py:298-303`, `619-621`, `895-897`).
- Multi-stage fallback in answer generation (`rag_utils.py:647-779`) and S3→local fallback IO (`chat_data_utils.py:45-75`, `89-112`).

## Cross-Cutting Concerns

**Logging:** Primarily `print()` tracing across API, RAG, and Lambda files (`main.py`, `rag_utils.py`, `index_handler.py`).
**Validation:** Pydantic schemas for request/response contracts (`schemas.py`), plus ad hoc runtime guards in route handlers.
**Authentication:** OAuth2 password flow + JWT bearer token in backend (`main.py:45-97`, `130-174`) and cookie/localStorage checks in frontend (`AuthContext.tsx`, `middleware.ts`).

---

*Architecture analysis: 2026-05-14*
