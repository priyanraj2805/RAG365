# RAG365 Enterprise Platform — Implementation Plan

> **Project:** RAG24 AI Chatbot Platform → Enterprise RAG365
> **Duration:** 16 Weeks | 8 Sprints × 2 Weeks
> **Architecture:** Microservice-based, Cloud-native (AWS)
> **Goal:** Transform the current RAG24 monolith into a production-ready enterprise RAG platform supporting 100 tenants, 10,000 concurrent users, and 99.9% uptime SLA.

---

## Table of Contents

1. [Current System Baseline](#1-current-system-baseline)
2. [Microservice Architecture](#2-microservice-architecture)
3. [Service Catalogue](#3-service-catalogue)
4. [Sprint-by-Sprint Implementation Plan](#4-sprint-by-sprint-implementation-plan)
5. [Master Timeline](#5-master-timeline)
6. [Dependency Map](#6-dependency-map)
7. [Technology Stack per Service](#7-technology-stack-per-service)
8. [Risk Register & Mitigation](#8-risk-register--mitigation)
9. [Success Metrics & KPIs](#9-success-metrics--kpis)

---

## 1. Current System Baseline

### What Is Already Built

| Component | Technology | Completion |
|---|---|---|
| Backend API | FastAPI + PostgreSQL | ~70% |
| AI/LLM Layer | AWS Bedrock (Llama 3 8B, Claude 3 Sonnet) | Active |
| Vector Storage | AWS S3 Vectors (tenant-isolated) | Active |
| Indexing Pipeline | SQS + Lambda | 60% — needs optimization |
| Authentication | JWT + Argon2 | Basic — no RBAC |
| Document Ingestion | PDF, DOCX, CSV, JSON + URL crawling | Text-only, no table/image extraction |
| Social Media | Facebook, Instagram, Telegram connectors | Active |
| Conversation Tracking | Basic analytics | 70% |
| Search | Vector similarity only | No hybrid/BM25 |

### Gaps to Close

- No source citations, no hallucination guards
- No RBAC, no audit logs, no GDPR compliance
- No hybrid search (BM25 + vector), no re-ranking
- No PDF table/image extraction
- No multi-language, no feedback loop, no prompt versioning
- No agentic reasoning, no enterprise data connectors
- Single-instance — not horizontally scalable

---

## 2. Microservice Architecture

### Why Microservices?

The current system is a **FastAPI monolith**. As we add 19 enterprise features — each with distinct scaling needs, failure boundaries, and release cycles — decomposing into microservices is essential. Benefits:

- **Independent deployment:** Each service can be released, rolled back, and scaled without touching others.
- **Fault isolation:** A failure in the Agentic Reasoning Service does not bring down core chat.
- **Targeted scaling:** The Document Ingestion Service and PDF Processor need burst capacity; the Auth Service does not.
- **Team parallelism:** Multiple developers can own separate services simultaneously.
- **Tech flexibility:** The Agent Orchestration Service can use LangGraph while the Translation Service wraps AWS Translate — no coupling.

### High-Level Architecture Diagram

```
                          ┌─────────────────────────────────┐
  Users / Clients         │        API Gateway / BFF         │
  (Web, Mobile, API)  --> │  (Rate limiting, Auth routing,   │
                          │   Request validation)             │
                          └────────────┬────────────────────┘
                                       │
               ┌───────────────────────┼───────────────────────┐
               │                       │                       │
   ┌───────────▼──────┐   ┌────────────▼────────┐  ┌──────────▼──────────┐
   │  Auth & RBAC     │   │  Chat & Conversation │  │  Document Ingestion  │
   │  Service         │   │  Service             │  │  Service             │
   └──────────────────┘   └─────────────────────┘  └─────────────────────┘
               │                       │                       │
   ┌───────────▼──────┐   ┌────────────▼────────┐  ┌──────────▼──────────┐
   │  Retrieval &     │   │  Agent Orchestration │  │  PDF Processing     │
   │  Search Service  │   │  Service (LangGraph) │  │  Service            │
   └──────────────────┘   └─────────────────────┘  └─────────────────────┘
               │                       │                       │
   ┌───────────▼──────┐   ┌────────────▼────────┐  ┌──────────▼──────────┐
   │  Observability & │   │  Prompt Management   │  │  Connector Service  │
   │  Cost Service    │   │  Service             │  │  (SharePoint, GDrive│
   └──────────────────┘   └─────────────────────┘  │   Confluence, NTRS) │
               │                                    └─────────────────────┘
   ┌───────────▼──────┐   ┌─────────────────────┐
   │  Feedback        │   │  Translation Service │
   │  Service         │   │  (AWS Translate)     │
   └──────────────────┘   └─────────────────────┘

              ─────────── Shared Infrastructure ───────────
              PostgreSQL (RDS) │ S3 Vectors │ Redis Cache
              SQS │ Lambda │ AWS Bedrock │ CloudWatch
```

### Communication Patterns

| Pattern | Used For |
|---|---|
| **REST (sync)** | Client-facing APIs (chat, auth, feedback, prompt management) |
| **SQS (async)** | Document ingestion queue, indexing jobs, agentic tool calls |
| **Event bus (SNS)** | Cross-service notifications (indexing complete, cost alert fired) |
| **Redis Pub/Sub** | Real-time indexing status updates to clients |
| **Internal gRPC** (optional, Sprint 6+) | High-frequency calls between Retrieval and Reranking services |

---

## 3. Service Catalogue

### 3.1 API Gateway / BFF Service
**Responsibility:** Single entry point for all clients. Handles rate limiting, JWT verification hand-off to Auth Service, request routing, and response aggregation.
**Key endpoints:** `/chat`, `/documents`, `/admin/*`, `/feedback`, `/agent`
**Scales with:** All user-facing traffic — horizontal auto-scale.

---

### 3.2 Auth & RBAC Service
**Responsibility:** JWT issuance, token validation, role management (Admin / Editor / Viewer), per-tenant permission enforcement.
**Database:** PostgreSQL — `users`, `roles`, `tenant_roles`, `permissions` tables.
**Triggered by:** Sprint 1 (JWT foundation exists), Sprint 2 (RBAC added).

---

### 3.3 Chat & Conversation Service
**Responsibility:** Multi-turn conversation management, context window management (50 messages + auto-summarization), response streaming to clients.
**Key features:** Feature 3 (Enhanced Conversation Memory), response assembly with citations.
**State:** PostgreSQL + Redis for hot session state.

---

### 3.4 Document Ingestion Service
**Responsibility:** Receives uploaded documents, queues them to SQS, manages indexing lifecycle (PENDING → INDEXING → COMPLETE → FAILED), triggers PDF Processing Service.
**Key features:** Feature 2 (Real-time Knowledge Updates — sub-2-min indexing), Feature 9 (Advanced Document Processing).
**Infrastructure:** SQS + Lambda workers, status events via SNS.

---

### 3.5 PDF Processing Service
**Responsibility:** Full-page extraction pipeline — text via pdfplumber, tables converted to markdown, images extracted via pdf2image and captioned via BLIP-2/LLaVA. Feeds chunks to Retrieval Service for indexing.
**Key features:** Feature 9 (Advanced Doc Processing), Feature 18 (Vectorless RAG / Hybrid Page Indexing).
**Infrastructure:** Lambda or ECS task (GPU instance optional for BLIP-2; CPU quantized model as default).

---

### 3.6 Retrieval & Search Service
**Responsibility:** Dual-index search — vector search via S3 Vectors + BM25 via PostgreSQL tsvector. RRF fusion, cross-encoder re-ranking. Returns ranked document chunks with metadata.
**Key features:** Feature 8 (Hybrid Search + RRF), Feature 16 (Cross-Encoder Re-ranking).
**Scales with:** Query volume — stateless, horizontally scalable.

---

### 3.7 Agent Orchestration Service
**Responsibility:** LangGraph-based multi-step reasoning agents. Tool registry: `rag_search`, `web_search`, `summarize_text`, `decompose_query`. Logs reasoning trace per query.
**Key features:** Feature 17 (Agentic RAG).
**Safeguards:** Max 10 steps, 30-second timeout per agent run.

---

### 3.8 Observability & Cost Service
**Responsibility:** Ingests query logs, computes aggregated metrics (latency, error rate, token usage, per-tenant costs), exposes dashboard APIs, triggers CloudWatch alarms.
**Key features:** Feature 5 (Observability & Monitoring), Feature 6 (Cost Monitoring).
**Infrastructure:** CloudWatch, async log consumers from SQS.

---

### 3.9 Feedback Service
**Responsibility:** Stores thumbs-up/down ratings and comments per response. Computes lowest-rated query patterns for admin dashboards.
**Key features:** Feature 10 (Feedback Loop).
**Database:** PostgreSQL `feedback` table.

---

### 3.10 Prompt Management Service
**Responsibility:** Version-controlled system prompts stored in DB. Serves active prompt at query time without restart. A/B test framework (50/50 traffic split with per-version logging).
**Key features:** Feature 11 (Prompt Management).

---

### 3.11 Translation Service
**Responsibility:** Language detection on every incoming query, English translation for retrieval, back-translation of response to user's language.
**Key features:** Feature 12 (Multi-language Support — 10 languages).
**Infrastructure:** Wraps AWS Translate with Redis caching for repeated phrase translations.

---

### 3.12 Connector Service
**Responsibility:** OAuth2 connectors for SharePoint, Confluence, Google Drive; database connectors for MySQL/PostgreSQL; NASA NTRS PDF upload handler. Incremental sync scheduler.
**Key features:** Feature 13 (Multi-source Integration), Feature 19 (NASA NTRS Connector).
**Infrastructure:** Scheduled Lambda jobs per connector, sync status persisted in PostgreSQL.

---

### 3.13 Enterprise Security & Compliance Service
**Responsibility:** Immutable audit log writer (append-only), GDPR DSAR handler (72-hour deletion SLA), data retention policy enforcer.
**Key features:** Feature 4 (RBAC audit trail), Feature 14 (Enterprise Security & Compliance).
**Infrastructure:** Append-only audit table in PostgreSQL + AWS KMS for encryption.

---

## 4. Sprint-by-Sprint Implementation Plan

---

### Sprint 1 — Quick Wins (Weeks 1–2)

**Objective:** Deliver three high-value, low-complexity features that immediately improve user trust and system performance.

**Features:**

#### Feature 1 — Source Citations (3 days)
- **Service:** Chat & Conversation Service
- **What to build:**
  - Attach `source_document`, `page_number`, and `text_snippet` metadata to every retrieved chunk during RAG retrieval.
  - Format citations block in LLM response template.
  - Fallback message when no citations are available (never silent failure).
- **Acceptance:** Every RAG response includes ≥1 citation. All response modes (detailed/summary/both) support citations.

#### Feature 2 — Real-time Knowledge Updates (5 days)
- **Service:** Document Ingestion Service
- **What to build:**
  - Refactor Lambda indexing workers for parallel chunk processing.
  - Add status polling endpoint: `GET /documents/{id}/status` → `PENDING / INDEXING / COMPLETE / FAILED`.
  - SNS notification on completion/failure; retry with exponential backoff on failure.
- **Acceptance:** p95 indexing latency < 120 seconds. Failed indexing triggers retry and error notification.

#### Feature 3 — Enhanced Conversation Memory (4 days)
- **Service:** Chat & Conversation Service
- **What to build:**
  - Expand context window to 50 messages per session in PostgreSQL.
  - Implement summarization job: when conversation exceeds 50 messages, oldest messages compressed using Bedrock summarization call.
  - Store compressed summary with key-fact metadata.
- **Acceptance:** Last 50 messages retained. Summarization preserves >90% of key facts.

**Sprint 1 Deliverables:**
- [ ] Citation extraction module in Chat Service
- [ ] Optimized SQS/Lambda parallel indexing pipeline
- [ ] Document status API endpoint
- [ ] Conversation summarization job (Bedrock)

---

### Sprint 2 — Security & Observability (Weeks 3–4)

**Objective:** Harden the platform with role-based access control and give operators full visibility.

**Features:**

#### Feature 4 — Secure Data Access & RBAC (6 days)
- **Service:** Auth & RBAC Service (new service, extracted from monolith)
- **What to build:**
  - Database tables: `roles`, `tenant_user_roles`, `permissions`.
  - Middleware: enforce role checks on every API endpoint.
  - Three roles: Admin (full access), Editor (upload + KB manage), Viewer (query only).
  - Role assignment API for Admins. All assignments logged to audit trail.
- **Acceptance:** HTTP 403 on unauthorized access. Role assignments in audit log.

#### Feature 5 — Observability & Monitoring (5 days)
- **Service:** Observability & Cost Service (new service)
- **What to build:**
  - Query log table: `tenant_id, user_id, query, response_time, model_used, token_count, timestamp`.
  - Dashboard API: aggregated metrics by day/week/month.
  - CloudWatch alarms: p95 latency > 3s → alert; error rate > 1% → alert.
- **Acceptance:** All queries logged. Dashboard API live. CloudWatch alarms active.

#### Feature 6 — Cost Monitoring (3 days)
- **Service:** Observability & Cost Service
- **What to build:**
  - Per-LLM-call logging: `input_tokens, output_tokens, model_id, estimated_cost_usd`.
  - Cost dashboard API: totals by tenant, model, time period.
  - Configurable per-tenant monthly cost threshold alert.
- **Acceptance:** 100% cost attribution per tenant. Threshold alert fires correctly.

**Sprint 2 Deliverables:**
- [ ] Auth & RBAC Service deployed (isolated from monolith)
- [ ] Role assignment and enforcement middleware
- [ ] Observability & Cost Service with query log schema
- [ ] CloudWatch alarm configuration

---

### Sprint 3 — Quality & Search (Weeks 5–6)

**Objective:** Drastically improve retrieval quality and document understanding.

**Features:**

#### Feature 7 — Hallucination Guardrails (5 days)
- **Service:** Retrieval & Search Service + Chat Service
- **What to build:**
  - Confidence scoring: cosine similarity between query and top-retrieved chunks → score 0.0–1.0.
  - Threshold filter (default 0.6, configurable per tenant): responses below threshold return "low confidence" disclaimer.
  - Confidence score included in every API response payload.
- **Acceptance:** Hallucination rate < 5% on test set. Low-confidence disclaimer shown when score < threshold.

#### Feature 8 — Hybrid Search: BM25 + Vector + RRF (6 days)
- **Service:** Retrieval & Search Service
- **What to build:**
  - BM25 implementation using PostgreSQL `tsvector` / `tsquery` on chunk content.
  - RRF fusion layer: combine BM25 ranked list and vector similarity ranked list with configurable weights.
  - Tenant-level BM25/vector weight ratio config API.
- **Acceptance:** Search relevance +25% vs. vector-only baseline. BM25 exact-match (acronyms, report numbers) working.

#### Feature 9 — Advanced Document Processing (7 days)
- **Service:** PDF Processing Service (new service)
- **What to build:**
  - `pdfplumber` for text + table extraction per page.
  - `pdf2image` + `poppler` for page-to-image conversion.
  - BLIP-2 (quantized, CPU-compatible) for image captioning.
  - `camelot-py` as fallback table extractor.
  - Output: text chunks + table (markdown) chunks + image caption chunks, all tagged with `page_number, content_type, source_file`.
  - Graceful fallback to plain text if image/table extraction fails.
- **Acceptance:** Tables → markdown with column headers. Images → captions. Multi-column PDFs handled without garbling.

**Sprint 3 Deliverables:**
- [ ] Confidence scoring engine in Retrieval Service
- [ ] PostgreSQL tsvector BM25 index on chunk table
- [ ] RRF fusion module
- [ ] PDF Processing Service with text + table + image pipeline

---

### Sprint 4 — User Experience (Weeks 7–8)

**Objective:** Personalise the platform, unlock global reach, and create a quality feedback loop.

**Features:**

#### Feature 10 — Feedback Loop (4 days)
- **Service:** Feedback Service (new service)
- **What to build:**
  - `POST /feedback` endpoint: `response_id, rating (+1/-1), optional comment`.
  - Feedback stored per tenant with `timestamp, user_id`.
  - Dashboard: top 10 lowest-rated query patterns per week.
- **Acceptance:** Feedback stored. Dashboard API live.

#### Feature 11 — Prompt Management (6 days)
- **Service:** Prompt Management Service (new service)
- **What to build:**
  - DB table: `prompts` — `id, version, content, status (draft/active/archived), created_by`.
  - Active prompt fetched at query time (no restart needed).
  - A/B test framework: 50/50 traffic split, logs `prompt_version_id` per response.
  - Approval workflow: Admin promotes draft → active.
- **Acceptance:** Active prompt loads without restart. A/B test logs version per response.

#### Feature 12 — Multi-language Support (6 days)
- **Service:** Translation Service (new service)
- **What to build:**
  - Language detection on every query (Amazon Comprehend or `langdetect`).
  - Translate query → English for retrieval (AWS Translate).
  - Translate response → detected language before returning to user.
  - Language usage analytics logged to Observability Service.
  - Redis caching for repeated translation pairs.
- **Supported languages:** English, Spanish, French, German, Arabic, Hindi, Portuguese, Japanese, Chinese, Korean.
- **Acceptance:** Translation accuracy > 90% on benchmark. Language auto-detected correctly.

**Sprint 4 Deliverables:**
- [ ] Feedback Service with dashboard API
- [ ] Prompt Management Service with versioning + A/B framework
- [ ] Translation Service (detect → translate → respond → back-translate)

---

### Sprint 5 — Enterprise Integration (Weeks 9–10)

**Objective:** Connect the platform to enterprise data sources and achieve regulatory compliance.

**Features:**

#### Feature 13 — Multi-source Data Integration (8 days)
- **Service:** Connector Service (new service)
- **What to build:**
  - OAuth2 connectors: SharePoint, Confluence, Google Drive.
  - Database connector: MySQL / PostgreSQL via JDBC.
  - Incremental sync: detect changed/deleted files since last sync using delta tokens / etags.
  - Sync status dashboard: `last_sync_time, files_added, files_removed, errors` per connector.
  - Scheduled Lambda jobs per connector (configurable interval).
- **Acceptance:** Sync reliability > 99.5% over 30 days. Status visible in dashboard.

#### Feature 14 — Enterprise Security & Compliance (7 days)
- **Service:** Enterprise Security & Compliance Service (new service)
- **What to build:**
  - Append-only audit log table in PostgreSQL (all data access, modification, deletion events).
  - GDPR DSAR endpoint: `POST /gdpr/dsar` → deletes all user data within 72 hours.
  - Data retention policy engine: per-tenant configurable retention (e.g., delete conversations after 90 days), automated cleanup job.
  - AES-256 encryption at rest via AWS KMS; TLS 1.2+ enforced in transit.
- **Acceptance:** 100% audit trail coverage. DSAR 72-hour SLA. Zero unauthorized access.

**Sprint 5 Deliverables:**
- [ ] Connector Service: SharePoint, Confluence, Google Drive, DB connectors
- [ ] Incremental sync engine + scheduler
- [ ] Audit log service (append-only)
- [ ] GDPR DSAR endpoint + data retention engine

---

### Sprint 6 — Scale & Polish (Weeks 11–12)

**Objective:** Make the platform ready for 10× traffic growth with zero-downtime scaling.

**Features:**

#### Feature 15 — Scalable Architecture (6 days)
- **Service:** All services + Infrastructure layer
- **What to build:**
  - **Redis cache layer:** TTL-based caching for repeated query results. Target: >70% cache hit rate.
  - **Connection pooling:** PgBouncer for PostgreSQL; AWS Bedrock connection pool with retry logic.
  - **Application Load Balancer (ALB):** Distribute traffic across service instances.
  - **Auto-scaling groups:** ECS task auto-scaling per service based on CPU/memory.
  - **Read replicas:** PostgreSQL read replicas for dashboard + analytics queries.
  - **Load testing:** Validate p95 < 2s at 10× baseline traffic with k6 or Locust.
- **Acceptance:** p95 latency < 2s at 10× load. Cache hit > 70%. Zero downtime during scale events.

**Sprint 6 Deliverables:**
- [ ] Redis cluster deployed with query result caching
- [ ] PgBouncer connection pooling
- [ ] ALB + ECS auto-scaling configured per service
- [ ] PostgreSQL read replicas for analytics
- [ ] Load test report (10× baseline)

---

### Sprint 7 — Advanced RAG & Agentic Systems (Weeks 13–14)

**Objective:** Unlock the highest-value AI capabilities — precision retrieval and autonomous multi-step reasoning.

**Features:**

#### Feature 16 — Advanced Hybrid RAG + Cross-Encoder Re-ranking (7 days)
- **Service:** Retrieval & Search Service (extended)
- **What to build:**
  - Cross-encoder re-ranking using `cross-encoder/ms-marco-MiniLM-L-6-v2` (open-source via sentence-transformers).
  - Full pipeline: retrieve top-K (default 50) via RRF → re-rank with cross-encoder → pass top-N (default 10) to LLM.
  - K and N configurable per tenant via config API.
  - Async/batched re-ranking to stay within 500ms latency budget.
- **Acceptance:** MRR@10 improves ≥30% vs. vector-only baseline. Re-ranking latency < 500ms for 50 candidates.

#### Feature 17 — Agentic RAG (Tool-calling Agents) (8 days)
- **Service:** Agent Orchestration Service (new service)
- **What to build:**
  - LangGraph agent with tool registry.
  - Tools: `rag_search` (calls Retrieval Service), `web_search` (httpx), `summarize_text` (Bedrock), `decompose_query` (breaks multi-part queries into sub-queries).
  - Reasoning trace logger: per query logs `tool_name, input, output, latency` for every step.
  - Safety: max 10 steps, 30-second timeout per run. Falls back to standard RAG if agent confidence not improved.
- **Acceptance:** Multi-hop question accuracy > 80%. Total latency < 15s for ≤3 tool calls. Reasoning trace logged.

**Sprint 7 Deliverables:**
- [ ] Cross-encoder re-ranking module (sentence-transformers)
- [ ] Full retrieval pipeline: RRF → Re-rank → LLM
- [ ] Agent Orchestration Service with LangGraph
- [ ] Tool registry: rag_search, web_search, summarize_text, decompose_query
- [ ] Reasoning trace logging + agent monitoring dashboard

---

### Sprint 8 — Vectorless RAG & NASA NTRS (Weeks 15–16)

**Objective:** Achieve 100% PDF content coverage with page-level indexing and launch the NASA NTRS domain connector.

**Features:**

#### Feature 18 — Vectorless RAG: Hybrid Page Indexing (9 days)
- **Service:** PDF Processing Service (extended) + Retrieval Service (extended)
- **What to build:**
  - `pdf_page_indexer.py`: per-page pipeline — text (pdfplumber) + tables (pdfplumber → markdown) + images (pdf2image → BLIP-2 caption).
  - `image_captioner.py`: BLIP-2 or LLaVA via HuggingFace transformers (CPU quantized 4-bit default; GPU optional).
  - `table_extractor.py`: pdfplumber primary, camelot-py fallback → table-to-markdown converter.
  - Dual-index storage: page text into PostgreSQL tsvector (BM25) + embeddings into S3 Vectors.
  - Metadata per chunk: `page_number, content_type (text/table/image), source_file`.
  - 100% page coverage — no silent skips.
- **Acceptance:** Table extraction accuracy > 90%. Image captioning BLEU > 0.60. Every page produces ≥1 indexed chunk.

#### Feature 19 — Enterprise Data Source: NASA NTRS (6 days)
- **Service:** Connector Service (extended)
- **What to build:**
  - `ntrs_connector.py`: NTRS PDF upload endpoint accepting files up to 500MB.
  - Metadata extractor: auto-identifies `title, authors, report_number, publication_date, abstract, keywords` from PDF headers and first page.
  - Applies full Feature 18 page-level pipeline to every NTRS document.
  - NTRS-specific fields added to `knowledge_base_files` table.
  - Search API: filter by `report_number, author, date_range, keyword`.
- **Acceptance:** Ingestion time < 3 min for ≤200-page document. Metadata extraction accuracy > 85% on test set of 50 NTRS reports.

**Sprint 8 Deliverables:**
- [ ] `pdf_page_indexer.py` — full per-page extraction pipeline
- [ ] `image_captioner.py` — BLIP-2/LLaVA integration
- [ ] `table_extractor.py` — pdfplumber + camelot markdown converter
- [ ] `ntrs_connector.py` — NASA NTRS upload + metadata extractor
- [ ] Dual-index storage (PostgreSQL BM25 + S3 Vectors) at page level
- [ ] NTRS search API with metadata filters

---

## 5. Master Timeline

```
WEEK  │ 1  │ 2  │ 3  │ 4  │ 5  │ 6  │ 7  │ 8  │ 9  │ 10 │ 11 │ 12 │ 13 │ 14 │ 15 │ 16 │
──────┼────┴────┼────┴────┼────┴────┼────┴────┼────┴────┼────┴────┼────┴────┼────┴────┤
      │ SPRINT 1│ SPRINT 2│ SPRINT 3│ SPRINT 4│ SPRINT 5│ SPRINT 6│ SPRINT 7│ SPRINT 8│
      │Quick Win│Security │Quality &│   UX    │Enterprise│Scale &  │Adv. RAG │Vectorless│
      │         │& Observ.│ Search  │         │Integratn │Polish   │& Agents │& NTRS   │
──────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
F1    │████████ │         │         │         │         │         │         │         │
F2    │████████ │         │         │         │         │         │         │         │
F3    │████████ │         │         │         │         │         │         │         │
F4    │         │████████ │         │         │         │         │         │         │
F5    │         │████████ │         │         │         │         │         │         │
F6    │         │████████ │         │         │         │         │         │         │
F7    │         │         │████████ │         │         │         │         │         │
F8    │         │         │████████ │         │         │         │         │         │
F9    │         │         │████████ │         │         │         │         │         │
F10   │         │         │         │████████ │         │         │         │         │
F11   │         │         │         │████████ │         │         │         │         │
F12   │         │         │         │████████ │         │         │         │         │
F13   │         │         │         │         │████████ │         │         │         │
F14   │         │         │         │         │████████ │         │         │         │
F15   │         │         │         │         │         │████████ │         │         │
F16   │         │         │         │         │         │         │████████ │         │
F17   │         │         │         │         │         │         │████████ │         │
F18   │         │         │         │         │         │         │         │████████ │
F19   │         │         │         │         │         │         │         │████████ │
──────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
DEMO  │       W2│       W4│       W6│       W8│      W10│      W12│      W14│      W16│
```

### Key Milestones

| Milestone | Week | Description |
|---|---|---|
| 🚀 MVP Enhancements Live | Week 2 | Citations, fast indexing, better memory |
| 🔒 Enterprise Security Live | Week 4 | RBAC, monitoring, cost tracking |
| 🔍 Hybrid Search Live | Week 6 | BM25 + Vector + RRF, PDF tables/images |
| 🌍 Global Ready | Week 8 | Multi-language, feedback, prompt management |
| 🏢 Enterprise Integrations Live | Week 10 | SharePoint, GDrive, Confluence, GDPR |
| ⚡ Scale-Ready Platform | Week 12 | Redis cache, auto-scaling, load balanced |
| 🤖 Advanced AI Live | Week 14 | Cross-encoder re-ranking + Agentic RAG |
| 🛸 Full PDF Intelligence + NASA NTRS | Week 16 | 100% PDF coverage, NTRS domain connector |

---

## 6. Dependency Map

```
Sprint 1 (F1, F2, F3)
   └──► Sprint 2 (F4 RBAC needs F1 foundation)
            └──► Sprint 4 (F10 Feedback needs F5 Observability)
Sprint 3 (F7, F8, F9)
   └──► Sprint 5 (F13 Multi-source needs F9 Doc Processing)
   └──► Sprint 7 (F16 Advanced RAG needs F8 Hybrid Search)
Sprint 6 (F15 Scale)
   └──► Sprint 7 (F17 Agentic needs Sprint 6 scalable infra)
Sprint 7 (F16, F17)
   └──► Sprint 8 (F18 Vectorless RAG needs F16 Advanced RAG + F9)
Sprint 8 F18
   └──► Sprint 8 F19 (NASA NTRS needs F18 page-level pipeline)
```

| Blocker Service | Unlocks |
|---|---|
| Auth & RBAC Service (Sprint 2) | All protected endpoints in every subsequent service |
| PDF Processing Service (Sprint 3) | Connector Service sync (Sprint 5), Vectorless RAG (Sprint 8) |
| Retrieval & Search Service — Hybrid (Sprint 3) | Cross-Encoder Re-ranking (Sprint 7) |
| Scalable Architecture (Sprint 6) | Agent Orchestration Service (Sprint 7) safe to deploy at load |
| Vectorless RAG pipeline (Sprint 8 F18) | NASA NTRS Connector (Sprint 8 F19) |

---

## 7. Technology Stack per Service

| Service | Language | Key Libraries / AWS Services |
|---|---|---|
| API Gateway / BFF | Python (FastAPI) | AWS ALB, JWT middleware |
| Auth & RBAC Service | Python (FastAPI) | PostgreSQL, Argon2, JWT |
| Chat & Conversation Service | Python (FastAPI) | AWS Bedrock, Redis, PostgreSQL |
| Document Ingestion Service | Python (FastAPI) + Lambda | SQS, SNS, S3 |
| PDF Processing Service | Python (Lambda / ECS) | pdfplumber, pdf2image, poppler, BLIP-2/LLaVA (HuggingFace transformers), camelot-py |
| Retrieval & Search Service | Python (FastAPI) | AWS S3 Vectors, PostgreSQL tsvector, sentence-transformers cross-encoder, RRF fusion |
| Agent Orchestration Service | Python | LangGraph, httpx (web search), AWS Bedrock |
| Observability & Cost Service | Python | CloudWatch, PostgreSQL, async SQS consumer |
| Feedback Service | Python (FastAPI) | PostgreSQL |
| Prompt Management Service | Python (FastAPI) | PostgreSQL |
| Translation Service | Python (FastAPI) | AWS Translate, Amazon Comprehend, Redis |
| Connector Service | Python | OAuth2 (MSAL, Google OAuth), httpx, SQS scheduler, NASA NTRS metadata extractor |
| Enterprise Security & Compliance Service | Python | AWS KMS, PostgreSQL (append-only audit), retention job scheduler |
| Shared Infrastructure | — | PostgreSQL (RDS + read replicas), Redis (ElastiCache), S3 Vectors, AWS Bedrock, SQS, Lambda, CloudWatch, ALB, ECS Fargate |

---

## 8. Risk Register & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AWS Bedrock rate limits hit under load | Medium | High | SQS queuing + exponential backoff; request batching |
| BLIP-2/LLaVA memory too high for Lambda | Medium | Medium | Use CPU-quantized 4-bit models; ECS Fargate with configurable memory; AWS Textract as future upgrade |
| LangGraph agent infinite loop / runaway cost | Low | High | Hard limit: 10 steps max, 30-second timeout per agent run |
| Cross-encoder re-ranking exceeds 500ms budget | Medium | Medium | Batch processing; async pipeline; model quantization |
| OAuth2 connector token expiry / revocation | Medium | Medium | Token refresh logic + re-auth alert to admin |
| GDPR DSAR misses 72-hour SLA | Low | High | Automated deletion job with SLA monitoring alert |
| PDF extraction fails on complex layouts | Medium | Medium | Graceful fallback to plain-text extraction; error logged to Observability Service |
| Redis cache invalidation inconsistency | Low | Medium | TTL-based expiry + explicit invalidation on document update events |
| Sync connector data duplication | Medium | Low | Deduplication via content hash before ingestion |
| Translation costs spike with high query volume | Medium | Medium | Redis translation cache for repeated phrases; per-tenant usage limits |

---

## 9. Success Metrics & KPIs

### Performance

| KPI | Target |
|---|---|
| p95 standard RAG query latency | < 2 seconds |
| p95 agentic RAG query latency | < 15 seconds |
| p95 document indexing latency | < 120 seconds |
| Redis cache hit rate | > 70% |
| Cross-encoder re-ranking latency | < 500ms for 50 candidates |

### Quality

| KPI | Target |
|---|---|
| Hallucination rate | < 5% |
| Hybrid search relevance improvement | ≥ +25% vs. vector-only baseline |
| Cross-encoder re-ranking MRR@10 improvement | ≥ +30% vs. vector-only baseline |
| Multi-hop agent accuracy | > 80% |
| PDF table extraction accuracy | > 90% |
| Image captioning BLEU score | > 0.60 |
| NTRS metadata extraction accuracy | > 85% on 50-report test set |
| Translation accuracy | > 90% on standard benchmark |

### Security & Compliance

| KPI | Target |
|---|---|
| Unauthorized access incidents | 0 |
| Audit trail coverage | 100% of data access events |
| GDPR DSAR completion time | < 72 hours |
| Encryption coverage | 100% at rest (AES-256) + in transit (TLS 1.2+) |

### Scale

| KPI | Target |
|---|---|
| Concurrent users supported | 10,000 |
| Tenants supported | 100 |
| Documents processable (with images/tables) | 1,000,000 |
| Traffic spike handling | 10× baseline with no degradation |
| Platform uptime SLA | 99.9% |

### Cost

| KPI | Target |
|---|---|
| Bedrock cost attribution | 100% per tenant |
| Cost reduction through optimization insights | −20% |

---

*Document Version: 1.0 | Created: May 2026 | Last Updated: May 2026*
*Project: RAG365 Enterprise Platform | Architecture: Microservice-based, AWS Cloud-native*