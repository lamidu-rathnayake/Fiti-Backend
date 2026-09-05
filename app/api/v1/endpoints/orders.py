from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_manage_order_use_case
from app.api.schemas.order_schema import (
    BidCreateRequest,
    BidResponse,
    ClothingRequestCreateRequest,
    ClothingRequestResponse,
    MockPaymentRequest,
    OrderCreateRequest,
    OrderResponse,
    PaymentResponse,
    RatingCreateRequest,
    RatingResponse,
    ShopRequestResponse,
)
from app.core.security import get_current_user_uid, require_role
from app.domain.exceptions.order import (
    ClothingRequestNotFoundError,
    OrderNotFoundError,
)
from app.use_cases.dtos.order_dto import (
    BidCreateDTO,
    ClothingRequestCreateDTO,
    MeasurementDTO,
    MockPaymentDTO,
    OrderCreateDTO,
    RatingCreateDTO,
)
from app.use_cases.order.manage_order import ManageOrderUseCase

router = APIRouter(prefix="/orders", tags=["Orders & Requests"])


# ── Clothing Requests ──────────────────────────────────────────────────
# IMPORTANT: Static routes (open, client/{id}) MUST be declared before
# the wildcard /{request_id} route, otherwise FastAPI will try to parse
# string path segments as integers and return 422.


