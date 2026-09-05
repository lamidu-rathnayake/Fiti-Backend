from datetime import UTC, datetime

from app.domain.entities.order import (
    Bid,
    ClothingRequest,
    ClothingRequestImage,
    ClothingRequestStatusEnum,
    Measurement,
    Order,
    OrderStatusEnum,
    Payment,
    PaymentStatusEnum,
    Rating,
    ShopRequest,
    ShopRequestStatusEnum,
)
from app.domain.exceptions.order import (
    ClothingRequestNotFoundError,
    OrderNotFoundError,
)
from app.domain.repositories.order_repository import AbstractOrderRepository
from app.domain.repositories.shop_repository import AbstractShopRepository
from app.use_cases.dtos.order_dto import (
    BidCreateDTO,
    BidDTO,
    ClothingRequestCreateDTO,
    ClothingRequestImageDTO,
    ClothingRequestOutputDTO,
    MeasurementDTO,
    MockPaymentDTO,
    OrderCreateDTO,
    OrderOutputDTO,
    PaymentOutputDTO,
    RatingCreateDTO,
    RatingOutputDTO,
    ShopRequestDTO,
)


class ManageOrderUseCase:
    def __init__(
        self,
        order_repository: AbstractOrderRepository,
        shop_repository: AbstractShopRepository | None = None,
    ):
        self.order_repository = order_repository
        self.shop_repository = shop_repository

    async def create_clothing_request(
        self, dto: ClothingRequestCreateDTO, target_shop_ids: list[int] | None = None
    ) -> ClothingRequestOutputDTO:
        meas_entity = None

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
            measurement_profile_id=dto.measurement_profile_id,
        )

        saved_req = await self.order_repository.create_clothing_request(req_entity)

        # Persist design inspiration images (URLs only — files already in cloud storage)
        if dto.design_image_urls:
            for url in dto.design_image_urls:
                img = ClothingRequestImage(
                    request_id=saved_req.request_id, image_url=url
                )  # type: ignore
                await self.order_repository.add_design_image(img)

        # Resolve recipient shops:
        # 1. Direct explicit target shops if provided
        # 2. Nearby shops within radius if latitude/longitude are provided
        shops_to_target: set[int] = set(target_shop_ids or [])

        if (
            not shops_to_target
            and dto.latitude is not None
            and dto.longitude is not None
            and self.shop_repository is not None
        ):
            nearby_shops = await self.shop_repository.search_near_location(
                lat=dto.latitude,
                lng=dto.longitude,
                radius_km=dto.radius_km or 10.0,
            )
            shops_to_target.update(
                s.shop_id for s in nearby_shops if s.shop_id is not None
            )

        # Broadcast only to the resolved nearby / targeted shops
        for shop_id in shops_to_target:
            shop_req = ShopRequest(
                request_id=saved_req.request_id, shop_id=shop_id
            )  # type: ignore
            await self.order_repository.create_shop_request(shop_req)

        refetched = await self.order_repository.get_clothing_request(
            saved_req.request_id
        )  # type: ignore
        return self._to_clothing_request_dto(refetched or saved_req)

    async def _assert_shop_request_owner(
        self, shop_request_id: int, uid: str, owner_type: str
    ) -> ShopRequest:
        shop_request = await self.order_repository.get_shop_request(shop_request_id)
        if not shop_request:
            raise OrderNotFoundError(shop_request_id)

        if owner_type == "client":
            if not shop_request.clothing_request or shop_request.clothing_request.client_id != uid:
                raise PermissionError("You do not own this shop request.")
        elif owner_type == "tailor":
            if not self.shop_repository:
                raise PermissionError("Shop ownership could not be verified.")
            shop = await self.shop_repository.get_by_id(shop_request.shop_id)
            if not shop or shop.tailor_id != uid:
                raise PermissionError("You do not own this shop request's shop.")
        return shop_request

    async def get_clothing_request(self, request_id: int) -> ClothingRequestOutputDTO:
        req = await self.order_repository.get_clothing_request(request_id)
        if not req:
            raise ClothingRequestNotFoundError(request_id)
        return self._to_clothing_request_dto(req)

    async def list_clothing_requests_by_client(
        self, client_id: str, authenticated_uid: str | None = None
    ) -> list[ClothingRequestOutputDTO]:
        if authenticated_uid and client_id != authenticated_uid:
            raise PermissionError("You can only view your own requests.")
        requests = await self.order_repository.list_clothing_requests_by_client(
            client_id
        )
        return [self._to_clothing_request_dto(r) for r in requests]

    async def list_open_clothing_requests(
        self, skip: int = 0, limit: int = 100
    ) -> list[ClothingRequestOutputDTO]:
        requests = await self.order_repository.list_open_clothing_requests(
            skip=skip, limit=limit
        )
        return [self._to_clothing_request_dto(r) for r in requests]

    async def list_shop_requests_by_shop(self, shop_id: int) -> list[ShopRequestDTO]:
        return await self._list_shop_requests_by_shop(shop_id)

    async def _list_shop_requests_by_shop(
        self, shop_id: int, tailor_uid: str | None = None
    ) -> list[ShopRequestDTO]:
        if tailor_uid:
            if not self.shop_repository:
                raise PermissionError("Shop ownership could not be verified.")
            shop = await self.shop_repository.get_by_id(shop_id)
            if not shop or shop.tailor_id != tailor_uid:
                raise PermissionError("You do not own this shop.")
        shop_requests = await self.order_repository.list_shop_requests_by_shop(shop_id)
        return [
            ShopRequestDTO(
                shop_request_id=sr.shop_request_id,  # type: ignore
                request_id=sr.request_id,
                shop_id=sr.shop_id,
                offered_price=sr.offered_price,
                status=sr.status,
                clothing_request=(
                    self._to_clothing_request_dto(sr.clothing_request)
                    if sr.clothing_request
                    else None
                ),
            )
            for sr in shop_requests
        ]

    async def reject_shop_request(self, shop_request_id: int, client_uid: str | None = None) -> ShopRequestDTO:
        if client_uid:
            await self._assert_shop_request_owner(shop_request_id, client_uid, "client")
        updated = await self.order_repository.update_shop_request_status(
            shop_request_id, ShopRequestStatusEnum.REJECTED
        )
        if not updated:
            raise ValueError(f"ShopRequest {shop_request_id} not found")
            
        return ShopRequestDTO(
            shop_request_id=updated.shop_request_id,  # type: ignore
            request_id=updated.request_id,
            shop_id=updated.shop_id,
            offered_price=updated.offered_price,
            status=updated.status,
        )

    async def withdraw_shop_request(self, shop_request_id: int, tailor_uid: str) -> ShopRequestDTO:
        shop_request = await self._assert_shop_request_owner(
            shop_request_id, tailor_uid, "tailor"
        )
        updated = await self.order_repository.update_shop_request_status(
            shop_request_id, ShopRequestStatusEnum.WITHDRAWN
        )
        if not updated:
            raise ValueError(f"ShopRequest {shop_request_id} not found")

        return ShopRequestDTO(
            shop_request_id=updated.shop_request_id,  # type: ignore
            request_id=updated.request_id,
            shop_id=updated.shop_id,
            offered_price=updated.offered_price,
            status=updated.status,
        )

    async def submit_bid(self, dto: BidCreateDTO, tailor_uid: str | None = None) -> BidDTO:
        if tailor_uid:
            await self._assert_shop_request_owner(dto.shop_request_id, tailor_uid, "tailor")
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

    async def accept_bid_and_create_order(self, dto: OrderCreateDTO, client_uid: str | None = None) -> OrderOutputDTO:
        if client_uid:
            await self._assert_shop_request_owner(dto.shop_request_id, client_uid, "client")
        order = Order(
            shop_request_id=dto.shop_request_id,
            accepted_price=dto.accepted_price,
            order_status=OrderStatusEnum.IN_PROGRESS,
        )
        saved_order = await self.order_repository.create_order(order)
        return self._to_order_dto(saved_order)

    async def update_order_status(
        self, order_id: int, new_status: str, authenticated_uid: str | None = None
    ) -> OrderOutputDTO:
        order = await self.order_repository.get_order(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if authenticated_uid:
            await self._assert_order_owner(order, authenticated_uid)

        updated = await self.order_repository.update_order_status(order_id, new_status)
        return self._to_order_dto(updated)

    async def get_order(self, order_id: int, authenticated_uid: str | None = None) -> OrderOutputDTO:
        order = await self.order_repository.get_order(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if authenticated_uid:
            await self._assert_order_owner(order, authenticated_uid)
        return self._to_order_dto(order)

    async def _assert_order_owner(self, order: Order, uid: str) -> None:
        if order.clothing_request and order.clothing_request.client_id == uid:
            return
        shop_request = await self.order_repository.get_shop_request(order.shop_request_id)
        if shop_request and self.shop_repository:
            shop = await self.shop_repository.get_by_id(shop_request.shop_id)
            if shop and shop.tailor_id == uid:
                return
        raise PermissionError("You are not authorized to access this order.")

    async def list_orders_by_shop(self, shop_id: int, tailor_uid: str | None = None) -> list[OrderOutputDTO]:
        if tailor_uid:
            if not self.shop_repository:
                raise PermissionError("Shop ownership could not be verified.")
            shop = await self.shop_repository.get_by_id(shop_id)
            if not shop or shop.tailor_id != tailor_uid:
                raise PermissionError("You do not own this shop.")
        orders = await self.order_repository.list_orders_by_shop(shop_id)
        return [self._to_order_dto(o) for o in orders]

    async def list_orders_by_client(self, client_id: str, authenticated_uid: str | None = None) -> list[OrderOutputDTO]:
        if authenticated_uid and client_id != authenticated_uid:
            raise PermissionError("You can only view your own orders.")
        orders = await self.order_repository.list_orders_by_client(client_id)
        return [self._to_order_dto(o) for o in orders]

    async def process_mock_payment(self, dto: MockPaymentDTO, client_uid: str | None = None) -> PaymentOutputDTO:
        order = await self.order_repository.get_order(dto.order_id)
        if not order:
            raise OrderNotFoundError(dto.order_id)
        if client_uid:
            if not order.clothing_request or order.clothing_request.client_id != client_uid:
                raise PermissionError("You do not own this order.")

        payment = Payment(
            order_id=dto.order_id,
            amount=dto.amount or order.accepted_price,
            payment_method=dto.payment_method,
            payment_status=PaymentStatusEnum.PAID,
            payment_date=datetime.now(UTC),
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

    async def submit_rating(self, dto: RatingCreateDTO, client_uid: str | None = None) -> RatingOutputDTO:
        if client_uid and dto.client_id != client_uid:
            raise PermissionError("You can only submit ratings as yourself.")
        order = await self.order_repository.get_order(dto.order_id)
        if not order:
            raise OrderNotFoundError(dto.order_id)
        if client_uid and (not order.clothing_request or order.clothing_request.client_id != client_uid):
            raise PermissionError("You do not own this order.")

        rating = Rating(
            order_id=dto.order_id,
            client_id=dto.client_id,
            shop_id=dto.shop_id,
            rating=dto.rating,
            review=dto.review,
        )
        saved_rating = await self.order_repository.create_rating(rating)

        # Recalculate average rating for the shop
        if self.shop_repository:
            all_ratings = await self.order_repository.get_ratings_by_shop(dto.shop_id)
            if all_ratings:
                avg = sum(r.rating for r in all_ratings) / len(all_ratings)
                await self.shop_repository.update_average_rating(
                    dto.shop_id, round(avg, 2)
                )

        return RatingOutputDTO(
            rating_id=saved_rating.rating_id,  # type: ignore
            order_id=saved_rating.order_id,
            client_id=saved_rating.client_id,
            shop_id=saved_rating.shop_id,
            rating=saved_rating.rating,
            review=saved_rating.review,
            created_at=saved_rating.created_at,
        )

    async def cancel_clothing_request(
        self, request_id: int, client_id: str
    ) -> ClothingRequestOutputDTO:
        """Cancel an open clothing request. Only the owning client may cancel."""
        req = await self.order_repository.get_clothing_request(request_id)
        if not req:
            raise ClothingRequestNotFoundError(request_id)
        if req.client_id != client_id:
            raise PermissionError(
                f"Client '{client_id}' does not own request {request_id}."
            )
        if req.status != ClothingRequestStatusEnum.OPEN:
            raise ValueError(
                f"Only OPEN requests can be cancelled. Current status: {req.status.value}"
            )
        updated = await self.order_repository.cancel_clothing_request(request_id)
        return self._to_clothing_request_dto(updated or req)

    async def list_bids_by_shop_request(self, shop_request_id: int) -> list[BidDTO]:
        """Return all bids submitted for a specific shop request."""
        bids = await self.order_repository.list_bids_by_shop_request(shop_request_id)
        return [
            BidDTO(
                bid_id=b.bid_id,
                shop_request_id=b.shop_request_id,
                bid_amount=b.bid_amount,
                message=b.message,
                created_at=b.created_at,
            )
            for b in bids
        ]

    async def get_order_payment(self, order_id: int, authenticated_uid: str | None = None) -> PaymentOutputDTO | None:
        """Return the payment record for an order, or None if not yet paid."""
        order = await self.order_repository.get_order(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if authenticated_uid:
            await self._assert_order_owner(order, authenticated_uid)
        payment = await self.order_repository.get_payment_by_order(order_id)
        if not payment:
            return None
        return PaymentOutputDTO(
            payment_id=payment.payment_id,  # type: ignore
            order_id=payment.order_id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            payment_status=payment.payment_status,
            payment_date=payment.payment_date,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _to_clothing_request_dto(
        self, req: ClothingRequest
    ) -> ClothingRequestOutputDTO:
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
            measurement_profile_id=req.measurement_profile_id,
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
                )
                for sr in req.shop_requests
            ],
            bids=[
                BidDTO(
                    bid_id=b.bid_id,
                    shop_request_id=b.shop_request_id,
                    bid_amount=b.bid_amount,
                    message=b.message,
                    created_at=b.created_at,
                )
                for sr in req.shop_requests
                for b in sr.bids
            ],
            client=req.client,
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
            clothing_request=self._to_clothing_request_dto(order.clothing_request) if order.clothing_request else None,
            created_at=order.created_at,
        )