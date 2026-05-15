# Technology Stack

**Project:** RAG365 Enterprise Microservices Migration  
**Researched:** 2026-05-14

## Recommended Stack

### Core Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| FastAPI + APIRouter modular services | FastAPI 0.12x line | Service APIs (Auth, Chat, Retrieval, Connectors, etc.) | Keep Python continuity with current codebase; FastAPI officially supports modular router composition for bounded contexts and staged extraction. |
| Next.js Admin BFF (existing) | Next.js 15.x | Admin UI orchestration and API consumption | Preserve frontend velocity; minimize concurrent frontend rewrite risk during backend decomposition. |

### Database
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| PostgreSQL (RDS) with schema-per-service initially | PostgreSQL 15+ | Transactional data during migration | Best transitional compromise: fast carve-out without immediate DB explosion; enables later DB-per-service split. |
| S3 + S3 Vectors | AWS managed | Knowledge/document blobs + vector retrieval | Already operational in production path; avoid costly vector migration mid-transform. |
| Redis (ElastiCache) | Redis 7+ | Hot session/cache/idempotency keys/rate-limit counters | Needed for latency and abuse control; required before high-concurrency rollout. |

### Infrastructure
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| API Gateway (HTTP API) + ALB | AWS managed | Edge throttling, auth routing, north-south ingress | Gives immediate rate controls and controlled strangler routing from monolith to new services. |
| ECS Fargate + Service Auto Scaling | AWS managed | Deploy and scale microservices | Lowest ops burden vs EKS for this team profile; official autoscaling support with target tracking. |
| SQS + SNS/EventBridge | AWS managed | Async workflows + service events | Decouples ingestion/indexing and prevents sync tail-latency coupling. |
| OpenTelemetry + CloudWatch/X-Ray | OTel stable + AWS managed | Distributed traces, metrics, logs | Critical for migration safety and cross-service debugging. |

### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, OTLP exporter | current stable | Trace/metric/log correlation | Mandatory in every extracted service before production traffic cutover. |
| `httpx` + `tenacity` | current stable | Internal service calls + resilient retries | Use for bounded retries, not for long-running jobs (push those to SQS). |
| `alembic` | current stable | Controlled schema evolution | Required for schema-per-service ownership and rollback-safe migrations. |
| `pydantic` contracts + OpenAPI | v2 line | API schema contracts | Use for consumer-driven contract tests and gateway validation. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Orchestration | ECS Fargate | EKS | EKS adds platform complexity too early for a migration already carrying domain risk. |
| Migration style | Strangler Fig (incremental) | Big-bang rewrite | Current monolith instability + missing tests makes big-bang failure-prone. |
| Data strategy | Schema-per-service -> DB-per-service evolution | Shared DB forever | Shared DB preserves coupling and creates distributed monolith behavior. |
| Service comms | REST + async events | gRPC-first everywhere | Premature optimization; gRPC only where measured latency/throughput requires it. |

## Installation

```bash
# Core backend service baseline
pip install fastapi uvicorn sqlalchemy alembic pydantic httpx tenacity redis boto3

# Observability baseline
pip install opentelemetry-sdk opentelemetry-exporter-otlp \
  opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-logging
```

## Sources

- FastAPI docs (APIRouter modularization): https://fastapi.tiangolo.com/tutorial/bigger-applications/ (HIGH)
- Context7 `/fastapi/fastapi` include_router and router dependency patterns (HIGH)
- AWS Prescriptive Guidance, Strangler Fig pattern: https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html (HIGH)
- Amazon ECS Service Auto Scaling: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html (HIGH)
- API Gateway HTTP API throttling: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-throttling.html (HIGH)
- SQS FIFO + Lambda concurrency behavior: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/fifo-queue-lambda-behavior.html (HIGH)
- OpenTelemetry Python docs: https://opentelemetry.io/docs/languages/python/ and Context7 `/open-telemetry/opentelemetry-python` (HIGH)
