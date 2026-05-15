# Architecture Patterns

**Domain:** Enterprise RAG platform microservices migration  
**Researched:** 2026-05-14

## Recommended Architecture

Use a **Strangler-Fig architecture**: API Gateway fronts both monolith and new services; traffic shifts route-by-route behind stable external contracts.

```text
Clients
  -> API Gateway (auth, throttling, routing rules)
    -> Monolith (legacy routes not yet extracted)
    -> Auth/RBAC Service
    -> Chat Service
    -> Retrieval Service
    -> Ingestion Service -> SQS -> Index Workers/PDF Processor
    -> Observability/Cost Service
Shared infra: RDS(Postgres), S3/S3 Vectors, Redis, CloudWatch/X-Ray, Secrets Manager
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| API Gateway/BFF | Edge auth checks, throttling, strangler routing, versioning | All internal services + legacy monolith |
| Auth & RBAC | Identity, token validation, role policy decisions | Gateway, all services via auth middleware |
| Chat Orchestrator | Session flow, prompt assembly, response streaming | Retrieval, Prompt service, Translation |
| Retrieval/Search | Hybrid retrieval + ranking | Chat, Ingestion, Vector/SQL stores |
| Ingestion Pipeline | File intake, status lifecycle, indexing orchestration | SQS/SNS, PDF Processor, Retrieval |
| Compliance/Audit | Immutable audit events, retention/DSAR workflows | All services via event ingestion |
| Observability/Cost | Traces/metrics/logs, spend analytics, SLO alerts | All services + CloudWatch/X-Ray |

### Data Flow

1. Request enters Gateway; route policy decides monolith vs extracted service.
2. Auth token validated by Auth service (or signed claims cache).
3. Chat service calls Retrieval synchronously; long-running work always async via queue.
4. Every write emits event (`document_indexed`, `role_changed`, `feedback_received`) for audit/analytics.
5. Traces propagated end-to-end with shared trace IDs.

## Patterns to Follow

### Pattern 1: Strangler Route Extraction
**What:** Move one endpoint group at a time behind gateway routing rules.  
**When:** Any bounded context with stable API contract.
**Example:**
```typescript
// gateway rule pseudocode
if (path.startsWith("/v1/auth")) route("auth-service")
else if (path.startsWith("/v1/documents")) route("ingestion-service")
else route("legacy-monolith")
```

### Pattern 2: Branch by Abstraction
**What:** Keep existing endpoint contract; swap internal implementation from monolith module to service client.  
**When:** High-traffic routes where frontend/API consumers must not change first.
**Example:**
```python
def ask_chat(request):
    if feature_flags.use_chat_service:
        return chat_service_client.ask(request)
    return legacy_monolith_chat(request)
```

### Pattern 3: Transactional Outbox for Cross-Service Events
**What:** Persist domain change + event in same DB transaction, then publish asynchronously.  
**When:** Role changes, ingestion state, billing events.
**Example:**
```typescript
BEGIN;
UPDATE documents SET status='INDEXING' WHERE id=:id;
INSERT INTO outbox(topic, payload) VALUES ('document.status.changed', :payload);
COMMIT;
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Distributed Monolith
**What:** Split deployables but keep shared DB tables and tight runtime coupling.  
**Why bad:** No true isolation, blocked deployments, cascading failures.  
**Instead:** Service-owned schemas, async boundaries, contract tests.

### Anti-Pattern 2: Observability-Later Migration
**What:** Extract services without traces/metrics/log standards first.  
**Why bad:** Incident triage and rollback decisions become guesswork.  
**Instead:** OTel baseline + SLO dashboards before traffic cutover.

### Anti-Pattern 3: FIFO Serialization Across Tenants
**What:** Single message group for all tenant indexing jobs.  
**Why bad:** Throughput collapse under multi-tenant load.  
**Instead:** Per-tenant message group IDs or standard queues where ordering is unnecessary.

## Scalability Considerations

| Concern | At 100 users | At 10K users | At 1M users |
|---------|--------------|--------------|-------------|
| API throughput | Single service instances OK | ECS autoscaling + gateway throttling required | Multi-region active/active likely needed |
| Indexing concurrency | Shared queue acceptable | Tenant-partitioned queue consumers required | Dedicated ingestion clusters + workload classes |
| DB load | Single writer OK | Read replicas + query isolation mandatory | Domain database split + archival strategy |
| Failures | Manual rollback possible | Automated canary rollback needed | Fault injection + regional failover required |
| Security/compliance | Basic RBAC | Full audit + DSAR automation | Formal compliance program and key segregation |

## Sources

- AWS Strangler Fig pattern (HIGH): https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html
- ECS service autoscaling (HIGH): https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html
- SQS FIFO concurrency behavior (HIGH): https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/fifo-queue-lambda-behavior.html
- FastAPI modular routers (HIGH): https://fastapi.tiangolo.com/tutorial/bigger-applications/
- API Gateway throttling (HIGH): https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-throttling.html
- OpenTelemetry Python + Context7 snippets (HIGH): https://opentelemetry.io/docs/languages/python/
- Internal architecture maps (HIGH): `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONCERNS.md`
