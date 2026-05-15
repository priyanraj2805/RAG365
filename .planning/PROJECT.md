# PROJECT: RAG365 Enterprise Transformation

## Problem
RAG365 currently operates as a monolithic FastAPI + Next.js system with strong tenant-isolated retrieval foundations but significant enterprise readiness gaps (modularity, security hardening, observability, CI-grade testing, and safe scale patterns). The goal is to evolve it into an enterprise-grade microservices platform without a risky rewrite.

## Product Direction
Transform the existing platform using a **Strangler Fig migration strategy**:
- Keep the current product operational
- Introduce an API gateway control plane
- Extract bounded services incrementally
- Route traffic gradually with rollback safety

## Primary Goals
1. Deliver trustworthy enterprise AI responses with citations, isolation, and policy controls.
2. Achieve safe multi-tenant scale with measurable SLOs and predictable cost controls.
3. Enable independent service delivery by decomposing the monolith into domain-owned services.
4. Reach enterprise compliance baseline (RBAC, auditability, retention/DSAR workflows).

## Users and Stakeholders
- Platform Owner / Head of AI
- Security & Compliance Lead
- Knowledge Operations Manager
- Business Unit Admin
- End User (analyst/support/engineering roles)

## Scope (Initial Milestone)
In scope:
- Control plane foundations (gateway, auth/rbac, secrets, tracing/metrics/logs, throttling)
- Ingestion/indexing carve-out and queue partitioning by tenant
- Retrieval and chat boundary split with compatibility contracts
- Governance and connector readiness for enterprise onboarding

Out of scope (initially):
- Big-bang rewrite
- Simultaneous frontend re-platform
- Premature gRPC-first architecture

## Technical Baseline
- Existing: FastAPI backend, Next.js 15 frontend, PostgreSQL, AWS S3/S3 Vectors, SQS/Lambda, Bedrock models.
- Target migration platform: API Gateway + ECS Fargate services, OpenTelemetry baseline, Redis, outbox/event patterns, staged schema ownership.

## Risks to Manage
- Service extraction before contract tests and observability
- Security deferral (hardcoded secrets, inconsistent auth practices)
- Throughput bottlenecks from FIFO serialization across tenants
- Distributed monolith risk from permanent shared-DB coupling

## Success Signals
- Controlled route-by-route traffic migration with rollback readiness
- Per-service SLO dashboards and traceability in production
- Zero cross-tenant leakage incidents
- Enterprise control features (RBAC/audit/retention) available for buyer reviews

