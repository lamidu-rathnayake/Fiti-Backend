import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.database import engine
from app.infrastructure.db.base import Base
from app.main import app
from app.core.security import get_current_user_uid

app.dependency_overrides[get_current_user_uid] = lambda: "mock_firebase_uid"


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    """Create DB tables for API tests."""
    from sqlalchemy import insert
    from app.infrastructure.db.models.rbac_model import RoleModel, UserRoleModel
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Seed mock roles for testing
        await conn.execute(insert(RoleModel).values(id=1, name="client"))
        await conn.execute(insert(RoleModel).values(id=2, name="tailor"))
        await conn.execute(insert(RoleModel).values(id=3, name="admin"))
        await conn.execute(insert(UserRoleModel).values(firebase_uid="mock_firebase_uid", role_id=1))
        await conn.execute(insert(UserRoleModel).values(firebase_uid="mock_firebase_uid", role_id=2))
        await conn.execute(insert(UserRoleModel).values(firebase_uid="mock_firebase_uid", role_id=3))
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
async def test_option2_client_registration_without_body_id():
    """
    Tests Option 2 direct registration flow where the frontend omits 'id' in the JSON body,
    and FastAPI extracts the authenticated Firebase UID from the security context.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # 1. Register Client Profile without supplying 'id' in body
        client_resp = await ac.post("/api/v1/profiles/client", json={})
        assert client_resp.status_code == 201
        # In mock mode, defaults to 'mock_firebase_uid'
        assert client_resp.json()["id"] == "mock_firebase_uid"


@pytest.mark.asyncio
async def test_full_marketplace_workflow_api():
    """
    End-to-end marketplace workflow test.

    Architecture note: User identity (name, email, password) is fully managed
    by Firebase Auth on the frontend. The backend only receives Firebase UIDs
    and creates role-specific profile extensions in PostgreSQL.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # 1. Register Client Profile
        # (In production: called after Firebase Auth sign-up on the frontend)
        client_resp = await ac.post("/api/v1/profiles/client", json={"id": "client_fb_001"})
        assert client_resp.status_code == 201
        assert client_resp.json()["id"] == "client_fb_001"

        # 2. Register Tailor Profile
        tailor_resp = await ac.post(
            "/api/v1/profiles/tailor",
            json={
                "id": "tailor_fb_001",
                "nic_front": "https://storage.googleapis.com/fiti/nic/front.jpg",
                "nic_rear": "https://storage.googleapis.com/fiti/nic/rear.jpg",
            },
        )
        assert tailor_resp.status_code == 201
        assert tailor_resp.json()["is_verified"] is False

        # 3. Duplicate client profile registration should return 409
        dup_resp = await ac.post("/api/v1/profiles/client", json={"id": "client_fb_001"})
        assert dup_resp.status_code == 409

        # 4. Save Measurement Profile for Client
        meas_resp = await ac.put(
            "/api/v1/profiles/client/client_fb_001/measurements",
            json={"chest": 40.5, "waist": 34.0, "shoulder": 18.0},
        )
        assert meas_resp.status_code == 200
        assert meas_resp.json()["client_id"] == "client_fb_001"
        assert meas_resp.json()["chest"] == 40.5

        # 5. Create Shop for Tailor
        shop_resp = await ac.post(
            "/api/v1/shops/",
            json={
                "tailor_id": "tailor_fb_001",
                "shop_name": "Royal Tailors",
                "city": "Colombo",
                "contact_number": "+94770001122",
            },
        )
        assert shop_resp.status_code == 201
        shop_id = shop_resp.json()["shop_id"]

        # 6. Client Creates Clothing Request with Voice Note, Design Images & Service Type
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
        assert req_data["voice_note_url"] == "https://storage.googleapis.com/fiti/voice/audio123.mp3"
        assert req_data["service_type"] == "physical_visit"
        assert len(req_data["design_images"]) == 2
        assert len(req_data["shop_requests"]) == 1
        shop_req_id = req_data["shop_requests"][0]["shop_request_id"]

        # 7. Tailor Submits Bid
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
        order_resp = await ac.post(
            "/api/v1/orders/accept-bid",
            json={"shop_request_id": shop_req_id, "accepted_price": 25000.0},
        )
        assert order_resp.status_code == 201
        order_data = order_resp.json()
        order_id = order_data["order_id"]
        assert order_data["order_status"] == "in_progress"

        # 9. Mock Payment
        pay_resp = await ac.post(
            "/api/v1/orders/payments/mock",
            json={"order_id": order_id, "amount": 25000.0, "payment_method": "card"},
        )
        assert pay_resp.status_code == 201
        assert pay_resp.json()["payment_status"] == "paid"

        # 10. Complete Order
        status_resp = await ac.patch(f"/api/v1/orders/{order_id}/status?order_status=completed")
        assert status_resp.status_code == 200
        assert status_resp.json()["order_status"] == "completed"

        # 11. Client Submits Rating
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
        assert rating_resp.json()["rating"] == 5


