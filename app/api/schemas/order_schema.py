from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.api.schemas.user_schema import MeasurementProfileRequest
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


class ClothingRequestImageResponse(BaseModel):
    """Design inspiration image linked to a clothing request."""
    image_id: int | None = None
    request_id: int | None = None
    image_url: str
    created_at: datetime | None = None


class ClothingRequestCreateRequest(BaseModel):
    client_id: str = Field(..., description="Firebase Auth UID of Client")
    target_date: date | None = None
    target_budget: float | None = None
    clothing_category: str | None = None
    gender: GenderEnum | None = None
    fabric_status: FabricStatusEnum | None = None
    description: str | None = None
    # NEW: Cloud-storage URL for voice-note audio (upload to Firebase Storage first)
    voice_note_url: str | None = Field(None, description="Cloud-storage URL for voice instruction audio")
    # NEW: Workflow toggle — 'online' or 'physical_visit'
    service_type: ServiceTypeEnum = Field(ServiceTypeEnum.ONLINE, description="Online or physical-visit workflow")
    request_location: str | None = None
    measurement: MeasurementProfileRequest | None = None
    # NEW: Cloud-storage URLs for design inspiration screenshots
    design_image_urls: list[str] = Field(default_factory=list, description="Cloud-storage URLs for design inspiration images")
    target_shop_ids: list[int] | None = Field(None, description="Optional list of specific Shop IDs to invite")


class BidCreateRequest(BaseModel):
    request_id: int
    shop_id: int
    bid_amount: float = Field(..., gt=0)
    message: str | None = None


class OrderCreateRequest(BaseModel):
    bid_id: int
    accepted_price: float = Field(..., gt=0)


class MockPaymentRequest(BaseModel):
    order_id: int
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethodEnum = PaymentMethodEnum.CARD


class RatingCreateRequest(BaseModel):
    order_id: int
    client_id: str
    shop_id: int
    rating: int = Field(..., ge=1, le=5)
    review: str | None = None


class BidResponse(BaseModel):
    bid_id: int | None
    request_id: int
    shop_id: int
    bid_amount: float
    message: str | None = None
    created_at: datetime | None = None


class ShopRequestResponse(BaseModel):
    shop_request_id: int
    request_id: int
    shop_id: int
    offered_price: float | None = None
    status: ShopRequestStatusEnum


class ClothingRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: int
    client_id: str
    target_date: date | None = None
    target_budget: float | None = None
    clothing_category: str | None = None
    gender: GenderEnum | None = None
    fabric_status: FabricStatusEnum | None = None
    description: str | None = None
    voice_note_url: str | None = None
    service_type: ServiceTypeEnum = ServiceTypeEnum.ONLINE
    request_location: str | None = None
    status: ClothingRequestStatusEnum
    measurement: MeasurementProfileRequest | None = None
    design_images: list[ClothingRequestImageResponse] = []
    shop_requests: list[ShopRequestResponse] = []
    bids: list[BidResponse] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    bid_id: int
    order_status: OrderStatusEnum
    accepted_price: float
    started_date: date | None = None
    completed_date: date | None = None
    created_at: datetime | None = None


class PaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    payment_method: PaymentMethodEnum | None
    payment_status: PaymentStatusEnum
    payment_date: datetime | None


class RatingResponse(BaseModel):
    rating_id: int
    order_id: int
    client_id: str
    shop_id: int
    rating: int
    review: str | None = None
    created_at: datetime | None = None
