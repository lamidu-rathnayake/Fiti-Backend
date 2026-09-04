from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ShopImageSchema(BaseModel):
    image_id: int | None = None
    shop_id: int
    image_url: str


class ShopImageCreateRequest(BaseModel):
    image_url: str = Field(..., pattern=r"^https?://", min_length=1, max_length=2048)


class GigCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: str = Field(..., min_length=5, max_length=2000)
    price: float = Field(..., gt=0)
    delivery_time: str | None = Field(None, max_length=100)
    category: str | None = Field(None, max_length=100)
    image_url: str | None = Field(None, pattern=r"^https?://", max_length=2048)


class GigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gig_id: int
    shop_id: int
    title: str
    description: str
    price: float
    delivery_time: str | None = None
    category: str | None = None
    image_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ShopCreateRequest(BaseModel):
    shop_name: str = Field(..., min_length=2, max_length=150)
    specialty: str | None = Field(None, min_length=2, max_length=100)
    shop_bio: str | None = Field(None, max_length=1000)
    shop_address: str | None = Field(None, min_length=5, max_length=255)
    city: str | None = Field(None, min_length=2, max_length=100)
    contact_number: str | None = Field(None, pattern=r"^(?:\+94|0)[0-9]{9}$")
    registration_number: str | None = Field(None, min_length=2, max_length=50)
    latitude: float | None = Field(None, ge=5.0, le=10.0)
    longitude: float | None = Field(None, ge=79.0, le=82.0)


class ShopUpdateRequest(BaseModel):
    shop_name: str = Field(..., min_length=2, max_length=150)
    specialty: str | None = Field(None, min_length=2, max_length=100)
    shop_bio: str | None = Field(None, max_length=1000)
    shop_address: str | None = Field(None, min_length=5, max_length=255)
    city: str | None = Field(None, min_length=2, max_length=100)
    contact_number: str | None = Field(None, pattern=r"^(?:\+94|0)[0-9]{9}$")
    registration_number: str | None = Field(None, min_length=2, max_length=50)
    latitude: float | None = Field(None, ge=5.0, le=10.0)
    longitude: float | None = Field(None, ge=79.0, le=82.0)


class ShopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    images: list[ShopImageSchema] = Field(default_factory=list)
    gigs: list[GigResponse] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
