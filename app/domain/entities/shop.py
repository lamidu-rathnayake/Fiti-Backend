from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ShopImage:
    shop_id: int
    image_url: str
    image_id: int | None = None
    created_at: datetime = None


@dataclass
class Shop:
    seller_id: str
    shop_name: str
    shop_id:int = None
    shop_bio: str | None = None
    shop_address: str= None
    city: str = None
    contact_number: str = None
    registration_number: str | None = None
    latitude: float = None
    longitude: float = None
    average_rating: float = 0.0
    images: list[ShopImage] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
