# Codebase Structure

**Analysis Date:** 2026-05-14

## Directory Layout

```text
RAG365/
├── ChatBotBE/backend/                                    # FastAPI API + RAG + indexing workers
│   ├── main.py                                           # API entrypoint and route registration
│   ├── rag_model/                                        # Retrieval, config, context, quality modules
│   ├── docs/                                             # Architecture/deployment workflow docs
│   ├── uploads/                                          # Local fallback artifacts (conversation history)
│   └── index_handler.py                                  # Lambda indexing entrypoint
├── ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/  # Next.js admin frontend
│   ├── src/app/                                          # App Router pages and nested dashboard routes
│   ├── src/components/                                   # Shared UI components
│   ├── src/contexts/                                     # Auth context
│   ├── src/lib/                                          # API helper calls
│   └── middleware.ts                                     # Route-level auth redirects
└── .planning/codebase/                                   # Generated codebase mapping docs
```

## Directory Purposes

**`ChatBotBE/backend/`:**
- Purpose: Core backend runtime, integrations, and operational scripts.
- Contains: FastAPI app (`main.py`), SQLAlchemy files (`database.py`, `models.py`), Lambda handlers, shell/python diagnostics.
- Key files: `ChatBotBE/backend/main.py`, `ChatBotBE/backend/database.py`, `ChatBotBE/backend/models.py`, `ChatBotBE/backend/index_handler.py`.

**`ChatBotBE/backend/rag_model/`:**
- Purpose: RAG-domain service layer separated from HTTP transport.
- Contains: Retrieval (`rag_utils.py`), intelligent processing (`intelligent_query_processor.py`), context/quality systems, config manager.
- Key files: `ChatBotBE/backend/rag_model/rag_utils.py`, `ChatBotBE/backend/rag_model/chat_data_utils.py`, `ChatBotBE/backend/rag_model/config_manager.py`.

**`ChatBotBE/backend/docs/`:**
- Purpose: Operational architecture notes for indexing/retrieval/deployment/tenant isolation.
- Contains: `1_INDEXING_WORKFLOW.md` through `4_TENANT_ISOLATION.md`.
- Key files: `ChatBotBE/backend/docs/1_INDEXING_WORKFLOW.md`, `ChatBotBE/backend/docs/2_RETRIEVAL_WORKFLOW.md`.

**`ChatBotBE/backend/uploads/`:**
- Purpose: Local filesystem fallback storage for conversation history.
- Contains: Tenant-scoped JSON history files under `uploads/conversation_history/{tenant_id}/`.
- Key files: `ChatBotBE/backend/uploads/conversation_history/`.

**`ChatBotFE/.../rag-admin-frontend/src/app/`:**
- Purpose: Next.js App Router route tree.
- Contains: Public routes (`page.tsx`, `login/page.tsx`, `register/page.tsx`, `pricing/page.tsx`) and dashboard subtree.
- Key files: `.../src/app/layout.tsx`, `.../src/app/dashboard/layout.tsx`, `.../src/app/dashboard/chat/page.tsx`.

**`ChatBotFE/.../rag-admin-frontend/src/components/`:**
- Purpose: Reusable client components.
- Contains: Auth UI, nav, route guard, error boundary.
- Key files: `.../src/components/AuthForm.tsx`, `.../src/components/NavBar.tsx`, `.../src/components/RouteGuard.tsx`.

**`ChatBotFE/.../rag-admin-frontend/src/contexts/`:**
- Purpose: Cross-route auth state.
- Contains: Context provider and token lifecycle logic.
- Key files: `.../src/contexts/AuthContext.tsx`.

## Key File Locations

**Entry Points:**
- `ChatBotBE/backend/main.py`: FastAPI service entry and all HTTP endpoints.
- `ChatBotBE/backend/index_handler.py`: Lambda SQS indexing worker entry.
- `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/src/app/layout.tsx`: Frontend root layout entry.

**Configuration:**
- `ChatBotBE/backend/docker-compose.yml`: Backend runtime topology (nginx, backend, postgres).
- `ChatBotBE/backend/Dockerfile`: Backend image build and uvicorn command.
- `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/next.config.ts`: Next.js build config.
- `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/tsconfig.json`: TypeScript config and `@/*` alias.

**Core Logic:**
- `ChatBotBE/backend/rag_model/rag_utils.py`: RAG retrieval/indexing orchestration.
- `ChatBotBE/backend/rag_model/chat_data_utils.py`: Conversation history and analytics.
- `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/src/app/dashboard/layout.tsx`: Dashboard state + API orchestration context.

**Testing:**
- `ChatBotBE/backend/test_*.py`: Backend integration/diagnostic tests (e.g., `test_api_retrieval.py`, `test_automatic_indexing.py`).
- `ChatBotFE/.../rag-admin-frontend`: No dedicated test directory detected.

## Naming Conventions

**Files:**
- Backend modules/scripts use `snake_case.py` (example: `rag_model/intelligent_query_processor.py`).
- Frontend route files follow Next.js conventions (`page.tsx`, `layout.tsx`) and component files use PascalCase (`AuthForm.tsx`).

**Directories:**
- Frontend feature directories map to URL segments (`src/app/dashboard/chat`, `src/app/dashboard/knowledge`).
- Backend domain directory groups related logic under `rag_model/`.

## Where to Add New Code

**New Backend API Feature:**
- Primary code: add route handler in `ChatBotBE/backend/main.py` only if staying consistent with current structure; preferred immediate modular placement is a new module under `ChatBotBE/backend/` imported by `main.py`.
- Tests: add backend tests as `ChatBotBE/backend/test_<feature>.py`.

**New RAG capability:**
- Implementation: add module under `ChatBotBE/backend/rag_model/` and integrate via `rag_utils.py`.
- API exposure: wire endpoint in `ChatBotBE/backend/main.py` under relevant tenant/chat/config section.

**New Frontend Dashboard capability:**
- Route UI: add new route under `.../src/app/dashboard/<feature>/page.tsx`.
- Shared dashboard state/actions: extend `.../src/app/dashboard/layout.tsx` context if feature needs global dashboard state.

**New Frontend shared UI component:**
- Implementation: `.../src/components/<ComponentName>.tsx`.
- If auth/stateful: consume `.../src/contexts/AuthContext.tsx` and `.../src/app/dashboard/layout.tsx` context hooks.

**Utilities:**
- Backend shared helpers: `ChatBotBE/backend/rag_model/` for RAG domain utilities or `ChatBotBE/backend/` for generic service helpers.
- Frontend API wrappers: `.../src/lib/api.ts`.

## Special Directories

**`ChatBotBE/backend/venv/`:**
- Purpose: Python virtual environment directory.
- Generated: Yes.
- Committed: Yes (present in repository snapshot).

**`ChatBotBE/backend/test_logs/`:**
- Purpose: Runtime log and sqlite artifacts for diagnostics/performance.
- Generated: Yes.
- Committed: Yes.

**`ChatBotBE/backend/uploads/`:**
- Purpose: Runtime content/history fallback storage.
- Generated: Yes.
- Committed: Yes.

**`ChatBotFE/.../rag-admin-frontend/node_modules/`:**
- Purpose: Frontend package install output.
- Generated: Yes.
- Committed: Yes (present in repository snapshot).

**`ChatBotBE/backend/env`:**
- Purpose: Environment configuration file (secrets/config values).
- Generated: No (managed file).
- Committed: Yes.

---

*Structure analysis: 2026-05-14*
