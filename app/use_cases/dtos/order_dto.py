from dataclasses import dataclass, field
from datetime import date, datetime

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


@dataclass
class MeasurementDTO:
    chest: float | None = None
    waist: float | None = None
    shoulder: float | None = None
    sleeve: float | None = None
    neck: float | None = None
    hip: float | None = None
    inseam: float | None = None
    length: float | None = None
    notes: str | None = None


@dataclass
class ClothingRequestImageDTO:
    """Carries the cloud-storage URL for a design inspiration image."""
    image_url: str
    image_id: int | None = None
    request_id: int | None = None
    created_at: datetime | None = None


@dataclass
class ClothingRequestCreateDTO:
    client_id: str
    target_date: date | None = None
    target_budget: float | None = None
    clothing_category: str | None = None
    gender: GenderEnum | None = None
    fabric_status: FabricStatusEnum | None = None
    description: str | None = None
    # NEW: Cloud-storage URL for voice instruction audio
    voice_note_url: str | None = None
    # NEW: Workflow preference — online or physical shop visit
    service_type: ServiceTypeEnum = ServiceTypeEnum.ONLINE
    request_location: str | None = None
    measurement: MeasurementDTO | None = None
    # NEW: Design inspiration image URLs (uploaded to cloud storage first)
    design_image_urls: list[str] = field(default_factory=list)


@dataclass
class BidDTO:
    bid_id: int | None
    request_id: int
    shop_id: int
    bid_amount: float
    message: str | None = None
    created_at: datetime | None = None


@dataclass
class ShopRequestDTO:
    shop_request_id: int
    request_id: int
    shop_id: int
    offered_price: float | None = None
    status: ShopRequestStatusEnum = ShopRequestStatusEnum.PENDING


@dataclass
class ClothingRequestOutputDTO:
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
    status: ClothingRequestStatusEnum = ClothingRequestStatusEnum.OPEN
    measurement: MeasurementDTO | None = None
    design_images: list[ClothingRequestImageDTO] = field(default_factory=list)
    shop_requests: list[ShopRequestDTO] = field(default_factory=list)
    bids: list[BidDTO] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class BidCreateDTO:
    request_id: int
    shop_id: int
    bid_amount: float
    message: str | None = None


@dataclass
class OrderCreateDTO:
    bid_id: int
    accepted_price: float


@dataclass
class OrderOutputDTO:
    order_id: int
    bid_id: int
    order_status: OrderStatusEnum
    accepted_price: float
    started_date: date | None = None
    completed_date: date | None = None
    created_at: datetime | None = None


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
    payment_method: PaymentMethodEnum | None
    payment_status: PaymentStatusEnum
    payment_date: datetime | None


@dataclass
class RatingCreateDTO:
    order_id: int
    client_id: str
    shop_id: int
    rating: int  # 1-5
    review: str | None = None


@dataclass
class RatingOutputDTO:
    rating_id: int
    order_id: int
    client_id: str
    shop_id: int
    rating: int
    review: str | None
    created_at: datetime | None
