# Research Summary: RAG365 Enterprise Microservices Transformation

**Domain:** Enterprise RAG platform migration (monolith → microservices)  
**Researched:** 2026-05-14  
**Overall confidence:** HIGH

## Executive Summary

RAG365 should not do a full rewrite. The safest and fastest path is an incremental **Strangler Fig** migration behind a single gateway, with controlled traffic cutovers and fast rollback. This aligns with AWS prescriptive guidance and matches current reality: a monolithic FastAPI backend, partial async indexing decoupling, and limited automated test coverage.

The first milestone is platform safety, not feature volume: extract/standardize edge routing, Auth/RBAC, observability, and secrets management before splitting core chat/retrieval logic. Without this control plane, service extraction will amplify current quality and security risks.

Service boundaries should follow domain volatility and coupling: start with Document Ingestion (already partially asynchronous), then isolate Retrieval, then Chat orchestration, then supporting services (feedback/prompt/translation), and finally advanced agentic and specialized connector workloads.

Roadmap sequencing should be dependency-driven: governance and telemetry first, asynchronous boundaries second, high-traffic synchronous boundaries third, enterprise integrations fourth, and scale polish continuously validated with SLO-based canaries and rollback gates.

## Key Findings

**Stack:** Keep Python/FastAPI on ECS Fargate, add API Gateway strangler routing, OpenTelemetry baseline, Redis, and event-driven service communication.  
**Architecture:** Strangler + branch-by-abstraction + outbox events is the recommended decomposition pattern.  
**Critical pitfall:** Extracting services before contract tests/observability will cause unstable cutovers and rework.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Platform Control Plane First** - create safe migration envelope
   - Addresses: gateway routing, RBAC, secrets, throttling, tracing/SLOs
   - Avoids: insecure and opaque service sprawl

2. **Asynchronous Domain Carve-Out** - extract ingestion/indexing pipeline
   - Addresses: queue partitioning, status lifecycle, worker scalability
   - Avoids: sync latency coupling and FIFO throughput bottlenecks

3. **Core Runtime Split** - separate Retrieval then Chat orchestration
   - Addresses: independent scaling, quality improvements, clear ownership
   - Avoids: distributed monolith through shared runtime logic

4. **Enterprise Governance + Integrations** - compliance/audit/connectors
   - Addresses: auditability, DSAR/retention, enterprise source onboarding
   - Avoids: late compliance surprises

5. **Advanced AI + Scale Hardening** - agentic workflows, re-ranking, high-scale reliability
   - Addresses: differentiation features after stable core decomposition
   - Avoids: advanced features built on unstable foundations

**Phase ordering rationale:**
- Security + observability are prerequisites for safe cutovers.
- Async extraction is lower coupling and de-risks first migration steps.
- Core chat/retrieval split depends on strong contracts and telemetry.
- Compliance and scale phases require service ownership boundaries already in place.

**Research flags for phases:**
- Phase 3: Needs deeper latency-budget and contract-test research for chat/retrieval sync path.
- Phase 4: Needs legal/compliance validation for DSAR and retention workflows.
- Phase 1-2: Standard patterns; lower research uncertainty.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Backed by official FastAPI/AWS/OpenTelemetry docs + existing codebase constraints |
| Features | MEDIUM | Migration feature priorities are evidence-based but org/team capacity assumptions remain |
| Architecture | HIGH | Strong pattern fit with AWS strangler guidance + current system topology |
| Pitfalls | HIGH | Directly confirmed by existing codebase concerns and testing/security gaps |

## Gaps to Address

- Define exact service-level SLO budgets (chat/retrieval/ingestion) before Phase 3 cutovers.
- Choose final event backbone split (SNS+SQS vs EventBridge+SQS) with cost/load modeling.
- Decide timeline for schema-per-service to DB-per-service transitions per domain.
- Validate compliance implementation details with legal/security stakeholders.
