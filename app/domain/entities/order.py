from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional, List
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
    measurement_id: Optional[int] = None
    request_id: Optional[int] = None
    chest: Optional[float] = None
    waist: Optional[float] = None
    shoulder: Optional[float] = None
    sleeve: Optional[float] = None
    neck: Optional[float] = None
    hip: Optional[float] = None
    inseam: Optional[float] = None
    length: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ClothingRequestImage:
    """Design-inspiration image uploaded to cloud storage and linked to a request."""
    request_id: int
    image_url: str
    image_id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Bid:
    shop_request_id: int
    bid_amount: float
    bid_id: int = None
    message: str = None
    created_at: datetime = None


@dataclass
class ShopRequest:
    shop_id: int
    shop_request_id: int = None
    request_id: int = None
    offered_price: Optional[float] = None
    status: ShopRequestStatusEnum = ShopRequestStatusEnum.PENDING
    response_date: Optional[datetime] = None
    bids: List[Bid] = field(default_factory=list)
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class ClothingRequest:
    client_id: str
    request_id:int = None
    target_date: date = None
    target_budget: float = None
    clothing_category: Optional[str] = None
    gender: GenderEnum = None
    fabric_status: Optional[FabricStatusEnum] = None
    description: Optional[str] = None
    # NEW: URL stored after client uploads audio to cloud storage
    voice_note_url: Optional[str] = None
    # NEW: Online processing vs. physical shop visit toggle
    service_type: ServiceTypeEnum = ServiceTypeEnum.ONLINE
    request_location: Optional[str] = None
    status: ClothingRequestStatusEnum = ClothingRequestStatusEnum.OPEN
    measurement: Optional[Measurement] = None
    # NEW: Zero or more design-inspiration images
    design_images: List[ClothingRequestImage] = field(default_factory=list)
    shop_requests: List[ShopRequest] = field(default_factory=list)
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class Order:
    shop_request_id: int
    order_id: Optional[int] = None
    order_status: OrderStatusEnum = OrderStatusEnum.IN_PROGRESS
    accepted_price: float = 0.0
    started_date: Optional[date] = None
    completed_date: Optional[date] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class Payment:
    order_id: int
    amount: float
    payment_id: Optional[int] = None
    payment_method: Optional[PaymentMethodEnum] = None
    payment_status: PaymentStatusEnum = PaymentStatusEnum.PENDING
    payment_date: Optional[datetime] = None
    created_at: datetime = None


@dataclass
class Rating:
    order_id: int
    client_id: str
    shop_id: int
    rating: int  # 1 to 5
    rating_id: Optional[int] = None
    review: Optional[str] = None
    created_at: datetime = None
