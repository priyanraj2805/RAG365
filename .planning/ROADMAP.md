# ROADMAP: RAG365 Enterprise Transformation

## Summary
- **Total phases:** 8
- **Execution model:** sequential phases with controlled cutovers and rollback gates
- **When:** complete each phase in order before moving to the next (Phase 1 -> Phase 8)

## Flow Overview (What happens and when)
1. Foundation and safety controls first
2. Security and tenant control hardening
3. Async ingestion/indexing extraction
4. Retrieval extraction and contract stabilization
5. Chat orchestration extraction
6. Governance/compliance platform capabilities
7. Enterprise connectors and operational controls
8. Advanced AI features and scale hardening

---

## Phase 1: Platform Control Plane
**When:** Start here  
**Goal:** Build a safe migration envelope before service extraction.

### Deliverables
- API gateway route control for legacy + new services
- Edge throttling/rate limiting
- Traffic split and rollback switches

### Exit Criteria
- Gateway controls all north-south traffic
- Cutovers are reversible without client changes

---

## Phase 2: Identity, RBAC, and Secrets Baseline
**When:** After Phase 1  
**Goal:** Establish enterprise security foundations.

### Deliverables
- Central auth/rbac boundary for critical endpoints
- Secrets management and hardcoded-secret removal
- Standard authorization checks in service boundaries

### Exit Criteria
- No critical endpoints bypass authz
- Secrets are not embedded in source code

---

## Phase 3: Ingestion and Indexing Carve-Out
**When:** After Phase 2  
**Goal:** Extract the async domain with lowest synchronous coupling.

### Deliverables
- Ingestion service boundary and lifecycle states
- Tenant-partitioned queue strategy for indexing throughput
- Worker hardening for retries/idempotency/status reporting

### Exit Criteria
- Indexing scales across tenants without global FIFO bottleneck
- Ingestion status is consistently observable end-to-end

---

## Phase 4: Retrieval Service Extraction
**When:** After Phase 3  
**Goal:** Isolate retrieval/search as an independent service.

### Deliverables
- Retrieval API contracts (compatible with existing callers)
- Contract checks for monolith-to-service parity
- Cutover toggles for safe route migration

### Exit Criteria
- Retrieval traffic can shift independently with rollback
- Latency/relevance remain within accepted bounds

---

## Phase 5: Chat Orchestration Service Extraction
**When:** After Phase 4  
**Goal:** Decouple chat orchestration from monolith runtime concerns.

### Deliverables
- Chat orchestration boundary and service APIs
- Prompt assembly and response pipeline isolation
- Sync-path optimization with async offload for non-critical work

### Exit Criteria
- Chat deploys independently from retrieval/legacy backend
- Stable user behavior under canary rollout

---

## Phase 6: Observability and SLO Enforcement
**When:** Runs strongly from here onward (after core split)  
**Goal:** Make operations measurable and production-grade.

### Deliverables
- OpenTelemetry tracing across extracted services
- Structured logs and centralized metrics
- SLO dashboards and alerting for latency/error budgets

### Exit Criteria
- Service health and incidents are traceable end-to-end
- Releases are gated by SLO status

---

## Phase 7: Governance, Compliance, and Connectors
**When:** After Phase 6 baseline is active  
**Goal:** Add enterprise onboarding capabilities.

### Deliverables
- Immutable audit event pipeline
- Retention/deletion workflow foundation
- Connector framework with incremental sync visibility
- Per-tenant operational and cost governance surfaces

### Exit Criteria
- Governance controls are demonstrable for enterprise reviews
- Connector lifecycle is observable and supportable

---

## Phase 8: Advanced AI and Scale Hardening
**When:** Final phase after stable enterprise core  
**Goal:** Introduce advanced capabilities on top of stable service boundaries.

### Deliverables
- Advanced retrieval/reranking enhancements
- Optional agentic orchestration with guardrails
- Capacity and resilience hardening for high concurrency

### Exit Criteria
- Core SLOs remain stable under higher load
- Advanced features do not degrade reliability or governance
