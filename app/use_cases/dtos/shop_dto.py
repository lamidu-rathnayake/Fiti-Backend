from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GigDTO:
    gig_id: int | None
    shop_id: int
    title: str
    description: str
    price: float
    delivery_time: str | None = None
    category: str | None = None
    image_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ShopWorkDTO:
    work_id: int | None
    shop_id: int
    image_url: str
    description: str | None = None


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
    profile_image_url: str | None = None


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
    profile_image_url: str | None = None


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
    profile_image_url: str | None = None
    average_rating: float = 0.0
    works: list[ShopWorkDTO] = field(default_factory=list)
    gigs: list[GigDTO] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
