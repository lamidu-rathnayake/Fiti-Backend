from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.domain.entities.user import GenderEnum
from app.domain.entities.order import (
    FabricStatusEnum,
    ServiceTypeEnum,
    ClothingRequestStatusEnum,
    ShopRequestStatusEnum,
    OrderStatusEnum,
    PaymentMethodEnum,
    PaymentStatusEnum,
)
from app.api.schemas.user_schema import MeasurementProfileRequest


class ClothingRequestImageResponse(BaseModel):
    """Design inspiration image linked to a clothing request."""
    image_id: Optional[int] = None
    request_id: Optional[int] = None
    image_url: str
    created_at: Optional[datetime] = None


class ClothingRequestCreateRequest(BaseModel):
    client_id: str = Field(..., description="Firebase Auth UID of Client")
    target_date: Optional[date] = None
    target_budget: Optional[float] = None
    clothing_category: Optional[str] = None
    gender: Optional[GenderEnum] = None
    fabric_status: Optional[FabricStatusEnum] = None
    description: Optional[str] = None
    # NEW: Cloud-storage URL for voice-note audio (upload to Firebase Storage first)
    voice_note_url: Optional[str] = Field(None, description="Cloud-storage URL for voice instruction audio")
    # NEW: Workflow toggle — 'online' or 'physical_visit'
    service_type: ServiceTypeEnum = Field(ServiceTypeEnum.ONLINE, description="Online or physical-visit workflow")
    request_location: Optional[str] = None
    measurement: Optional[MeasurementProfileRequest] = None
    # NEW: Cloud-storage URLs for design inspiration screenshots
    design_image_urls: List[str] = Field(default_factory=list, description="Cloud-storage URLs for design inspiration images")
    target_shop_ids: Optional[List[int]] = Field(None, description="Optional list of specific Shop IDs to invite")


class BidCreateRequest(BaseModel):
    shop_request_id: int
    bid_amount: float = Field(..., gt=0)
    message: Optional[str] = None


class OrderCreateRequest(BaseModel):
    shop_request_id: int
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
    review: Optional[str] = None


class BidResponse(BaseModel):
    bid_id: Optional[int]
    shop_request_id: int
    bid_amount: float
    message: Optional[str] = None
    created_at: Optional[datetime] = None


class ShopRequestResponse(BaseModel):
    shop_request_id: int
    request_id: int
    shop_id: int
    offered_price: Optional[float] = None
    status: ShopRequestStatusEnum
    bids: List[BidResponse] = []


class ClothingRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: int
    client_id: str
    target_date: Optional[date] = None
    target_budget: Optional[float] = None
    clothing_category: Optional[str] = None
    gender: Optional[GenderEnum] = None
    fabric_status: Optional[FabricStatusEnum] = None
    description: Optional[str] = None
    voice_note_url: Optional[str] = None
    service_type: ServiceTypeEnum = ServiceTypeEnum.ONLINE
    request_location: Optional[str] = None
    status: ClothingRequestStatusEnum
    measurement: Optional[MeasurementProfileRequest] = None
    design_images: List[ClothingRequestImageResponse] = []
    shop_requests: List[ShopRequestResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    shop_request_id: int
    order_status: OrderStatusEnum
    accepted_price: float
    started_date: Optional[date] = None
    completed_date: Optional[date] = None
    created_at: Optional[datetime] = None


class PaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    amount: float
    payment_method: Optional[PaymentMethodEnum]
    payment_status: PaymentStatusEnum
    payment_date: Optional[datetime]


class RatingResponse(BaseModel):
    rating_id: int
    order_id: int
    client_id: str
    shop_id: int
    rating: int
    review: Optional[str] = None
    created_at: Optional[datetime] = None
