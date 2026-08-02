from typing import List, Optional
from datetime import datetime, timezone
from app.domain.entities.order import (
    ClothingRequest,
    ClothingRequestImage,
    Measurement,
    ShopRequest,
    Bid,
    Order,
    Payment,
    Rating,
    ClothingRequestStatusEnum,
    ShopRequestStatusEnum,
    OrderStatusEnum,
    PaymentStatusEnum,
)
from app.domain.repositories.order_repository import AbstractOrderRepository
from app.domain.repositories.shop_repository import AbstractShopRepository
from app.domain.exceptions.order import (
    OrderNotFoundError,
    ClothingRequestNotFoundError,
    ShopRequestNotFoundError,
    InvalidOrderStateTransitionError,
)
from app.use_cases.dtos.order_dto import (
    ClothingRequestCreateDTO,
    ClothingRequestOutputDTO,
    ClothingRequestImageDTO,
    MeasurementDTO,
    BidCreateDTO,
    BidDTO,
    ShopRequestDTO,
    OrderCreateDTO,
    OrderOutputDTO,
    MockPaymentDTO,
    PaymentOutputDTO,
    RatingCreateDTO,
    RatingOutputDTO,
)


class ManageOrderUseCase:
    def __init__(
        self,
        order_repository: AbstractOrderRepository,
        shop_repository: Optional[AbstractShopRepository] = None,
    ):
        self.order_repository = order_repository
        self.shop_repository = shop_repository

    async def create_clothing_request(
        self, dto: ClothingRequestCreateDTO, target_shop_ids: Optional[List[int]] = None
    ) -> ClothingRequestOutputDTO:
        meas_entity = None
        if dto.measurement:
            meas_entity = Measurement(
                chest=dto.measurement.chest,
                waist=dto.measurement.waist,
                shoulder=dto.measurement.shoulder,
                sleeve=dto.measurement.sleeve,
                neck=dto.measurement.neck,
                hip=dto.measurement.hip,
                inseam=dto.measurement.inseam,
                length=dto.measurement.length,
                notes=dto.measurement.notes,
            )

        req_entity = ClothingRequest(
            client_id=dto.client_id,
            target_date=dto.target_date,
            target_budget=dto.target_budget,
            clothing_category=dto.clothing_category,
            gender=dto.gender,
            fabric_status=dto.fabric_status,
            description=dto.description,
            voice_note_url=dto.voice_note_url,
            service_type=dto.service_type,
            request_location=dto.request_location,
            measurement=meas_entity,
        )

        saved_req = await self.order_repository.create_clothing_request(req_entity)

        # Persist design inspiration images (URLs only — files already in cloud storage)
        if dto.design_image_urls:
            for url in dto.design_image_urls:
                img = ClothingRequestImage(request_id=saved_req.request_id, image_url=url)  # type: ignore
                await self.order_repository.add_design_image(img)

        # Broadcast/Directly target shops by creating shop_requests
        if target_shop_ids:
            for shop_id in target_shop_ids:
                shop_req = ShopRequest(request_id=saved_req.request_id, shop_id=shop_id)  # type: ignore
                await self.order_repository.create_shop_request(shop_req)

        refetched = await self.order_repository.get_clothing_request(saved_req.request_id)  # type: ignore
        return self._to_clothing_request_dto(refetched or saved_req)

    async def submit_bid(self, dto: BidCreateDTO) -> BidDTO:
        sr = await self.order_repository.get_shop_request(dto.shop_request_id)
        if not sr:
            raise ShopRequestNotFoundError(dto.shop_request_id)

        bid = Bid(
            shop_request_id=dto.shop_request_id,
            bid_amount=dto.bid_amount,
            message=dto.message,
        )
        saved_bid = await self.order_repository.create_bid(bid)
        return BidDTO(
            bid_id=saved_bid.bid_id,
            shop_request_id=saved_bid.shop_request_id,
            bid_amount=saved_bid.bid_amount,
            message=saved_bid.message,
            created_at=saved_bid.created_at,
        )

    async def accept_bid_and_create_order(self, dto: OrderCreateDTO) -> OrderOutputDTO:
        sr = await self.order_repository.get_shop_request(dto.shop_request_id)
        if not sr:
            raise ShopRequestNotFoundError(dto.shop_request_id)

        order = Order(
            shop_request_id=dto.shop_request_id,
            accepted_price=dto.accepted_price,
            order_status=OrderStatusEnum.IN_PROGRESS,
        )
        saved_order = await self.order_repository.create_order(order)
        return self._to_order_dto(saved_order)

    async def update_order_status(self, order_id: int, new_status: str) -> OrderOutputDTO:
        order = await self.order_repository.get_order(order_id)
        if not order:
            raise OrderNotFoundError(order_id)

        updated = await self.order_repository.update_order_status(order_id, new_status)
        return self._to_order_dto(updated)

    async def process_mock_payment(self, dto: MockPaymentDTO) -> PaymentOutputDTO:
        order = await self.order_repository.get_order(dto.order_id)
        if not order:
            raise OrderNotFoundError(dto.order_id)

        payment = Payment(
            order_id=dto.order_id,
            amount=dto.amount,
            payment_method=dto.payment_method,
            payment_status=PaymentStatusEnum.PAID,
            payment_date=datetime.now(timezone.utc),
        )
        saved_payment = await self.order_repository.create_payment(payment)
        return PaymentOutputDTO(
            payment_id=saved_payment.payment_id,  # type: ignore
            order_id=saved_payment.order_id,
            amount=saved_payment.amount,
            payment_method=saved_payment.payment_method,
            payment_status=saved_payment.payment_status,
            payment_date=saved_payment.payment_date,
        )

    async def submit_rating(self, dto: RatingCreateDTO) -> RatingOutputDTO:
        order = await self.order_repository.get_order(dto.order_id)
        if not order:
            raise OrderNotFoundError(dto.order_id)

        rating = Rating(
            order_id=dto.order_id,
            client_id=dto.client_id,
            shop_id=dto.shop_id,
            rating=dto.rating,
            review=dto.review,
        )
        saved_rating = await self.order_repository.create_rating(rating)

        # Update average rating of shop if repository is available
        if self.shop_repository:
            pass  # TODO: recalculate average from all ratings for this shop

        return RatingOutputDTO(
            rating_id=saved_rating.rating_id,  # type: ignore
            order_id=saved_rating.order_id,
            client_id=saved_rating.client_id,
            shop_id=saved_rating.shop_id,
            rating=saved_rating.rating,
            review=saved_rating.review,
            created_at=saved_rating.created_at,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _to_clothing_request_dto(self, req: ClothingRequest) -> ClothingRequestOutputDTO:
        meas_dto = None
        if req.measurement:
            meas_dto = MeasurementDTO(
                chest=req.measurement.chest,
                waist=req.measurement.waist,
                shoulder=req.measurement.shoulder,
                sleeve=req.measurement.sleeve,
                neck=req.measurement.neck,
                hip=req.measurement.hip,
                inseam=req.measurement.inseam,
                length=req.measurement.length,
                notes=req.measurement.notes,
            )
        return ClothingRequestOutputDTO(
            request_id=req.request_id,  # type: ignore
            client_id=req.client_id,
            target_date=req.target_date,
            target_budget=req.target_budget,
            clothing_category=req.clothing_category,
            gender=req.gender,
            fabric_status=req.fabric_status,
            description=req.description,
            voice_note_url=req.voice_note_url,
            service_type=req.service_type,
            request_location=req.request_location,
            status=req.status,
            measurement=meas_dto,
            design_images=[
                ClothingRequestImageDTO(
                    image_id=img.image_id,
                    request_id=img.request_id,
                    image_url=img.image_url,
                    created_at=img.created_at,
                )
                for img in req.design_images
            ],
            shop_requests=[
                ShopRequestDTO(
                    shop_request_id=sr.shop_request_id,  # type: ignore
                    request_id=sr.request_id,
                    shop_id=sr.shop_id,
                    offered_price=sr.offered_price,
                    status=sr.status,
                    bids=[
                        BidDTO(
                            bid_id=b.bid_id,
                            shop_request_id=b.shop_request_id,
                            bid_amount=b.bid_amount,
                            message=b.message,
                            created_at=b.created_at,
                        )
                        for b in sr.bids
                    ],
                )
                for sr in req.shop_requests
            ],
            created_at=req.created_at,
            updated_at=req.updated_at,
        )

    def _to_order_dto(self, order: Order) -> OrderOutputDTO:
        return OrderOutputDTO(
            order_id=order.order_id,  # type: ignore
            shop_request_id=order.shop_request_id,
            order_status=order.order_status,
            accepted_price=order.accepted_price,
            started_date=order.started_date,
            completed_date=order.completed_date,
            created_at=order.created_at,
        )
