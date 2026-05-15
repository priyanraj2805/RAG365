# External Integrations

**Analysis Date:** 2026-05-14

## APIs & External Services

**AWS (Core RAG + Infra):**
- Amazon S3 - Document/object storage for tenant knowledge files
  - SDK/Client: `boto3` clients in `ChatBotBE/backend/rag_model/rag_utils.py`, `ChatBotBE/backend/lambda_function_unified.py`
  - Auth: AWS credential environment (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) wired in `ChatBotBE/backend/docker-compose.yml`
- Amazon S3 Vectors - Vector index storage and retrieval
  - SDK/Client: `boto3.client('s3vectors')` in `ChatBotBE/backend/rag_model/rag_utils.py`
  - Auth: AWS credential chain; bucket/index names from `S3_VECTORS_BUCKET_NAME` / `S3_VECTORS_INDEX_NAME`
- Amazon Bedrock Runtime - Embeddings and LLM inference
  - SDK/Client: `boto3.client('bedrock-runtime')` + `langchain_aws` in `ChatBotBE/backend/rag_model/rag_utils.py`
  - Auth: AWS credential chain; region via `AWS_DEFAULT_REGION`
- Amazon SQS - Reindex queueing
  - SDK/Client: `boto3.client('sqs')` in `ChatBotBE/backend/rag_model/rag_utils.py`
  - Auth: AWS credential chain; queue URL configured in code (`INDEXING_QUEUE_URL` in `ChatBotBE/backend/rag_model/rag_utils.py`)
- AWS Lambda - Indexing execution/deploy scripts
  - SDK/Client: `boto3.client('lambda')` in `ChatBotBE/backend/deploy_lambda_fix.py`, `ChatBotBE/backend/deploy_fixed_lambda.py`
  - Auth: AWS credential chain

**Messaging/Social Platforms:**
- Facebook Graph API - Sends chatbot replies and webhook processing
  - SDK/Client: `httpx.AsyncClient` POST to `graph.facebook.com` in `ChatBotBE/backend/main.py`
  - Auth: per-tenant access token from DB fields (`tenant.fb_access_token`) in `ChatBotBE/backend/main.py`
- Instagram Graph API - Sends chatbot replies and webhook processing
  - SDK/Client: `httpx.AsyncClient` POST to `graph.instagram.com` in `ChatBotBE/backend/main.py`
  - Auth: per-tenant token (`tenant.insta_access_token`)
- Telegram Bot API - Bot replies for webhook flow
  - SDK/Client: `httpx.AsyncClient` POST to `api.telegram.org` in `ChatBotBE/backend/main.py`
  - Auth: per-tenant bot token (`tenant.telegram_bot_token`)

**Notification/Webhook Outbound:**
- Slack Incoming Webhook
  - SDK/Client: `requests.post` in `ChatBotBE/backend/rag_model/alerting_system.py`
  - Auth: `slack_webhook_url` in runtime alert config
- Generic outbound webhook callback
  - SDK/Client: `requests.post` in `ChatBotBE/backend/rag_model/alerting_system.py`
  - Auth: `webhook_url` in runtime alert config

## Data Storage

**Databases:**
- PostgreSQL
  - Connection: `DATABASE_URI` (`ChatBotBE/backend/database.py`)
  - Client: SQLAlchemy ORM/session (`ChatBotBE/backend/database.py`, `ChatBotBE/backend/crud.py`)
  - Local compose DB service: `postgres:15` in `ChatBotBE/backend/docker-compose.yml`

**File Storage:**
- AWS S3 for knowledge files and conversation/config artifacts (`ChatBotBE/backend/rag_model/rag_utils.py`, `ChatBotBE/backend/rag_model/chat_data_utils.py`, `ChatBotBE/backend/rag_model/config_manager.py`)
- Local uploads mount in backend container (`ChatBotBE/backend/docker-compose.yml`)

**Caching:**
- In-memory Python cache for tenant RAG config with TTL in `ChatBotBE/backend/rag_model/config_manager.py` (`_config_cache`, `_cache_timestamps`)
- Frontend query cache via React Query in `ChatBotFE/.../src/providers/QueryProvider.tsx`

## Authentication & Identity

**Auth Provider:**
- Custom JWT auth (FastAPI + OAuth2PasswordBearer)
  - Implementation: token issue/verify in `ChatBotBE/backend/main.py`; password hashing via Passlib Argon2 (`CryptContext`) and user persistence via SQLAlchemy.

## Monitoring & Observability

**Error Tracking:**
- No dedicated SaaS error tracker detected.

**Logs:**
- Application uses print/logging statements in backend modules (`ChatBotBE/backend/main.py`, `ChatBotBE/backend/rag_model/quality_monitor.py`)
- AWS CloudWatch Logs interaction scripts via `boto3.client('logs')` in `ChatBotBE/backend/fetch_lambda_logs.py`, `ChatBotBE/backend/check_recent_logs.py`
- Local test/perf logs persisted under `ChatBotBE/backend/test_logs/`

## CI/CD & Deployment

**Hosting:**
- Containerized deployment (Nginx + app containers + Certbot) via compose files in:
  - `ChatBotBE/backend/docker-compose.yml`
  - `ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend/docker-compose.yml`
- Serverless indexing path via AWS Lambda handler files (`ChatBotBE/backend/index_handler.py`, `ChatBotBE/backend/lambda_function_unified.py`)

**CI Pipeline:**
- Not detected (`.github/workflows` not present in scanned repo).

## Environment Configuration

**Required env vars:**
- Backend core: `DATABASE_URI` (`ChatBotBE/backend/database.py`)
- AWS: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` (`ChatBotBE/backend/docker-compose.yml`, `ChatBotBE/backend/rag_model/rag_utils.py`)
- Storage/indexing: `S3_BUCKET_NAME`, `S3_VECTORS_BUCKET_NAME`, `S3_VECTORS_INDEX_NAME` (`ChatBotBE/backend/rag_model/rag_utils.py`, `ChatBotBE/backend/debug_server_deployment.py`)
- Frontend API base: `NEXT_PUBLIC_API_URL` (`ChatBotFE/.../src/lib/api.ts`, `ChatBotFE/.../docker-compose.yml`)

**Secrets location:**
- Backend env file detected at `ChatBotBE/backend/env` (present; contents not inspected)
- Compose variable interpolation for AWS/frontend vars in both compose files.

## Webhooks & Callbacks

**Incoming:**
- Facebook/Instagram webhook verify + ingest:
  - `GET /webhook/{tenant_id}` and `POST /webhook/{tenant_id}` in `ChatBotBE/backend/main.py`
- Telegram webhook ingest:
  - `POST /webhook/telegram/{tenant_id}` in `ChatBotBE/backend/main.py`

**Outgoing:**
- Social message delivery callbacks:
  - Facebook/Instagram message send from `send_reply()` in `ChatBotBE/backend/main.py`
  - Telegram send from `send_telegram_reply()` in `ChatBotBE/backend/main.py`
- Slack/webhook notifications from `ChatBotBE/backend/rag_model/alerting_system.py`

---

*Integration audit: 2026-05-14*
