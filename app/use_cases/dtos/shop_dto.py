from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class ShopImageDTO:
    image_id: Optional[int]
    shop_id: int
    image_url: str


@dataclass
class ShopCreateDTO:
    seller_id: str
    shop_name: str
    shop_bio: Optional[str] = None
    shop_address: Optional[str] = None
    city: Optional[str] = None
    contact_number: Optional[str] = None
    registration_number: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class ShopOutputDTO:
    shop_id: int
    seller_id: str
    shop_name: str
    shop_bio: Optional[str] = None
    shop_address: Optional[str] = None
    city: Optional[str] = None
    contact_number: Optional[str] = None
    registration_number: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    average_rating: float = 0.0
    images: List[ShopImageDTO] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
