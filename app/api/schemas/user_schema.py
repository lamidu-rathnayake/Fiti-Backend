from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientRegisterRequest(BaseModel):
    """
    Sent by the web frontend after Firebase Auth sign-up to register a client profile.
    The Firebase UID is NEVER sent in the body — it is always extracted from the Bearer Token.
    Contact details were previously stored in Firestore; they now live in PostgreSQL.
    """

    phone: str | None = Field(None, pattern=r"^(?:\+94|0)[0-9]{9}$", description="Contact phone number (Sri Lankan format: +94xxxxxxxxx or 0xxxxxxxxx)")
    city: str | None = Field(None, min_length=2, max_length=100, description="City")
    address: str | None = Field(None, min_length=5, max_length=255, description="Street address")
    latitude: float | None = Field(None, ge=5.0, le=10.0, description="Latitude (Sri Lanka: ~5.0 to 10.0)")
    longitude: float | None = Field(None, ge=79.0, le=82.0, description="Longitude (Sri Lanka: ~79.0 to 82.0)")


class ClientUpdateRequest(BaseModel):
    """Partial update for a client's contact profile. All fields optional."""

    display_name: str | None = Field(None, min_length=2, max_length=150, description="Display name")
    email: EmailStr | None = Field(None, description="Email address")
    photo_url: str | None = Field(None, pattern=r"^https?://", max_length=2048, description="Profile photo URL")
    phone: str | None = Field(None, pattern=r"^(?:\+94|0)[0-9]{9}$", description="Contact phone number")
    city: str | None = Field(None, min_length=2, max_length=100, description="City")
    address: str | None = Field(None, min_length=5, max_length=255, description="Street address")
    latitude: float | None = Field(None, ge=5.0, le=10.0, description="Latitude")
    longitude: float | None = Field(None, ge=79.0, le=82.0, description="Longitude")


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    display_name: str | None = None
    email: str | None = None
    photo_url: str | None = None
    phone: str | None = None
    city: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TailorRegisterRequest(BaseModel):
    """
    Sent by the web frontend after Firebase Auth sign-up to register a tailor profile.
    The Firebase UID is NEVER sent in the body — it is always extracted from the Bearer Token.
    NIC image URLs should point to files already uploaded to cloud storage.
    Contact details were previously stored in Firestore; they now live in PostgreSQL.
    """

    nic_front: str | None = Field(
        None, pattern=r"^https?://", max_length=2048, description="Cloud storage URL for NIC front photo"
    )
    nic_rear: str | None = Field(
        None, pattern=r"^https?://", max_length=2048, description="Cloud storage URL for NIC rear photo"
    )
    phone: str | None = Field(None, pattern=r"^(?:\+94|0)[0-9]{9}$", description="Contact phone number")
    city: str | None = Field(None, min_length=2, max_length=100, description="City")
    address: str | None = Field(None, min_length=5, max_length=255, description="Street address")
    latitude: float | None = Field(None, ge=5.0, le=10.0, description="Latitude")
    longitude: float | None = Field(None, ge=79.0, le=82.0, description="Longitude")


class TailorUpdateRequest(BaseModel):
    """Partial update for a tailor's contact profile and NIC images. All fields optional."""

    display_name: str | None = Field(None, min_length=2, max_length=150, description="Display name")
    email: EmailStr | None = Field(None, description="Email address")
    photo_url: str | None = Field(None, pattern=r"^https?://", max_length=2048, description="Profile photo URL")
    phone: str | None = Field(None, pattern=r"^(?:\+94|0)[0-9]{9}$", description="Contact phone number")
    city: str | None = Field(None, min_length=2, max_length=100, description="City")
    address: str | None = Field(None, min_length=5, max_length=255, description="Street address")
    latitude: float | None = Field(None, ge=5.0, le=10.0, description="Latitude")
    longitude: float | None = Field(None, ge=79.0, le=82.0, description="Longitude")
    nic_front: str | None = Field(
        None, pattern=r"^https?://", max_length=2048, description="Cloud storage URL for NIC front photo"
    )
    nic_rear: str | None = Field(
        None, pattern=r"^https?://", max_length=2048, description="Cloud storage URL for NIC rear photo"
    )


class TailorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    display_name: str | None = None
    email: str | None = None
    photo_url: str | None = None
    nic_front: str | None = None
    nic_rear: str | None = None
    is_verified: bool = False
    phone: str | None = None
    city: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MeasurementProfileRequest(BaseModel):
    """Body measurements used in both profile storage and order clothing requests."""
    chest: float | None = Field(None, gt=0, description="Chest measurement")
    waist: float | None = Field(None, gt=0, description="Waist measurement")
    shoulder: float | None = Field(None, gt=0, description="Shoulder measurement")
    sleeve: float | None = Field(None, gt=0, description="Sleeve measurement")
    neck: float | None = Field(None, gt=0, description="Neck measurement")
    hip: float | None = Field(None, gt=0, description="Hip measurement")
    inseam: float | None = Field(None, gt=0, description="Inseam measurement")
    length: float | None = Field(None, gt=0, description="Length measurement")
    notes: str | None = Field(None, max_length=1000, description="Additional notes")


class MeasurementProfileResponse(MeasurementProfileRequest):
    client_id: str
    measurement_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
