
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.order import (
    Bid,
    ClothingRequest,
    ClothingRequestImage,
    ClothingRequestStatusEnum,
    Order,
    OrderStatusEnum,
    Payment,
    Rating,
    ShopRequest,
    ShopRequestStatusEnum,
)
from app.domain.repositories.order_repository import AbstractOrderRepository
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
from app.infrastructure.db.models.user_model import MeasurementProfileModel


class SQLAlchemyOrderRepository(AbstractOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_clothing_request(self, request: ClothingRequest) -> ClothingRequest:
        model = ClothingRequestModel(
            client_id=request.client_id,
            target_date=request.target_date,
            target_budget=request.target_budget,
            clothing_category=request.clothing_category,
            gender=request.gender,
            fabric_status=request.fabric_status,
            description=request.description,
            voice_note_url=request.voice_note_url,
            service_type=request.service_type,
            request_location=request.request_location,
            status=request.status,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        if request.measurement:
            meas_model = MeasurementModel(
                request_id=model.request_id,
                chest=request.measurement.chest,
                waist=request.measurement.waist,
                shoulder=request.measurement.shoulder,
                sleeve=request.measurement.sleeve,
                neck=request.measurement.neck,
                hip=request.measurement.hip,
                inseam=request.measurement.inseam,
                length=request.measurement.length,
                notes=request.measurement.notes,
            )
            self.session.add(meas_model)
            await self.session.commit()
        else:
            # If no per-request measurements provided, reference client's saved profile if exists
            stmt = select(MeasurementProfileModel).where(MeasurementProfileModel.client_id == request.client_id)
            res = await self.session.execute(stmt)
            profile = res.scalar_one_or_none()
            if profile:
                model.measurement_profile_id = profile.measurement_id
                await self.session.commit()

        # Re-fetch with relationships
        fetched = await self.get_clothing_request(model.request_id)
        assert fetched is not None
        return fetched

    async def get_clothing_request(self, request_id: int) -> ClothingRequest | None:
        stmt = (
            select(ClothingRequestModel)
            .options(
                selectinload(ClothingRequestModel.measurement),
                selectinload(ClothingRequestModel.design_images),
                selectinload(ClothingRequestModel.shop_requests).selectinload(ShopRequestModel.bids),
            )
            .where(ClothingRequestModel.request_id == request_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def list_clothing_requests_by_client(self, client_id: str) -> list[ClothingRequest]:
        stmt = (
            select(ClothingRequestModel)
            .options(
                selectinload(ClothingRequestModel.measurement),
                selectinload(ClothingRequestModel.design_images),
                selectinload(ClothingRequestModel.shop_requests).selectinload(ShopRequestModel.bids),
            )
            .where(ClothingRequestModel.client_id == client_id)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def list_open_clothing_requests(self, skip: int = 0, limit: int = 100) -> list[ClothingRequest]:
        stmt = (
            select(ClothingRequestModel)
            .options(
                selectinload(ClothingRequestModel.measurement),
                selectinload(ClothingRequestModel.design_images),
                selectinload(ClothingRequestModel.shop_requests).selectinload(ShopRequestModel.bids),
            )
            .where(ClothingRequestModel.status == ClothingRequestStatusEnum.OPEN)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def add_design_image(self, image: ClothingRequestImage) -> ClothingRequestImage:
        model = ClothingRequestImageModel(
            request_id=image.request_id,
            image_url=image.image_url,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def create_shop_request(self, shop_request: ShopRequest) -> ShopRequest:
        model = ShopRequestModel(
            request_id=shop_request.request_id,
            shop_id=shop_request.shop_id,
            offered_price=shop_request.offered_price,
            status=shop_request.status,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        fetched = await self.get_shop_request(model.shop_request_id)
        return fetched if fetched else ShopRequest(shop_id=model.shop_id, shop_request_id=model.shop_request_id, request_id=model.request_id)

    async def get_shop_request(self, shop_request_id: int) -> ShopRequest | None:
        stmt = (
            select(ShopRequestModel)
            .where(ShopRequestModel.shop_request_id == shop_request_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def list_shop_requests_by_shop(self, shop_id: int) -> list[ShopRequest]:
        stmt = (
            select(ShopRequestModel)
            .where(ShopRequestModel.shop_id == shop_id)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def create_bid(self, bid: Bid) -> Bid:
        model = BidModel(
            shop_request_id=bid.shop_request_id,
            bid_amount=bid.bid_amount,
            message=bid.message,
        )
        self.session.add(model)

        # Update shop_request offered_price & status to QUOTED
        sr_stmt = select(ShopRequestModel).where(
            ShopRequestModel.shop_request_id == bid.shop_request_id
        )
        sr_res = await self.session.execute(sr_stmt)
        sr_model = sr_res.scalar_one_or_none()
        if sr_model:
            sr_model.offered_price = bid.bid_amount
            sr_model.status = ShopRequestStatusEnum.QUOTED

        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def create_order(self, order: Order) -> Order:
        model = OrderModel(
            shop_request_id=order.shop_request_id,
            order_status=order.order_status,
            accepted_price=order.accepted_price,
            started_date=order.started_date,
            completed_date=order.completed_date,
        )
        self.session.add(model)

        # Mark shop request accepted
        sr_stmt = select(ShopRequestModel).where(
            ShopRequestModel.shop_request_id == order.shop_request_id
        )
        sr_res = await self.session.execute(sr_stmt)
        sr_model = sr_res.scalar_one_or_none()
        if sr_model:
            sr_model.status = ShopRequestStatusEnum.ACCEPTED
            # Mark parent clothing request in_progress
            cr_stmt = select(ClothingRequestModel).where(ClothingRequestModel.request_id == sr_model.request_id)
            cr_res = await self.session.execute(cr_stmt)
            cr_model = cr_res.scalar_one_or_none()
            if cr_model:
                cr_model.status = ClothingRequestStatusEnum.IN_PROGRESS

        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def get_order(self, order_id: int) -> Order | None:
        stmt = select(OrderModel).where(OrderModel.order_id == order_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def list_orders_by_shop(self, shop_id: int) -> list[Order]:
        stmt = (
            select(OrderModel)
            .join(ShopRequestModel, ShopRequestModel.shop_request_id == OrderModel.shop_request_id)
            .where(ShopRequestModel.shop_id == shop_id)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def list_orders_by_client(self, client_id: str) -> list[Order]:
        stmt = (
            select(OrderModel)
            .join(ShopRequestModel, ShopRequestModel.shop_request_id == OrderModel.shop_request_id)
            .join(ClothingRequestModel, ClothingRequestModel.request_id == ShopRequestModel.request_id)
            .where(ClothingRequestModel.client_id == client_id)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def update_order_status(self, order_id: int, status: str) -> Order:
        stmt = select(OrderModel).where(OrderModel.order_id == order_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.order_status = OrderStatusEnum(status)
            if status == OrderStatusEnum.COMPLETED.value:
                # Update clothing request status to COMPLETED
                sr_stmt = select(ShopRequestModel).where(ShopRequestModel.shop_request_id == model.shop_request_id)
                sr_res = await self.session.execute(sr_stmt)
                sr_model = sr_res.scalar_one_or_none()
                if sr_model:
                    cr_stmt = select(ClothingRequestModel).where(ClothingRequestModel.request_id == sr_model.request_id)
                    cr_res = await self.session.execute(cr_stmt)
                    cr_model = cr_res.scalar_one_or_none()
                    if cr_model:
                        cr_model.status = ClothingRequestStatusEnum.COMPLETED
            await self.session.commit()
            await self.session.refresh(model)
            return model.to_domain()
        raise ValueError(f"Order {order_id} not found")

    async def create_payment(self, payment: Payment) -> Payment:
        model = PaymentModel(
            order_id=payment.order_id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            payment_status=payment.payment_status,
            payment_date=payment.payment_date,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def get_payment(self, payment_id: int) -> Payment | None:
        stmt = select(PaymentModel).where(PaymentModel.payment_id == payment_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def create_rating(self, rating: Rating) -> Rating:
        model = RatingModel(
            order_id=rating.order_id,
            client_id=rating.client_id,
            shop_id=rating.shop_id,
            rating=rating.rating,
            review=rating.review,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.to_domain()

    async def get_ratings_by_shop(self, shop_id: int) -> list[Rating]:
        stmt = select(RatingModel).where(RatingModel.shop_id == shop_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]
