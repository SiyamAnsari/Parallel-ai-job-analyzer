"""
Unit tests for FastAPI endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from api import app
from src.data.sample_data import SAMPLE_CANDIDATE_DATA_ANALYST, SAMPLE_JOBS_BATCH


@pytest.mark.asyncio
async def test_api_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "available_models" in data


@pytest.mark.asyncio
async def test_api_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Parallel AI Job Analyzer" in data["app"]


@pytest.mark.asyncio
async def test_api_analyze_batch():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "candidate": SAMPLE_CANDIDATE_DATA_ANALYST.model_dump(),
            "jobs": [j.model_dump() for j in SAMPLE_JOBS_BATCH[:2]],
            "concurrency_limit": 2
        }
        response = await ac.post("/api/v1/analyze-batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_jobs_analyzed"] == 2
    assert len(data["results"]) == 2
    assert len(data["comparison_table"]) == 2

