import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

import pytest_asyncio

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_liveness_probe(async_client):
    response = await async_client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

@pytest.mark.asyncio
async def test_health_check_endpoint(async_client):
    # Tests the base structure is returned properly
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "dependencies" in data
    assert "database" in data["dependencies"]
    assert "redis" in data["dependencies"]
    assert "chromadb" in data["dependencies"]
