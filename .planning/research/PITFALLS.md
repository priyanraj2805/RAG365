# Domain Pitfalls

**Domain:** Monolith to enterprise microservices migration (RAG365)  
**Researched:** 2026-05-14

## Critical Pitfalls

### Pitfall 1: Extracting Services Without Contract Tests
**What goes wrong:** New services drift from monolith behavior and silently break clients.  
**Why it happens:** Current repo lacks CI-grade automated tests and stable API contract checks.  
**Consequences:** Frequent regressions, rollback churn, stalled migration.  
**Prevention:** Define OpenAPI contracts, add consumer/provider contract tests before route cutover.  
**Detection:** Increased 4xx/5xx after cutovers, high hotfix rate, inconsistent payloads.

### Pitfall 2: Shared Database Coupling Forever
**What goes wrong:** “Microservices” still coupled by shared tables and direct cross-service writes.  
**Why it happens:** Fast migration pressure and fear of data duplication.  
**Consequences:** Distributed monolith, blocked deployments, impossible independent scaling.  
**Prevention:** Service-owned schemas now; staged DB splits later for high-scale domains.  
**Detection:** Cross-service SQL joins and multi-team migration conflicts.

### Pitfall 3: Security Deferred Until Late Phases
**What goes wrong:** Services launch with inconsistent authz, leaked secrets, and weak auditability.  
**Why it happens:** Feature pressure outruns platform hardening.  
**Consequences:** Compliance failures and production incidents.  
**Prevention:** Extract Auth/RBAC and secrets management first; enforce policy checks in CI/CD.  
**Detection:** Anonymous/weakly-protected endpoints, secrets in code, missing audit events.

## Moderate Pitfalls

### Pitfall 1: Queue Ordering Misconfiguration
**What goes wrong:** FIFO queue design serializes tenant workloads and indexing stalls.  
**Prevention:** Use per-tenant message groups (or standard queues if strict ordering is unnecessary).

### Pitfall 2: Synchronous Cross-Service Chattiness
**What goes wrong:** Chat latency spikes due to many blocking internal calls.  
**Prevention:** Keep critical sync path short; offload non-critical steps to async events.

### Pitfall 3: Incomplete Observability Context
**What goes wrong:** Logs exist but cannot correlate across services.  
**Prevention:** Propagate trace IDs; standardize OTel instrumentation, log schema, and SLO dashboards.

## Minor Pitfalls

### Pitfall 1: Premature gRPC Adoption
**What goes wrong:** Added complexity without measurable performance gain.  
**Prevention:** Start REST+events; introduce gRPC only for demonstrated hotspots.

### Pitfall 2: Frontend Coupled to Internal Service Topology
**What goes wrong:** UI breaks when backend routes move.  
**Prevention:** Keep stable BFF/gateway contract and avoid exposing internal topology.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Foundation (Gateway/Auth/Obs) | Treating it as “overhead” and skipping | Make foundation exit criteria mandatory before extraction |
| First carve-out (Ingestion) | Queue and status model mismatch with legacy data | Run dual-write/dual-read validation window |
| Core split (Chat/Retrieval) | Latency regressions from call chains | SLO-based canary + rollback automation |
| Compliance rollout | Audit events added inconsistently | Shared event schema + required middleware |
| Scale phase | Autoscaling without load profile | k6/Locust workload replay + capacity guards |

## Sources

- AWS Strangler Fig pattern (HIGH): https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html
- SQS FIFO + Lambda behavior (HIGH): https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/fifo-queue-lambda-behavior.html
- API Gateway throttling (HIGH): https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-throttling.html
- OpenTelemetry Python (HIGH): https://opentelemetry.io/docs/languages/python/
- Internal risks and gaps (HIGH): `.planning/codebase/CONCERNS.md`, `.planning/codebase/TESTING.md`
