# Coding Conventions

**Analysis Date:** 2026-05-14

## Naming Patterns

**Files:**
- Frontend uses PascalCase for components and providers (for example `src/components/AuthForm.tsx`, `src/components/RouteGuard.tsx`, `src/providers/QueryProvider.tsx`).
- Frontend route files use Next.js app-router conventions (`src/app/layout.tsx`, `src/app/dashboard/page.tsx`).
- Backend uses snake_case for Python modules and scripts (`ChatBotBE/backend/rag_model/rag_utils.py`, `ChatBotBE/backend/test_api_retrieval.py`).

**Functions:**
- Frontend functions and hooks use camelCase (`clearAuthData`, `registerUser`, `useAuth`) in `src/lib/api.ts` and `src/contexts/AuthContext.tsx`.
- Backend functions use snake_case (`get_current_user`, `create_access_token`, `ensure_vector_index`) in `ChatBotBE/backend/main.py` and `ChatBotBE/backend/rag_model/rag_utils.py`.

**Variables:**
- Frontend constants use UPPER_SNAKE_CASE for environment/config (`API_URL` in `src/lib/api.ts:3`), component state uses camelCase (`isLoadingAuth`, `phoneNumber`).
- Backend module constants use UPPER_SNAKE_CASE (`SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `S3_VECTORS_BUCKET_NAME`) in `ChatBotBE/backend/main.py` and `ChatBotBE/backend/rag_model/rag_utils.py`.

**Types:**
- Frontend types/interfaces use PascalCase (`AuthContextType`, `RegisterData`, `RouteGuardProps`) in `src/contexts/AuthContext.tsx` and `src/components/AuthForm.tsx`.
- Backend schema/model classes use PascalCase (`UserCreate`, `ChatResponse`, `TenantValues`) in `ChatBotBE/backend/schemas.py` and `ChatBotBE/backend/models.py`.

## Code Style

**Formatting:**
- Prettier config is not detected (`.prettierrc*` / `prettier.config.*` not found in repository scan).
- Frontend formatting is enforced indirectly through Next/ESLint defaults via `eslint.config.mjs:13-14`.
- Backend formatting tooling (Black/Ruff/isort) is not detected (no `pyproject.toml`, `setup.cfg`, `tox.ini`, `.flake8`, `ruff.toml` in `ChatBotBE/backend`).

**Linting:**
- Frontend linting uses ESLint flat config extending Next presets (`ChatBotFE/.../eslint.config.mjs:12-16`).
- Frontend lint command is `next lint` (`ChatBotFE/.../package.json:9`).
- Backend Python linting command/config is not detected.
- Frontend build explicitly bypasses lint failures (`ignoreDuringBuilds: true` in `ChatBotFE/.../next.config.ts:4-6`).

## Import Organization

**Order:**
1. External libraries first (for example `react`, `next/navigation`, `@tanstack/react-query` in `src/components/AuthForm.tsx:4-6`)
2. Internal alias imports next (`@/lib/api`, `@/contexts/AuthContext` in `src/components/AuthForm.tsx:7-9`)
3. Side-effect CSS imports in layout (`bootstrap/dist/css/bootstrap.min.css`, `./globals.css` in `src/app/layout.tsx:8-9`)

**Path Aliases:**
- Frontend uses `@/*` alias configured in `ChatBotFE/.../tsconfig.json:21-23`.
- Backend uses direct relative/module imports without aliasing (for example `from database import ...` in `ChatBotBE/backend/main.py:8`).

## Error Handling

**Patterns:**
- Frontend handles async API errors in mutation callbacks with status-specific branching (`src/components/AuthForm.tsx:85-124`).
- Frontend global 401 handling uses Axios response interceptor and redirect (`src/lib/api.ts:25-34`).
- Backend endpoints use `HTTPException` for API errors (`ChatBotBE/backend/main.py:72-76`, `:136-141`).
- Backend frequently wraps external calls in broad `try/except Exception` with `print` (`ChatBotBE/backend/rag_model/rag_utils.py:75-86`, `:127-142`).

## Logging

**Framework:** console / print

**Patterns:**
- Frontend uses `console.log` heavily for auth/routing diagnostics (`src/contexts/AuthContext.tsx:63`, `src/components/RouteGuard.tsx:27`).
- Backend primarily uses `print` statements for operational logs and errors (`ChatBotBE/backend/main.py:132`, `:144-147`; `ChatBotBE/backend/rag_model/rag_utils.py:83`, `:141`).
- Structured logging library usage is not detected.

## Comments

**When to Comment:**
- Inline explanatory comments are common around auth flow, route guards, and API behavior (`src/contexts/AuthContext.tsx:57`, `src/components/RouteGuard.tsx:17`, `src/lib/api.ts:24`).
- Backend comments document workflow phases and operations, especially in RAG utilities (`ChatBotBE/backend/rag_model/rag_utils.py:33-35`, `:114-116`, `:152-154`).

**JSDoc/TSDoc:**
- Formal JSDoc/TSDoc blocks are generally not used in frontend TS files; inline comments are used instead.
- Python docstrings are used selectively in backend scripts/functions (`ChatBotBE/backend/test_automatic_indexing.py:2-5`, `ChatBotBE/backend/rag_model/rag_utils.py:42-46`).

## Function Design

**Size:** 
- Frontend utility/provider functions are generally medium-sized (`src/lib/api.ts`, `src/providers/QueryProvider.tsx`).
- Several frontend and backend functions are large and multi-responsibility (for example `AuthForm` in `src/components/AuthForm.tsx`, endpoint + setup mix in `ChatBotBE/backend/main.py`).

**Parameters:** 
- Frontend uses typed object parameters for API calls (`registerUser(data: RegisterData)` in `src/lib/api.ts:51`).
- Backend uses typed function parameters inconsistently; some functions are typed (`def ensure_vector_index(tenant_id: int)` in `rag_utils.py:177`), others rely on runtime assumptions.

**Return Values:** 
- Frontend async API wrappers return `response.data` directly (`src/lib/api.ts:53`, `:64`).
- Backend returns ORM or dict payloads from endpoints (`ChatBotBE/backend/main.py:128`, `:170-174`).

## Module Design

**Exports:** 
- Frontend favors named exports for hooks/utilities/providers (`registerUser`, `loginUser`, `AuthProvider`, `useAuth`, `QueryProvider`).
- Frontend components are mostly default exports (`src/components/AuthForm.tsx`, `src/components/RouteGuard.tsx`, `src/components/ErrorBoundary.tsx`).
- Backend modules expose top-level functions/classes directly.

**Barrel Files:** 
- Barrel files (`index.ts`) are not detected in frontend source.

## Quality Risks Affecting Conventions

- Backend mixes production API code and temporary/diagnostic script style in one directory (`ChatBotBE/backend/main.py` alongside many `test_*.py`, `debug_*.py`, `diagnose_*.py` files).
- Backend has no detectable enforced formatter/linter, so style consistency depends on manual discipline.
- Frontend lint is configured but can be bypassed during build (`ChatBotFE/.../next.config.ts:4-6`), reducing gate strength.
- Backend `.gitignore` ignores `test_*.py` (`ChatBotBE/backend/.gitignore`, decoded lines 139-146), which makes test artifact/versioning practices fragile.

---

*Convention analysis: 2026-05-14*
