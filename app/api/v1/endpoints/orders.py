from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_manage_order_use_case
from app.api.schemas.order_schema import (
    ClothingRequestCreateRequest,
    ClothingRequestResponse,
    BidCreateRequest,
    BidResponse,
    OrderCreateRequest,
    OrderResponse,
    MockPaymentRequest,
    PaymentResponse,
    RatingCreateRequest,
    RatingResponse,
)
from app.domain.exceptions.order import (
    ClothingRequestNotFoundError,
    ShopRequestNotFoundError,
    OrderNotFoundError,
)
from app.use_cases.dtos.order_dto import (
    ClothingRequestCreateDTO,
    MeasurementDTO,
    BidCreateDTO,
    OrderCreateDTO,
    MockPaymentDTO,
    RatingCreateDTO,
)
from app.use_cases.order.manage_order import ManageOrderUseCase

router = APIRouter(prefix="/orders", tags=["Orders & Requests"])


@router.post("/requests", response_model=ClothingRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_clothing_request(
    request: ClothingRequestCreateRequest,
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    meas_dto = None
    if request.measurement:
        meas_dto = MeasurementDTO(
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
        measurement=meas_dto,
        design_image_urls=request.design_image_urls,
    )
    return await use_case.create_clothing_request(dto, target_shop_ids=request.target_shop_ids)


@router.post("/bids", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
async def submit_bid(
    request: BidCreateRequest,
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    try:
        dto = BidCreateDTO(
            shop_request_id=request.shop_request_id,
            bid_amount=request.bid_amount,
            message=request.message,
        )
        return await use_case.submit_bid(dto)
    except ShopRequestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/accept-bid", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def accept_bid_and_create_order(
    request: OrderCreateRequest,
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    try:
        dto = OrderCreateDTO(
            shop_request_id=request.shop_request_id,
            accepted_price=request.accepted_price,
        )
        return await use_case.accept_bid_and_create_order(dto)
    except ShopRequestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    order_status: str,
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    try:
        return await use_case.update_order_status(order_id, order_status)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/payments/mock", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_mock_payment(
    request: MockPaymentRequest,
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    try:
        dto = MockPaymentDTO(
            order_id=request.order_id,
            amount=request.amount,
            payment_method=request.payment_method,
        )
        return await use_case.process_mock_payment(dto)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/ratings", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def submit_rating(
    request: RatingCreateRequest,
    use_case: ManageOrderUseCase = Depends(get_manage_order_use_case),
):
    try:
        dto = RatingCreateDTO(
            order_id=request.order_id,
            client_id=request.client_id,
            shop_id=request.shop_id,
            rating=request.rating,
            review=request.review,
        )
        return await use_case.submit_rating(dto)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
