import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from collections.abc import AsyncGenerator

from app.infrastructure.db.base import Base
from app.main import app
from app.core.security import get_current_user_uid, get_current_user
from app.core.database import get_db_session

from sqlalchemy import text
from app.core.config import settings

# Test Database Engine (Supabase PostgreSQL)
test_engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"server_settings": {"search_path": "test"}},
    poolclass=NullPool,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=test_engine, class_=AsyncSession
)

async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

app.dependency_overrides[get_db_session] = override_get_db_session

# Global mock state for tests to easily swap active user
current_mock_user = {
    "uid": "mock_firebase_uid",
    "email": "mock@example.com",
    "role": "client",
    "name": "Mock User",
    "picture": None,
}

def mock_get_current_user():
    return current_mock_user.copy()

def set_mock_user(uid: str, role: str):
    current_mock_user["uid"] = uid
    current_mock_user["role"] = role

app.dependency_overrides[get_current_user] = mock_get_current_user
app.dependency_overrides[get_current_user_uid] = lambda: current_mock_user["uid"]


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    """Create DB tables for API tests."""
    from sqlalchemy import insert
    from app.infrastructure.db.models.rbac_model import RoleModel, UserRoleModel
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS test"))
        await conn.run_sync(Base.metadata.create_all)
        # Seed mock roles for testing
        await conn.execute(insert(RoleModel).values(id=1, name="client"))
        await conn.execute(insert(RoleModel).values(id=2, name="tailor"))
        await conn.execute(insert(RoleModel).values(id=3, name="admin"))
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
    # Reset mock user after each test
    set_mock_user("mock_firebase_uid", "client")


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
async def test_option2_client_registration_without_body_id():
    """
    Tests Option 2 direct registration flow where the frontend omits 'id' in the JSON body,
    and FastAPI extracts the authenticated Firebase UID from the security context.
    """
    set_mock_user("client_auto_id", "client")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        client_resp = await ac.post("/api/v1/profiles/client", json={})
        assert client_resp.status_code == 201
        assert client_resp.json()["id"] == "client_auto_id"


@pytest.mark.asyncio
async def test_full_marketplace_workflow_api():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # 1. Register Client Profile
        set_mock_user("client_fb_001", "client")
        client_resp = await ac.post("/api/v1/profiles/client", json={"id": "client_fb_001"})
        assert client_resp.status_code == 201

        # 2. Register Tailor Profile
        set_mock_user("tailor_fb_001", "tailor")
        tailor_resp = await ac.post(
            "/api/v1/profiles/tailor",
            json={
                "id": "tailor_fb_001",
                "nic_front": "https://storage.googleapis.com/fiti/nic/front.jpg",
                "nic_rear": "https://storage.googleapis.com/fiti/nic/rear.jpg",
            },
        )
        assert tailor_resp.status_code == 201

        # 3. Duplicate client profile registration should return 409
        set_mock_user("client_fb_001", "client")
        dup_resp = await ac.post("/api/v1/profiles/client", json={"id": "client_fb_001"})
        assert dup_resp.status_code == 409

        # 4. Save Measurement Profile for Client
        set_mock_user("client_fb_001", "client")
        meas_resp = await ac.put(
            "/api/v1/profiles/client/client_fb_001/measurements",
            json={"chest": 40.5, "waist": 34.0, "shoulder": 18.0},
        )
        assert meas_resp.status_code == 200

        # 5. Create Shop for Tailor
        set_mock_user("tailor_fb_001", "tailor")
        shop_resp = await ac.post(
            "/api/v1/shops/",
            json={
                "shop_name": "Royal Tailors",
                "city": "Colombo",
                "contact_number": "+94770001122",
            },
        )
        assert shop_resp.status_code == 201
        shop_id = shop_resp.json()["shop_id"]

        # 6. Client Creates Clothing Request
        set_mock_user("client_fb_001", "client")
        req_resp = await ac.post(
            "/api/v1/orders/requests",
            json={
                "client_id": "client_fb_001",
                "clothing_category": "Suit",
                "gender": "male",
                "fabric_status": "shop_provides",
                "description": "Black 3-piece tuxedo",
                "voice_note_url": "https://storage.googleapis.com/fiti/voice/audio123.mp3",
                "service_type": "physical_visit",
                "request_location": "Colombo",
                "measurement": {"chest": 40.5, "waist": 34.0, "shoulder": 18.0},
                "design_image_urls": [
                    "https://storage.googleapis.com/fiti/inspiration/tuxedo_front.jpg",
                    "https://storage.googleapis.com/fiti/inspiration/tuxedo_back.jpg",
                ],
                "target_shop_ids": [shop_id],
            },
        )
        assert req_resp.status_code == 201
        req_data = req_resp.json()
        shop_req_id = req_data["shop_requests"][0]["shop_request_id"]

        # 7. Tailor Submits Bid
        set_mock_user("tailor_fb_001", "tailor")
        bid_resp = await ac.post(
            "/api/v1/orders/bids",
            json={
                "shop_request_id": shop_req_id,
                "bid_amount": 25000.0,
                "message": "We can finish in 3 days with Italian wool.",
            },
        )
        assert bid_resp.status_code == 201

        # 8. Client Accepts Bid → Order Created
        set_mock_user("client_fb_001", "client")
        order_resp = await ac.post(
            "/api/v1/orders/accept-bid",
            json={"shop_request_id": shop_req_id, "accepted_price": 25000.0},
        )
        assert order_resp.status_code == 201
        order_id = order_resp.json()["order_id"]

        # 9. Mock Payment
        set_mock_user("client_fb_001", "client")
        pay_resp = await ac.post(
            "/api/v1/orders/payments/mock",
            json={"order_id": order_id, "amount": 25000.0, "payment_method": "card"},
        )
        assert pay_resp.status_code == 201

        # 10. Complete Order
        # Any authenticated user with access to the order can mark it completed (depending on RBAC design).
        # We assume the tailor or client can. Let's use tailor.
        set_mock_user("tailor_fb_001", "tailor")
        status_resp = await ac.patch(f"/api/v1/orders/{order_id}/status?order_status=completed")
        assert status_resp.status_code == 200

        # 11. Client Submits Rating
        set_mock_user("client_fb_001", "client")
        rating_resp = await ac.post(
            "/api/v1/orders/ratings",
            json={
                "order_id": order_id,
                "client_id": "client_fb_001",
                "shop_id": shop_id,
                "rating": 5,
                "review": "Excellent fitting and high quality craftsmanship!",
            },
        )
        assert rating_resp.status_code == 201


