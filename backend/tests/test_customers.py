import pytest


async def get_auth_token(client) -> str:
    await client.post("/api/v1/auth/register", json={"full_name": "Test Admin", "email": "admin@test.com", "password": "password123", "role": "admin"})
    response = await client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "password123"})
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_customer(client):
    token = await get_auth_token(client)
    response = await client.post("/api/v1/customers", json={"company_name": "Acme Corp", "contact_person": "John Doe", "email": "john@acme.com", "industry": "Technology", "annual_revenue": 1000000, "company_size": 50}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["company_name"] == "Acme Corp"


@pytest.mark.asyncio
async def test_list_customers(client):
    token = await get_auth_token(client)
    response = await client.get("/api/v1/customers", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
