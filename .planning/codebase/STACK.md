# Technology Stack

**Analysis Date:** 2026-05-14

## Languages

**Primary:**
- Python 3.11 (containerized) - Backend API, RAG pipeline, and AWS Lambda handlers in `ChatBotBE/backend/main.py`, `ChatBotBE/backend/rag_model/rag_utils.py`, `ChatBotBE/backend/lambda_function_unified.py`, with runtime from `ChatBotBE/backend/Dockerfile`.
- TypeScript - Frontend app and middleware in `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/src/app/**/*.tsx`, `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/middleware.ts`.

**Secondary:**
- SQL (PostgreSQL usage via SQLAlchemy) - DB access configured in `ChatBotBE/backend/database.py` and compose service in `ChatBotBE/backend/docker-compose.yml`.
- Shell - Deployment and ops scripts in `ChatBotBE/backend/*.sh`.

## Runtime

**Environment:**
- Python 3.11-slim (`ChatBotBE/backend/Dockerfile`)
- Node.js 18-alpine (`ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/Dockerfile`)

**Package Manager:**
- pip (backend dependencies in `ChatBotBE/backend/requirements.txt`)
- npm (frontend dependencies in `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/package.json`)
- Lockfile: present (`ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/package-lock.json`, lockfileVersion 3)

## Frameworks

**Core:**
- FastAPI - Backend HTTP API and webhook server in `ChatBotBE/backend/main.py`
- Next.js 15 (App Router) - Frontend web app in `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/package.json` and `src/app/`
- SQLAlchemy - ORM/session layer in `ChatBotBE/backend/database.py` and `ChatBotBE/backend/crud.py`

**Testing:**
- Not detected as a dedicated framework in manifests; test-like scripts are standalone Python files such as `ChatBotBE/backend/test_api_retrieval.py` and `ChatBotBE/backend/test_automatic_indexing.py`.

**Build/Dev:**
- Uvicorn - ASGI server (`ChatBotBE/backend/requirements.txt`, `ChatBotBE/backend/Dockerfile`)
- ESLint (Next config) - lint tooling in `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/eslint.config.mjs`
- Tailwind/PostCSS - styling pipeline in `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/postcss.config.mjs`
- Docker + Docker Compose - local/prod orchestration in both `*/Dockerfile` and `*/docker-compose.yml`
- Nginx + Certbot containers - TLS termination/renewal in both compose files

## Key Dependencies

**Critical:**
- `langchain==0.3.27`, `langchain-community==0.3.27`, `langchain-aws==0.2.30` - RAG orchestration and Bedrock integration (`ChatBotBE/backend/requirements.txt`, `ChatBotBE/backend/rag_model/rag_utils.py`)
- `boto3`, `botocore` - AWS SDK for S3/SQS/Bedrock/S3 Vectors/Lambda (`ChatBotBE/backend/requirements.txt`, `ChatBotBE/backend/rag_model/rag_utils.py`)
- `fastapi`, `uvicorn`, `starlette` - API runtime (`ChatBotBE/backend/requirements.txt`, `ChatBotBE/backend/main.py`)
- `next@15.3.5`, `react@19`, `react-dom@19` - frontend runtime (`ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/package.json`)

**Infrastructure:**
- `psycopg2-binary` - PostgreSQL driver (`ChatBotBE/backend/requirements.txt`)
- `python-dotenv` - env file loading (`ChatBotBE/backend/database.py`)
- `@tanstack/react-query` - frontend server-state cache (`ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/src/providers/QueryProvider.tsx`)
- `axios` - frontend API client (`ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/src/lib/api.ts`)

## Configuration

**Environment:**
- Backend loads env values from an `env` file via `load_dotenv` in `ChatBotBE/backend/database.py`.
- Detected backend env file: `ChatBotBE/backend/env` (present; contents not inspected).
- Frontend relies on `NEXT_PUBLIC_API_URL` via `process.env` in `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/src/lib/api.ts`.
- Common backend vars used: `DATABASE_URI`, `AWS_DEFAULT_REGION`, `S3_BUCKET_NAME`, `S3_VECTORS_BUCKET_NAME`, `S3_VECTORS_INDEX_NAME` (seen in `ChatBotBE/backend/database.py`, `ChatBotBE/backend/rag_model/rag_utils.py`, `ChatBotBE/backend/debug_server_deployment.py`).

**Build:**
- Backend container build: `ChatBotBE/backend/Dockerfile`
- Backend compose stack: `ChatBotBE/backend/docker-compose.yml`
- Frontend container build: `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/Dockerfile`
- Frontend Next config: `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/next.config.ts`

## Platform Requirements

**Development:**
- Python 3.10+ indicated in docs (`ChatBotBE/backend/README.md`), with container baseline Python 3.11 (`ChatBotBE/backend/Dockerfile`)
- Node 18+ (Node 18 used in container image at `ChatBotFE/.../Dockerfile`)
- Docker/Compose for full stack (`ChatBotBE/backend/README.md`, both compose files)
- AWS account/services for core RAG features (`ChatBotBE/backend/README.md`)

**Production:**
- Dockerized deployment with Nginx reverse proxy + Certbot + app containers (`ChatBotBE/backend/docker-compose.yml`, `ChatBotFE/.../docker-compose.yml`)
- AWS managed services dependency for RAG path (S3, SQS, Lambda, Bedrock, S3 Vectors) implemented in `ChatBotBE/backend/rag_model/rag_utils.py` and Lambda handler files.

---

*Stack analysis: 2026-05-14*
