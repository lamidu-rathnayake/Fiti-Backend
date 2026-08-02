from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List
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


@dataclass
class MeasurementDTO:
    chest: Optional[float] = None
    waist: Optional[float] = None
    shoulder: Optional[float] = None
    sleeve: Optional[float] = None
    neck: Optional[float] = None
    hip: Optional[float] = None
    inseam: Optional[float] = None
    length: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class ClothingRequestImageDTO:
    """Carries the cloud-storage URL for a design inspiration image."""
    image_url: str
    image_id: Optional[int] = None
    request_id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class ClothingRequestCreateDTO:
    client_id: str
    target_date: Optional[date] = None
    target_budget: Optional[float] = None
    clothing_category: Optional[str] = None
    gender: Optional[GenderEnum] = None
    fabric_status: Optional[FabricStatusEnum] = None
    description: Optional[str] = None
    # NEW: Cloud-storage URL for voice instruction audio
    voice_note_url: Optional[str] = None
    # NEW: Workflow preference — online or physical shop visit
    service_type: ServiceTypeEnum = ServiceTypeEnum.ONLINE
    request_location: Optional[str] = None
    measurement: Optional[MeasurementDTO] = None
    # NEW: Design inspiration image URLs (uploaded to cloud storage first)
    design_image_urls: List[str] = field(default_factory=list)


@dataclass
class BidDTO:
    bid_id: Optional[int]
    shop_request_id: int
    bid_amount: float
    message: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class ShopRequestDTO:
    shop_request_id: int
    request_id: int
    shop_id: int
    offered_price: Optional[float] = None
    status: ShopRequestStatusEnum = ShopRequestStatusEnum.PENDING
    bids: List[BidDTO] = field(default_factory=list)


@dataclass
class ClothingRequestOutputDTO:
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
    status: ClothingRequestStatusEnum = ClothingRequestStatusEnum.OPEN
    measurement: Optional[MeasurementDTO] = None
    design_images: List[ClothingRequestImageDTO] = field(default_factory=list)
    shop_requests: List[ShopRequestDTO] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class BidCreateDTO:
    shop_request_id: int
    bid_amount: float
    message: Optional[str] = None


@dataclass
class OrderCreateDTO:
    shop_request_id: int
    accepted_price: float


@dataclass
class OrderOutputDTO:
    order_id: int
    shop_request_id: int
    order_status: OrderStatusEnum
    accepted_price: float
    started_date: Optional[date] = None
    completed_date: Optional[date] = None
    created_at: Optional[datetime] = None


@dataclass
class MockPaymentDTO:
    order_id: int
    amount: float
    payment_method: PaymentMethodEnum


@dataclass
class PaymentOutputDTO:
    payment_id: int
    order_id: int
    amount: float
    payment_method: Optional[PaymentMethodEnum]
    payment_status: PaymentStatusEnum
    payment_date: Optional[datetime]


@dataclass
class RatingCreateDTO:
    order_id: int
    client_id: str
    shop_id: int
    rating: int  # 1-5
    review: Optional[str] = None


@dataclass
class RatingOutputDTO:
    rating_id: int
    order_id: int
    client_id: str
    shop_id: int
    rating: int
    review: Optional[str]
    created_at: Optional[datetime]