@pytest.mark.asyncio
async def test_support_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        
        # 1. Create a client
        set_mock_user("client_1", "client")
        client_res = await ac.post("/api/v1/profiles/client", json={"id": "client_1"})
        assert client_res.status_code == 201

        # 2. Create a tailor and shop to favorite
        set_mock_user("tailor_fav", "tailor")
        tailor_res = await ac.post("/api/v1/profiles/tailor", json={"id": "tailor_fav", "nic_front": "https://img.com/nic"})
        assert tailor_res.status_code == 201
        
        shop_res = await ac.post("/api/v1/shops/", json={
            "shop_name": "Fav Shop", "city": "Kandy", "contact_number": "+94770001133"
        })
        assert shop_res.status_code == 201
        shop_id = shop_res.json()["shop_id"]

        # Switch back to client
        set_mock_user("client_1", "client")
        
        # Create notification
        res = await ac.post("/api/v1/support/notifications", json={"user_id": "client_1", "title": "Test Alert"})
        assert res.status_code == 201
        n_id = res.json()["notification_id"]
        
        res = await ac.get("/api/v1/support/notifications/client_1")
        assert res.status_code == 200
        
        res = await ac.patch(f"/api/v1/support/notifications/{n_id}/read")
        assert res.status_code == 204
        
        res = await ac.post("/api/v1/support/favorites", json={"client_id": "client_1", "shop_id": shop_id})
        assert res.status_code == 201
        
        res = await ac.get("/api/v1/support/favorites/client_1")
        assert res.status_code == 200
        
        res = await ac.delete(f"/api/v1/support/favorites/client_1/{shop_id}")
        assert res.status_code == 204


@pytest.mark.asyncio
async def test_shop_listing_and_update_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        set_mock_user("tailor_search", "tailor")
        tailor_res = await ac.post("/api/v1/profiles/tailor", json={"id": "tailor_search", "nic_front": "https://img.com/nic"})
        assert tailor_res.status_code == 201
        
        shop_res = await ac.post("/api/v1/shops/", json={
            "shop_name": "Search Shop", "city": "Galle", "contact_number": "+94770001144"
        })
        assert shop_res.status_code == 201
        shop_id = shop_res.json()["shop_id"]

        image_res = await ac.post(
            f"/api/v1/shops/{shop_id}/images",
            json={"image_url": "https://example.com/shop.jpg"},
        )
        assert image_res.status_code == 201

        # Update
        res = await ac.put(f"/api/v1/shops/{shop_id}", json={
            "shop_name": "Updated Shop", "city": "Galle", "contact_number": "+94770001144"
        })
        assert res.status_code == 200
        
        # Search nearby shops (Public endpoint, mock identity doesn't matter much)
        set_mock_user("client_random", "client")
        res = await ac.get("/api/v1/shops/nearby?lat=6.92&lng=79.86&radius_km=10")
        assert res.status_code == 200
        
        # Get by tailor
        res = await ac.get("/api/v1/shops/tailor/tailor_search")
        assert res.status_code == 200

        # Try to update shop as a completely different user
        set_mock_user("other_firebase_uid", "tailor")
        forbidden_res = await ac.put(f"/api/v1/shops/{shop_id}", json={
            "shop_name": "Unauthorized Update", "city": "Galle", "contact_number": "+94770001144"
        })
        # Note: Depending on your exact implementation in the endpoints, 
        # this might return 403 or 404 (if shop is filtered by tailor_id). 
        assert forbidden_res.status_code in [403, 404]
        
        set_mock_user("tailor_search", "tailor")
        # Delete
        res = await ac.delete(f"/api/v1/shops/{shop_id}")
        assert res.status_code == 204
