from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ShopImageDTO:
    image_id: int | None
    shop_id: int
    image_url: str


@dataclass
class ShopCreateDTO:
    tailor_id: str
    shop_name: str
    specialty: str | None = None  # Migrated from Firestore
    shop_bio: str | None = None
    shop_address: str | None = None
    city: str | None = None
    contact_number: str | None = None
    registration_number: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass
class ShopUpdateDTO:
    shop_id: int
    shop_name: str
    specialty: str | None = None  # Migrated from Firestore
    shop_bio: str | None = None
    shop_address: str | None = None
    city: str | None = None
    contact_number: str | None = None
    registration_number: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass
class ShopOutputDTO:
    shop_id: int
    tailor_id: str
    shop_name: str
    specialty: str | None = None
    shop_bio: str | None = None
    shop_address: str | None = None
    city: str | None = None
    contact_number: str | None = None
    registration_number: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    average_rating: float = 0.0
    images: list[ShopImageDTO] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
