"""
Integration Tests for FastAPI REST Endpoints
Validates API contract, status codes, and end-to-end HTTP request lifecycle.
"""

import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.database import init_db
from rag.vector_store import vector_store


@pytest.fixture(autouse=True, scope="function")
def setup_test_env():
    """Synchronous fixture ensuring DB schema and vector store are ready."""
    asyncio.run(init_db())
    vector_store.load()


@pytest.mark.asyncio
async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "similarity_policy" in data
        assert data["similarity_policy"]["duplicate_threshold"] == 0.82


@pytest.mark.asyncio
async def test_submit_and_diagnose_pipeline_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Submit Bug
        sub_payload = {
            "title": "Deadlock in database connection catalog loader",
            "raw_content": "Database deadlock detected in ConnectionProfile and CatalogLoader threads.",
            "input_type": "bug_report"
        }
        sub_resp = await client.post("/api/submissions", json=sub_payload)
        assert sub_resp.status_code == 201
        sub_data = sub_resp.json()
        sub_id = sub_data["id"]
        assert sub_data["title"] == sub_payload["title"]

        # 2. Run Diagnosis
        diag_resp = await client.post(f"/api/diagnosis/run/{sub_id}")
        assert diag_resp.status_code == 200
        diag_data = diag_resp.json()
        assert diag_data["submission_id"] == sub_id
        assert diag_data["triage"]["severity"] in ["Critical", "High", "Medium", "Low"]
        assert diag_data["root_cause"]["hypothesis"] is not None
        assert diag_data["remediation"]["action"] is not None

        # 3. Retrieve Diagnosis by Submission ID
        get_diag = await client.get(f"/api/diagnosis/{sub_id}")
        assert get_diag.status_code == 200
        assert get_diag.json()["submission_id"] == sub_id


@pytest.mark.asyncio
async def test_submit_and_immediate_get_diagnosis_flow():
    """
    Validates canonical frontend workflow:
    1. POST /api/submissions (creates bug submission)
    2. Immediate GET /api/diagnosis/{submission_id} (executes and returns canonical diagnosis)
    3. Confirms real outputs from all 6 pipeline components:
       - Triage
       - Log Analysis
       - RAG evidence
       - Duplicate Detection
       - Root Cause
       - Remediation
    4. Subsequent GET returns persisted record without re-execution.
    5. GET for non-existent submission returns 404.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. POST /api/submissions
        payload = {
            "title": "NullPointerException in authentication filter token validation",
            "raw_content": (
                "Exception in thread \"main\" java.lang.NullPointerException: Cannot invoke String.trim() on null\n"
                "    at com.example.auth.AuthFilter.doFilter(AuthFilter.java:42)\n"
                "    at com.example.web.FilterChain.proceed(FilterChain.java:18)"
            ),
            "input_type": "stack_trace"
        }
        create_resp = await client.post("/api/submissions", json=payload)
        assert create_resp.status_code == 201
        sub_id = create_resp.json()["id"]

        # 2. Immediate GET /api/diagnosis/{sub_id} (canonical diagnosis request)
        diag_resp = await client.get(f"/api/diagnosis/{sub_id}")
        assert diag_resp.status_code == 200
        data = diag_resp.json()

        # 3. Verify valid JSON and core properties
        assert data["submission_id"] == sub_id

        # 4. Verify outputs from all 6 agents/components:
        # Triage
        assert data["triage"] is not None
        assert data["triage"]["severity"] in ["Critical", "High", "Medium", "Low"]
        assert data["triage"]["priority"] in ["High", "Medium", "Low"]
        assert data["triage"]["confidence"] > 0

        # Log Analysis
        assert data["log_analysis"] is not None
        assert data["log_analysis"]["exception_type"] == "java.lang.NullPointerException"
        assert data["log_analysis"]["failure_point"] is not None
        assert len(data["log_analysis"]["stack_frames"]) >= 1

        # RAG Evidence
        assert "rag_retrieval" in data
        assert isinstance(data["rag_retrieval"], list)

        # Duplicate Detection
        assert data["duplicate_detection"] is not None
        assert isinstance(data["duplicate_detection"]["is_duplicate"], bool)
        assert "duplicate_threshold" in data["duplicate_detection"]

        # Root Cause
        assert data["root_cause"] is not None
        assert len(data["root_cause"]["hypothesis"]) > 0
        assert data["root_cause"]["confidence"] > 0

        # Remediation
        assert data["remediation"] is not None
        assert len(data["remediation"]["action"]) > 0
        assert len(data["remediation"]["recommended_tests"]) > 0

        # 5. Subsequent GET returns persisted record
        cached_resp = await client.get(f"/api/diagnosis/{sub_id}")
        assert cached_resp.status_code == 200
        cached_data = cached_resp.json()
        assert cached_data["submission_id"] == sub_id
        assert cached_data["triage"]["severity"] == data["triage"]["severity"]

        # 6. GET non-existent submission returns 404
        missing_resp = await client.get("/api/diagnosis/00000000-0000-0000-0000-000000000000")
        assert missing_resp.status_code == 404


@pytest.mark.asyncio
async def test_historical_defects_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/historical?project=Mozilla")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        if items:
            assert items[0]["project"] == "Mozilla"


@pytest.mark.asyncio
async def test_analytics_api_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/analytics")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_submissions" in data
        assert "reconciliation_verified" in data
        assert data["reconciliation_verified"] is True