@pytest.mark.asyncio
async def test_rbac_endpoints():

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Assign role
        res = await ac.post("/api/v1/rbac/assign-role", json={"user_id": "user_999", "role_name": "client"})
        assert res.status_code == 204
        
        # 2. Get user access
        res = await ac.get("/api/v1/rbac/users/user_999/access")
        assert res.status_code == 200
        data = res.json()
        assert "client" in data["roles"]
        
        # 3. Check route access
        res = await ac.get("/api/v1/rbac/users/user_999/check-route?route_name=/some/route")
        assert res.status_code == 200
        assert "has_access" in res.json()


@pytest.mark.asyncio
async def test_support_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create notification
        res = await ac.post("/api/v1/support/notifications", json={"user_id": "user_1", "title": "Test Alert"})
        assert res.status_code == 201
        n_id = res.json()["notification_id"]
        
        # 2. List notifications
        res = await ac.get("/api/v1/support/notifications/user_1")
        assert res.status_code == 200
        assert len(res.json()) >= 1
        
        # 3. Mark read
        res = await ac.patch(f"/api/v1/support/notifications/{n_id}/read")
        assert res.status_code == 204
        
        # 4. Create favorite
        # Note: requires a valid shop_id. Let's create a shop first.
        # But wait, foreign keys might fail if the shop doesn't exist.
        # Wait, the sqlite db handles foreign keys if enabled. Let's create a dummy tailor and shop.
        client_res = await ac.post("/api/v1/profiles/client", json={"id": "client_1"})
        assert client_res.status_code == 201

        tailor_res = await ac.post("/api/v1/profiles/tailor", json={"id": "tailor_fav", "nic_front": "http://img.com/nic"})
        assert tailor_res.status_code == 201
        
        shop_res = await ac.post("/api/v1/shops/", json={
            "tailor_id": "tailor_fav", "shop_name": "Fav Shop", "city": "Kandy", "contact_number": "123"
        })
        assert shop_res.status_code == 201
        shop_id = shop_res.json()["shop_id"]

        res = await ac.post("/api/v1/support/favorites", json={"client_id": "client_1", "shop_id": shop_id})
        assert res.status_code == 201
        
        # 5. List favorites
        res = await ac.get("/api/v1/support/favorites/client_1")
        assert res.status_code == 200
        assert len(res.json()) == 1
        
        # 6. Remove favorite
        res = await ac.delete(f"/api/v1/support/favorites/client_1/{shop_id}")
        assert res.status_code == 204


@pytest.mark.asyncio
async def test_shop_listing_and_update_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        tailor_res = await ac.post("/api/v1/profiles/tailor", json={"id": "tailor_search", "nic_front": "http://img.com/nic"})
        assert tailor_res.status_code == 201
        
        shop_res = await ac.post("/api/v1/shops/", json={
            "tailor_id": "tailor_search", "shop_name": "Search Shop", "city": "Galle", "contact_number": "123"
        })
        assert shop_res.status_code == 201
        shop_id = shop_res.json()["shop_id"]

        # Update
        res = await ac.put(f"/api/v1/shops/{shop_id}", json={
            "shop_name": "Updated Shop", "city": "Galle", "contact_number": "123"
        })
        assert res.status_code == 200
        assert res.json()["shop_name"] == "Updated Shop"
        
        # Search nearby shops
        res = await ac.get("/api/v1/shops/nearby?lat=6.92&lng=79.86&radius_km=10")
        assert res.status_code == 200
        assert type(res.json()) is list
        
        # Get by tailor
        res = await ac.get("/api/v1/shops/tailor/tailor_search")
        assert res.status_code == 200
        assert len(res.json()) >= 1
        
        # Delete
        res = await ac.delete(f"/api/v1/shops/{shop_id}")
        assert res.status_code == 204