@router.get("/requests/open", response_model=list[ClothingRequestResponse])
async def list_open_clothing_requests(
    skip: int = 0,
    limit: int = 100,
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """List all open clothing requests (marketplace view for tailors). Declared before /{request_id}."""
    return await use_case.list_open_clothing_requests(skip=skip, limit=limit)


@router.get(
    "/requests/client/{client_id}", response_model=list[ClothingRequestResponse]
)
async def list_clothing_requests_by_client(
    client_id: str,
    authenticated_uid: str = Depends(require_role("client")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """List all clothing requests for a specific client. Declared before /{request_id}."""
    if client_id != authenticated_uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own requests.")
    return await use_case.list_clothing_requests_by_client(client_id, authenticated_uid)


@router.post(
    "/requests",
    response_model=ClothingRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_clothing_request(
    request: ClothingRequestCreateRequest,
    authenticated_uid: str = Depends(require_role("client")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Submit a new clothing request. Requires client role."""
    if request.client_id != authenticated_uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only create requests for yourself.")

    dto = ClothingRequestCreateDTO(
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
        latitude=request.latitude,
        longitude=request.longitude,
        radius_km=request.radius_km,
        measurement=(
            MeasurementDTO(**request.measurement.model_dump())
            if request.measurement
            else None
        ),
        measurement_profile_id=request.measurement_profile_id,
        design_image_urls=request.design_image_urls,
        request_type=request.request_type,
    )
    return await use_case.create_clothing_request(
        dto, target_shop_ids=request.target_shop_ids
    )


@router.get("/requests/{request_id}", response_model=ClothingRequestResponse)
async def get_clothing_request(
    request_id: int,
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Get a specific clothing request by ID."""
    try:
        return await use_case.get_clothing_request(request_id)
    except ClothingRequestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/requests/{request_id}/cancel", response_model=ClothingRequestResponse)
async def cancel_clothing_request(
    request_id: int,
    authenticated_uid: str = Depends(require_role("client")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Cancel an open clothing request. Requires client role and must be the request owner."""
    try:
        return await use_case.cancel_clothing_request(request_id, authenticated_uid)
    except ClothingRequestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ── Shop Requests ──────────────────────────────────────────────────────


@router.get("/shop-requests/shop/{shop_id}", response_model=list[ShopRequestResponse])
async def list_shop_requests_by_shop(
    shop_id: int,
    authenticated_uid: str = Depends(require_role("tailor")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """List all shop requests assigned to a specific shop."""
    return await use_case._list_shop_requests_by_shop(shop_id, authenticated_uid)


@router.patch("/shop-requests/{shop_request_id}/reject", response_model=ShopRequestResponse)
async def reject_shop_request(
    shop_request_id: int,
    authenticated_uid: str = Depends(require_role("client")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Reject a tailor's quote. Requires client role."""
    try:
        return await use_case.reject_shop_request(shop_request_id, authenticated_uid)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.patch("/shop-requests/{shop_request_id}/withdraw", response_model=ShopRequestResponse)
async def withdraw_shop_request(
    shop_request_id: int,
    authenticated_uid: str = Depends(require_role("tailor")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Withdraw a pending shop request. Requires tailor role."""
    try:
        return await use_case.withdraw_shop_request(shop_request_id, authenticated_uid)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/shop-requests/{shop_request_id}/bids", response_model=list[BidResponse])
async def list_bids_by_shop_request(
    shop_request_id: int,
    authenticated_uid: str = Depends(require_role("tailor")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """List all bids on a specific shop request. Requires tailor role."""
    return await use_case.list_bids_by_shop_request(shop_request_id)


# ── Bids ───────────────────────────────────────────────────────────────


@router.post("/bids", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def submit_bid(
    request: BidCreateRequest,
    authenticated_uid: str = Depends(require_role("tailor")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Submit a bid on a shop request. Requires tailor role."""
    try:
        dto = BidCreateDTO(
            shop_request_id=request.shop_request_id,
            bid_amount=request.bid_amount,
            message=request.message,
        )
        return await use_case.submit_bid(dto, authenticated_uid)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# ── Orders ─────────────────────────────────────────────────────────────
# Static paths (shop/{id}, client/{id}) MUST be before /{order_id}


@router.get("/shop/{shop_id}", response_model=list[OrderResponse])
async def list_orders_by_shop(
    shop_id: int,
    authenticated_uid: str = Depends(require_role("tailor")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """List all orders for a specific shop. Declared before /{order_id}."""
    return await use_case.list_orders_by_shop(shop_id, authenticated_uid)


@router.get("/client/{client_id}", response_model=list[OrderResponse])
async def list_orders_by_client(
    client_id: str,
    authenticated_uid: str = Depends(require_role("client")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """List all orders for a specific client. Declared before /{order_id}."""
    return await use_case.list_orders_by_client(client_id, authenticated_uid)


@router.post(
    "/accept-bid", response_model=OrderResponse, status_code=status.HTTP_201_CREATED
)
async def accept_bid_and_create_order(
    request: OrderCreateRequest,
    authenticated_uid: str = Depends(require_role("client")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Accept a bid and create an order. Requires client role."""
    try:
        dto = OrderCreateDTO(
            shop_request_id=request.shop_request_id,
            accepted_price=request.accepted_price,
        )
        return await use_case.accept_bid_and_create_order(dto, authenticated_uid)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    authenticated_uid: str = Depends(get_current_user_uid),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Get a specific order by ID."""
    try:
        return await use_case.get_order(order_id, authenticated_uid)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    order_status: str,
    authenticated_uid: str = Depends(get_current_user_uid),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Update order status."""
    try:
        return await use_case.update_order_status(order_id, order_status, authenticated_uid)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


# ── Payments ───────────────────────────────────────────────────────────


@router.get("/{order_id}/payment", response_model=PaymentResponse | None)
async def get_order_payment(
    order_id: int,
    authenticated_uid: str = Depends(get_current_user_uid),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Get payment status for an order. Returns null if not yet paid."""
    try:
        return await use_case.get_order_payment(order_id, authenticated_uid)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.post(
    "/payments/mock",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def process_mock_payment(
    request: MockPaymentRequest,
    authenticated_uid: str = Depends(require_role("client")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Process a mock payment for an order. Requires client role."""
    try:
        dto = MockPaymentDTO(
            order_id=request.order_id,
            amount=request.amount,
            payment_method=request.payment_method,
        )
        return await use_case.process_mock_payment(dto, authenticated_uid)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


# ── Ratings ────────────────────────────────────────────────────


@router.post(
    "/ratings", response_model=RatingResponse, status_code=status.HTTP_201_CREATED
)
async def submit_rating(
    request: RatingCreateRequest,
    authenticated_uid: str = Depends(require_role("client")),
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    """Submit a rating for a completed order. Requires client role."""
    try:
        dto = RatingCreateDTO(
            order_id=request.order_id,
            client_id=request.client_id,
            shop_id=request.shop_id,
            rating=request.rating,
            review=request.review,
        )
        return await use_case.submit_rating(dto, authenticated_uid)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))