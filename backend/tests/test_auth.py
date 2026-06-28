import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/api/v1/auth/register", json={"full_name": "Test User", "email": "test@example.com", "password": "password123", "role": "sales_rep"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login(client):
    await client.post("/api/v1/auth/register", json={"full_name": "Login User", "email": "login@example.com", "password": "password123"})
    response = await client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={"full_name": "Wrong User", "email": "wrong@example.com", "password": "password123"})
    response = await client.post("/api/v1/auth/login", json={"email": "wrong@example.com", "password": "wrongpassword"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client):
    await client.post("/api/v1/auth/register", json={"full_name": "Current User", "email": "current@example.com", "password": "password123"})
    login_response = await client.post("/api/v1/auth/login", json={"email": "current@example.com", "password": "password123"})
    token = login_response.json()["access_token"]
    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "current@example.com"


@pytest.mark.asyncio
async def test_protected_route_no_token(client):
    response = await client.get("/api/v1/customers")
    assert response.status_code == 401
