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
async def test_full_marketplace_workflow_api():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # 1. Create Client User
        client_payload = {
            "id": "client_fb_001",
            "name": "Jane Client",
            "email": "client@example.com",
            "auth_provider": "google.com",
            "role": "client",
        }
        client_resp = await ac.post("/api/v1/users/", json=client_payload)
        assert client_resp.status_code == 201
        assert client_resp.json()["id"] == "client_fb_001"

        # 2. Create Seller User
        seller_payload = {
            "id": "seller_fb_001",
            "name": "Master Tailor",
            "email": "tailor@example.com",
            "auth_provider": "email",
            "role": "seller",
        }
        seller_resp = await ac.post("/api/v1/users/", json=seller_payload)
        assert seller_resp.status_code == 201

        # 3. Create Shop for Seller
        shop_payload = {
            "seller_id": "seller_fb_001",
            "shop_name": "Royal Tailors",
            "city": "Colombo",
            "contact_number": "+94770001122",
        }
        shop_resp = await ac.post("/api/v1/shops/", json=shop_payload)
        assert shop_resp.status_code == 201
        shop_data = shop_resp.json()
        shop_id = shop_data["shop_id"]

        # 4. Client creates Clothing Request with Measurements, Voice Note, Design Images, & Service Type Toggle
        req_payload = {
            "client_id": "client_fb_001",
            "clothing_category": "Suit",
            "gender": "male",
            "fabric_status": "shop_provides",
            "description": "Black 3-piece tuxedo",
            "voice_note_url": "https://storage.googleapis.com/fiti-app/voice_notes/audio123.mp3",
            "service_type": "physical_visit",
            "request_location": "Colombo",
            "measurement": {
                "chest": 40.5,
                "waist": 34.0,
                "shoulder": 18.0,
            },
            "design_image_urls": [
                "https://storage.googleapis.com/fiti-app/inspiration/tuxedo_front.jpg",
                "https://storage.googleapis.com/fiti-app/inspiration/tuxedo_back.jpg",
            ],
            "target_shop_ids": [shop_id],
        }
        req_resp = await ac.post("/api/v1/orders/requests", json=req_payload)
        assert req_resp.status_code == 201
        req_data = req_resp.json()
        assert req_data["voice_note_url"] == "https://storage.googleapis.com/fiti-app/voice_notes/audio123.mp3"
        assert req_data["service_type"] == "physical_visit"
        assert len(req_data["design_images"]) == 2
        assert req_data["design_images"][0]["image_url"] == "https://storage.googleapis.com/fiti-app/inspiration/tuxedo_front.jpg"
        assert len(req_data["shop_requests"]) == 1
        shop_req_id = req_data["shop_requests"][0]["shop_request_id"]

        # 5. Tailor submits Bid
        bid_payload = {
            "shop_request_id": shop_req_id,
            "bid_amount": 25000.0,
            "message": "We can finish this in 3 days with Italian wool.",
        }
        bid_resp = await ac.post("/api/v1/orders/bids", json=bid_payload)
        assert bid_resp.status_code == 201

        # 6. Client Accepts Bid -> Order Created
        accept_payload = {
            "shop_request_id": shop_req_id,
            "accepted_price": 25000.0,
        }
        order_resp = await ac.post("/api/v1/orders/accept-bid", json=accept_payload)
        assert order_resp.status_code == 201
        order_data = order_resp.json()
        order_id = order_data["order_id"]
        assert order_data["order_status"] == "in_progress"

        # 7. Mock Payment
        pay_payload = {
            "order_id": order_id,
            "amount": 25000.0,
            "payment_method": "card",
        }
        pay_resp = await ac.post("/api/v1/orders/payments/mock", json=pay_payload)
        assert pay_resp.status_code == 201
        assert pay_resp.json()["payment_status"] == "paid"

        # 8. Complete Order & Submit Rating
        status_resp = await ac.patch(f"/api/v1/orders/{order_id}/status?order_status=completed")
        assert status_resp.status_code == 200
        assert status_resp.json()["order_status"] == "completed"

        rating_payload = {
            "order_id": order_id,
            "client_id": "client_fb_001",
            "shop_id": shop_id,
            "rating": 5,
            "review": "Excellent fitting and high quality craftsmanship!",
        }
        rating_resp = await ac.post("/api/v1/orders/ratings", json=rating_payload)
        assert rating_resp.status_code == 201
        assert rating_resp.json()["rating"] == 5
