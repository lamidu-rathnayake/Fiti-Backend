from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ShopImageSchema(BaseModel):
    image_id: int | None = None
    shop_id: int
    image_url: str


class ShopCreateRequest(BaseModel):
    tailor_id: str = Field(
        ..., description="Firebase UID of the tailor who owns this shop"
    )
    shop_name: str = Field(..., min_length=2, max_length=150)
    shop_bio: str | None = None
    shop_address: str | None = None
    city: str | None = None
    contact_number: str | None = None
    registration_number: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class ShopUpdateRequest(BaseModel):
    shop_name: str = Field(..., min_length=2, max_length=150)
    shop_bio: str | None = None
    shop_address: str | None = None
    city: str | None = None
    contact_number: str | None = None
    registration_number: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class ShopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    shop_id: int
    tailor_id: str
    shop_name: str
    shop_bio: str | None = None
    shop_address: str | None = None
    city: str | None = None
    contact_number: str | None = None
    registration_number: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    average_rating: float = 0.0
    images: list[ShopImageSchema] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None
