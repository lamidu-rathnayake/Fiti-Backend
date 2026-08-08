import asyncio
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionFactory, engine
from app.domain.entities.order import (
    ClothingRequestStatusEnum,
    FabricStatusEnum,
    OrderStatusEnum,
    PaymentMethodEnum,
    PaymentStatusEnum,
    ServiceTypeEnum,
    ShopRequestStatusEnum,
)
from app.domain.entities.user import GenderEnum
from app.infrastructure.db.base import Base
from app.infrastructure.db.models.order_model import (
    BidModel,
    ClothingRequestImageModel,
    ClothingRequestModel,
    MeasurementModel,
    OrderModel,
    PaymentModel,
    RatingModel,
    ShopRequestModel,
)
from app.infrastructure.db.models.shop_model import ShopImageModel, ShopModel
from app.infrastructure.db.models.user_model import (
    ClientModel,
    MeasurementProfileModel,
    SellerModel,
)


async def seed_database():
    print("🚀 Connecting to database and creating tables if needed...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionFactory() as session:
        # Check if dummy clients already exist
        existing_client = await session.get(ClientModel, "client_demo_001")
        if existing_client:
            print("⚠️ Dummy data already exists in the database. Skipping seed.")
            return

        print("🌱 Seeding dummy data...")

        # 1. Create Dummy Clients
        client1 = ClientModel(id="client_demo_001")
        client2 = ClientModel(id="client_demo_002")
        session.add_all([client1, client2])
        await session.flush()

        # 2. Create Measurement Profile
        meas_profile1 = MeasurementProfileModel(
            client_id=client1.id,
            chest=38.5,
            waist=32.0,
            shoulder=17.5,
            sleeve=24.5,
            neck=15.5,
            hip=39.0,
            inseam=31.0,
            length=40.0,
            notes="Prefers slim fit around waist",
        )
        session.add(meas_profile1)

        # 3. Create Dummy Sellers
        seller1 = SellerModel(
            id="seller_demo_001",
            nic_front="https://storage.googleapis.com/fiti/nic/seller1_front.jpg",
            nic_rear="https://storage.googleapis.com/fiti/nic/seller1_rear.jpg",
            is_verified=True,
        )
        seller2 = SellerModel(
            id="seller_demo_002",
            nic_front="https://storage.googleapis.com/fiti/nic/seller2_front.jpg",
            nic_rear="https://storage.googleapis.com/fiti/nic/seller2_rear.jpg",
            is_verified=True,
        )
        session.add_all([seller1, seller2])
        await session.flush()

        # 4. Create Dummy Shops
        shop1 = ShopModel(
            seller_id=seller1.id,
            shop_name="Royal Tailors Colombo",
            shop_bio="Bespoke luxury suits and traditional formal attire crafted with Italian wool.",
            shop_address="123 Galle Road, Colombo 03",
            city="Colombo",
            contact_number="+94771234567",
            registration_number="REG-COL-2024-001",
            latitude=6.9271,
            longitude=79.8612,
            average_rating=4.8,
        )
        shop2 = ShopModel(
            seller_id=seller2.id,
            shop_name="Kandy Heritage Custom Apparel",
            shop_bio="Expert tailoring for weddings, ceremonies, and modern casual shirts.",
            shop_address="45 Peradeniya Road, Kandy",
            city="Kandy",
            contact_number="+94812233445",
            registration_number="REG-KDY-2024-002",
            latitude=7.2906,
            longitude=80.6337,
            average_rating=4.9,
        )
        session.add_all([shop1, shop2])
        await session.flush()

        # Add Shop Images
        shop1_img1 = ShopImageModel(shop_id=shop1.shop_id, image_url="https://images.unsplash.com/photo-1594938298603-c8148c4dae35")
        shop1_img2 = ShopImageModel(shop_id=shop1.shop_id, image_url="https://images.unsplash.com/photo-1598033129183-c4f50c736f10")
        shop2_img1 = ShopImageModel(shop_id=shop2.shop_id, image_url="https://images.unsplash.com/photo-1507679799987-c73779587ccf")
        session.add_all([shop1_img1, shop1_img2, shop2_img1])

        # 5. Create Clothing Request
        req1 = ClothingRequestModel(
            client_id=client1.id,
            target_date=date.today() + timedelta(days=14),
            target_budget=35000.0,
            clothing_category="3-Piece Suit",
            gender=GenderEnum.MALE,
            fabric_status=FabricStatusEnum.SHOP_PROVIDES,
            description="Custom navy blue 3-piece tuxedo with peak lapels for a wedding.",
            voice_note_url="https://storage.googleapis.com/fiti/voice/note_req_001.mp3",
            service_type=ServiceTypeEnum.PHYSICAL_VISIT,
            request_location="Colombo",
            status=ClothingRequestStatusEnum.OPEN,
        )
        session.add(req1)
        await session.flush()

        # Request Measurements & Images
        req1_meas = MeasurementModel(
            request_id=req1.request_id,
            chest=39.0,
            waist=33.0,
            shoulder=18.0,
            sleeve=25.0,
            notes="Slight room for shirt underneath",
        )
        req1_img = ClothingRequestImageModel(
            request_id=req1.request_id,
            image_url="https://images.unsplash.com/photo-1593030761757-71fae45fa0e7",
        )
        session.add_all([req1_meas, req1_img])

        # 6. Create Shop Request & Bid
        shop_req1 = ShopRequestModel(
            request_id=req1.request_id,
            shop_id=shop1.shop_id,
            offered_price=32000.0,
            status=ShopRequestStatusEnum.ACCEPTED,
        )
        session.add(shop_req1)
        await session.flush()

        bid1 = BidModel(
            shop_request_id=shop_req1.shop_request_id,
            bid_amount=32000.0,
            message="We can deliver within 10 days using premium Italian wool.",
        )
        session.add(bid1)

        # 7. Create Order & Payment
        order1 = OrderModel(
            shop_request_id=shop_req1.shop_request_id,
            order_status=OrderStatusEnum.COMPLETED,
            accepted_price=32000.0,
            started_date=date.today() - timedelta(days=7),
            completed_date=date.today(),
        )
        session.add(order1)
        await session.flush()

        payment1 = PaymentModel(
            order_id=order1.order_id,
            amount=32000.0,
            payment_method=PaymentMethodEnum.CARD,
            payment_status=PaymentStatusEnum.PAID,
            payment_date=datetime.now(UTC),
        )
        rating1 = RatingModel(
            order_id=order1.order_id,
            client_id=client1.id,
            shop_id=shop1.shop_id,
            rating=5,
            review="Phenomenal fit and exceptional craftmanship! Highly recommended.",
        )
        session.add_all([payment1, rating1])

        # Commit all data
        await session.commit()
        print("✅ Dummy data successfully seeded into database!")
        print("   - 2 Clients created (client_demo_001, client_demo_002)")
        print("   - 2 Sellers created (seller_demo_001, seller_demo_002)")
        print("   - 2 Shops created ('Royal Tailors Colombo', 'Kandy Heritage Custom Apparel')")
        print("   - 1 Clothing Request with measurement, bid, completed order, payment & rating")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
