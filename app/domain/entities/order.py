from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum

from app.domain.entities.user import GenderEnum


class FabricStatusEnum(str, Enum):
    CLIENT_PROVIDED = "client_provided"
    SHOP_PROVIDES = "shop_provides"


class ServiceTypeEnum(str, Enum):
    """Operational toggle: client chooses between online processing or
    physically visiting the tailor's shop."""

    ONLINE = "online"
    PHYSICAL_VISIT = "physical_visit"


class ClothingRequestStatusEnum(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ClothingRequestTypeEnum(str, Enum):
    DIRECT = "direct"
    BIDDING = "bidding"


class ShopRequestStatusEnum(str, Enum):
    PENDING = "pending"
    QUOTED = "quoted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class OrderStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentMethodEnum(str, Enum):
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_WALLET = "mobile_wallet"


class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class Measurement:
    """Per-request body measurements attached to a ClothingRequest."""

    measurement_id: int | None = None
    request_id: int | None = None
    chest: float | None = None
    waist: float | None = None
    shoulder: float | None = None
    sleeve: float | None = None
    neck: float | None = None
    hip: float | None = None
    inseam: float | None = None
    length: float | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ClothingRequestImage:
    """Design-inspiration image uploaded to cloud storage and linked to a request."""

    request_id: int
    image_url: str
    image_id: int | None = None
    created_at: datetime | None = None


@dataclass
class Bid:
    shop_request_id: int
    bid_amount: float
    bid_id: int | None = None
    message: str | None = None
    created_at: datetime | None = None


@dataclass
class ShopRequest:
    shop_id: int
    shop_request_id: int | None = None
    request_id: int | None = None
    offered_price: float | None = None
    status: ShopRequestStatusEnum = ShopRequestStatusEnum.PENDING
    response_date: datetime | None = None
    bids: list[Bid] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ClothingRequest:
    client_id: str
    request_id: int | None = None
    target_date: date | None = None
    target_budget: float | None = None
    clothing_category: str | None = None
    gender: GenderEnum | None = None
    fabric_status: FabricStatusEnum | None = None
    description: str | None = None
    # NEW: URL stored after client uploads audio to cloud storage
    voice_note_url: str | None = None
    # NEW: Online processing vs. physical shop visit toggle
    service_type: ServiceTypeEnum = ServiceTypeEnum.ONLINE
    # NEW: Request type (direct or bidding)
    request_type: ClothingRequestTypeEnum = ClothingRequestTypeEnum.DIRECT
    request_location: str | None = None
    status: ClothingRequestStatusEnum = ClothingRequestStatusEnum.OPEN
    measurement: Measurement | None = None
    # NEW: Zero or more design-inspiration images
    design_images: list[ClothingRequestImage] = field(default_factory=list)
    shop_requests: list[ShopRequest] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Order:
    shop_request_id: int
    order_id: int | None = None
    order_status: OrderStatusEnum = OrderStatusEnum.IN_PROGRESS
    accepted_price: float = 0.0
    started_date: date | None = None
    completed_date: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Payment:
    order_id: int
    amount: float
    payment_id: int | None = None
    payment_method: PaymentMethodEnum | None = None
    payment_status: PaymentStatusEnum = PaymentStatusEnum.PENDING
    payment_date: datetime | None = None
    created_at: datetime | None = None


@dataclass
class Rating:
    order_id: int
    client_id: str
    shop_id: int
    rating: int  # 1 to 5
    rating_id: int | None = None
    review: str | None = None
    created_at: datetime | None = None
