# Testing Patterns

**Analysis Date:** 2026-05-14

## Test Framework

**Runner:**
- Python/TS unit-test framework config is not detected (`pytest.ini`, `pyproject.toml`, `jest.config.*`, `vitest.config.*` not found).
- Backend tests are executable Python scripts run directly (for example `ChatBotBE/backend/test_automatic_indexing.py`, `ChatBotBE/backend/test_api_retrieval.py`).
- Frontend test framework is not configured in `ChatBotFE/.../package.json` scripts.

**Assertion Library:**
- Not detected as a standardized library. Validation is done with manual conditionals and pass/fail prints in scripts.

**Run Commands:**
```bash
python ChatBotBE/backend/test_automatic_indexing.py <tenant_id>   # Scripted backend validation
python ChatBotBE/backend/test_api_retrieval.py                    # API retrieval smoke checks
npm --prefix ChatBotFE/RAGAdminFE/RAGAdminFE/frontend/rag-admin-frontend run lint  # Frontend lint gate
```

## Test File Organization

**Location:**
- Backend test scripts are co-located in `ChatBotBE/backend/` (for example `test_metadata_fix.py`, `test_retrieval_on_server.py`).
- Frontend test files (`*.test.*` / `*.spec.*`) are not detected under `ChatBotFE/.../src`.

**Naming:**
- Backend uses `test_*.py` naming convention (`ChatBotBE/backend/test_api_retrieval.py`, `ChatBotBE/backend/test_lambda_tenant_11.py`).
- Shell-based test helpers also exist (`ChatBotBE/backend/test_lambda_tenant_11.sh`).

**Structure:**
```text
ChatBotBE/backend/
├── test_api_retrieval.py
├── test_automatic_indexing.py
├── test_direct_s3_vectors.py
├── test_lambda_tenant_11.py
├── test_metadata_fix.py
└── test_retrieval_on_server.py
```

## Test Structure

**Suite Organization:**
```python
# ChatBotBE/backend/test_api_retrieval.py
for i, query in enumerate(test_queries, 1):
    response = requests.post(...)
    if response.status_code == 200:
        ...
        if has_no_info:
            print("❌ FAIL ...")
        else:
            print("✅ PASS ...")
```

**Patterns:**
- Setup pattern: Inline constants for tenant IDs/endpoints/regions at file top (`test_metadata_fix.py:12-17`, `test_retrieval_on_server.py:10-15`).
- Teardown pattern: Not standardized; scripts usually end after logging summary.
- Assertion pattern: `if/else` checks with `print` and exit codes (`test_automatic_indexing.py:131-140`, `test_api_retrieval.py:27-53`).

## Mocking

**Framework:** Not detected

**Patterns:**
```python
# Current pattern in repository: real service calls, no mocks
s3vectors_client = boto3.client('s3vectors', region_name=S3_VECTORS_REGION)
response = requests.post(f"{API_ENDPOINT}/rag/ask/{TENANT_ID}", json={...})
```

**What to Mock:**
- No repository-standard mocking guidance is present.

**What NOT to Mock:**
- Current scripts intentionally avoid mocking and hit live AWS/API systems.

## Fixtures and Factories

**Test Data:**
```python
# ChatBotBE/backend/test_api_retrieval.py
test_queries = [
    "Tell me about the projects",
    "What skills are mentioned?",
    "What is the experience?"
]
```

**Location:**
- Inline in each test script; shared fixture/factory modules are not detected.

## Coverage

**Requirements:** None enforced

**View Coverage:**
```bash
Not detected
```

## Test Types

**Unit Tests:**
- Not detected as isolated unit tests with local-only dependencies.

**Integration Tests:**
- Primary testing style: end-to-end integration scripts against running API and AWS services (`test_metadata_fix.py`, `test_retrieval_on_server.py`, `test_automatic_indexing.py`).

**E2E Tests:**
- Browser E2E framework (Playwright/Cypress) is not detected in frontend config.

## Common Patterns

**Async Testing:**
```python
# ChatBotBE/backend/test_metadata_fix.py
print("⏳ Waiting 30 seconds for Lambda to process...")
time.sleep(30)
```

**Error Testing:**
```python
try:
    response = requests.post(...)
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
```

## CI Quality Gates

- CI pipeline configuration is not detected (`.github/workflows/*`, GitLab CI YAML, and other CI files not found).
- Frontend quality gate available: `npm run lint` (`ChatBotFE/.../package.json:9`), but lint can be skipped during production build via `ignoreDuringBuilds` (`ChatBotFE/.../next.config.ts:4-6`).
- Backend has no detected automated gate for lint, type-check, or test execution.

## Quality Risks in Current Testing Strategy

- Tests depend on live infrastructure (AWS S3/SQS/Bedrock + running API), creating non-deterministic and high-cost feedback loops (`test_metadata_fix.py`, `test_retrieval_on_server.py`).
- No dedicated fast unit-test layer means regressions in local business logic can ship without quick detection.
- Frontend has no automated test suite despite strict TypeScript config (`ChatBotFE/.../tsconfig.json:7`).
- Backend `.gitignore` contains `test_*.py` ignore patterns (decoded `ChatBotBE/backend/.gitignore` lines 139-146), which can undermine reliable versioned test coverage.

---

*Testing analysis: 2026-05-14*
