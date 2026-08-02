from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.domain.entities.user import GenderEnum


class UserCreateRequest(BaseModel):
    id: str = Field(..., description="Firebase Auth UID", json_schema_extra={"example": "fb_uid_123456"})
    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "John Doe"})
    email: EmailStr = Field(..., json_schema_extra={"example": "user@example.com"})
    auth_provider: str = Field("email", json_schema_extra={"example": "google.com"})
    whatsapp_number: Optional[str] = Field(None, json_schema_extra={"example": "+94771234567"})
    address: Optional[str] = None
    city: Optional[str] = Field(None, json_schema_extra={"example": "Colombo"})
    postal_code: Optional[str] = None
    gender: Optional[GenderEnum] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    profile_image: Optional[str] = None
    role: str = Field("client", json_schema_extra={"example": "client"})


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    auth_provider: str
    whatsapp_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    gender: Optional[GenderEnum] = None
    age: Optional[int] = None
    profile_image: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MeasurementProfileRequest(BaseModel):
    chest: Optional[float] = None
    waist: Optional[float] = None
    shoulder: Optional[float] = None
    sleeve: Optional[float] = None
    neck: Optional[float] = None
    hip: Optional[float] = None
    inseam: Optional[float] = None
    length: Optional[float] = None
    notes: Optional[str] = None


class MeasurementProfileResponse(MeasurementProfileRequest):
    user_id: str
