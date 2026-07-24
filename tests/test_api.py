import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import engine
from app.infrastructure.db.base import Base


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    """Create DB tables for API tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_health_check_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_and_get_user_api():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create user
        payload = {
            "email": "api_user@example.com",
            "username": "api_user",
            "password": "securepassword123",
        }
        create_resp = await ac.post("/api/v1/users/", json=payload)
        assert create_resp.status_code == 201
        created_data = create_resp.json()
        assert created_data["email"] == "api_user@example.com"
        assert "id" in created_data

        user_id = created_data["id"]

        # Fetch user
        get_resp = await ac.get(f"/api/v1/users/{user_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["username"] == "api_user"

        # List users
        list_resp = await ac.get("/api/v1/users/")
        assert list_resp.status_code == 200
        users_list = list_resp.json()
        assert len(users_list) >= 1
