from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ShopImageSchema(BaseModel):
    image_id: Optional[int] = None
    shop_id: int
    image_url: str


class ShopCreateRequest(BaseModel):
    seller_id: str = Field(..., description="Firebase UID of seller")
    shop_name: str = Field(..., min_length=2, max_length=150)
    shop_bio: Optional[str] = None
    shop_address: Optional[str] = None
    city: Optional[str] = None
    contact_number: Optional[str] = None
    registration_number: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ShopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    images: List[ShopImageSchema] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
