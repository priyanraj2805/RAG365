# Feature Landscape

**Domain:** Monolith-to-microservices enterprise migration (RAG platform)  
**Researched:** 2026-05-14

## Table Stakes

Features enterprise buyers and operators expect in a serious migration.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Strangler routing (gateway routes old/new backends) | Zero-downtime incremental migration | Med | Start with read paths and non-critical endpoints. |
| Service contracts + compatibility tests | Prevent integration regressions | Med | Required because current repo lacks CI-grade tests. |
| Identity boundary (AuthN/AuthZ service + RBAC) | Enterprise security baseline | High | Must be first extracted control plane service. |
| Observability baseline (traces + logs + SLOs) | Debugging across services is impossible otherwise | Med | Deploy before first real traffic split. |
| Event-driven ingestion/indexing workflow | Avoid chat path coupling and tail latency | Med | Existing SQS/Lambda path is strongest first carve-out candidate. |
| Centralized secrets + key rotation + audit trail | Compliance and incident response | Med | Move hardcoded secrets immediately. |
| Edge throttling/rate limits | Cost and abuse containment | Low | API Gateway native throttling should gate all public endpoints. |

## Differentiators

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Tenant-isolated SLO and cost budgets | Enterprise-ready multi-tenant governance | Med | Per-tenant p95, error budget, Bedrock spend limits. |
| Progressive service extraction scorecard | Executive and delivery visibility | Low | Track each bounded context by % traffic moved + rollback readiness. |
| Policy-as-code guardrails for migrations | Safer releases at scale | Med | Enforce non-negotiables (auth, tracing, rate limits) in CI/CD. |
| Dual-run validation (shadow traffic) | Lower migration risk for retrieval/chat services | High | Compare monolith/new service responses before cutover. |

## Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Big-bang rewrite of all services | High failure probability with current test/quality gaps | Incremental strangler migration with reversible route cutovers |
| DB-per-service from day 1 for all domains | Slows delivery and increases operational risk immediately | Start schema-per-service; split high-scale domains later |
| gRPC-everywhere mandate | Premature complexity | Use REST+events first; add gRPC only for proven hotspots |
| Simultaneous frontend and backend re-platforming | Multiplies blast radius | Keep Next.js UI stable; transform backend first |

## Feature Dependencies

```text
Secrets management + RBAC + tracing baseline → safe service extraction
Gateway strangler routing → incremental traffic cutovers
Contract testing → reliable independent deployments
Async ingestion boundary → retrieval/chat boundary split
Observability SLOs → confident monolith endpoint retirement
```

## MVP Recommendation

Prioritize:
1. Gateway strangler routing + edge throttling
2. Auth/RBAC control plane extraction
3. Observability baseline (OpenTelemetry + SLO dashboards)

Then: ingestion/indexing service carve-out as first high-value domain split.

Defer: full agentic orchestration decomposition until core chat/retrieval boundaries are stable and observable.

## Sources

- AWS Strangler Fig guidance (HIGH): https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html
- API Gateway throttling docs (HIGH): https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-throttling.html
- FastAPI modular app patterns (HIGH): https://fastapi.tiangolo.com/tutorial/bigger-applications/
- Internal codebase concerns/architecture maps (HIGH): `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/TESTING.md`
