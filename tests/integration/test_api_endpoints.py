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
