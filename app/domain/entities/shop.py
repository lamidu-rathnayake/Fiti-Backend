from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Gig:
    shop_id: int
    title: str
    description: str
    price: float
    delivery_time: str | None = None
    category: str | None = None
    image_url: str | None = None
    gig_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ShopImage:
    shop_id: int
    image_url: str
    image_id: int | None = None
    created_at: datetime | None = None


@dataclass
class Shop:
    tailor_id: str  # Firebase Auth UID of the tailor who owns this shop
    shop_name: str
    shop_id: int | None = None
    specialty: str | None = None  # Tailor specialty (migrated from Firestore)
    shop_bio: str | None = None
    shop_address: str | None = None
    city: str | None = None
    contact_number: str | None = None
    registration_number: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    average_rating: float = 0.0
    images: list[ShopImage] = field(default_factory=list)
    gigs: list[Gig] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
