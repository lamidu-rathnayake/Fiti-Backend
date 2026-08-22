from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClientRegisterRequest(BaseModel):
    """
    Sent by the web frontend after Firebase Auth sign-up to register a client profile.
    The Firebase UID is NEVER sent in the body — it is always extracted from the Bearer Token.
    Contact details were previously stored in Firestore; they now live in PostgreSQL.
    """

    phone: str | None = Field(None, description="Contact phone number")
    city: str | None = Field(None, description="City")
    address: str | None = Field(None, description="Street address")
    latitude: float | None = Field(None, description="Latitude")
    longitude: float | None = Field(None, description="Longitude")


class ClientUpdateRequest(BaseModel):
    """Partial update for a client's contact profile. All fields optional."""

    display_name: str | None = Field(None, description="Display name")
    email: str | None = Field(None, description="Email address")
    photo_url: str | None = Field(None, description="Profile photo URL")
    phone: str | None = Field(None, description="Contact phone number")
    city: str | None = Field(None, description="City")
    address: str | None = Field(None, description="Street address")
    latitude: float | None = Field(None, description="Latitude")
    longitude: float | None = Field(None, description="Longitude")


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
        None, description="Cloud storage URL for NIC front photo"
    )
    nic_rear: str | None = Field(
        None, description="Cloud storage URL for NIC rear photo"
    )
    phone: str | None = Field(None, description="Contact phone number")
    city: str | None = Field(None, description="City")
    address: str | None = Field(None, description="Street address")
    latitude: float | None = Field(None, description="Latitude")
    longitude: float | None = Field(None, description="Longitude")


class TailorUpdateRequest(BaseModel):
    """Partial update for a tailor's contact profile and NIC images. All fields optional."""

    display_name: str | None = Field(None, description="Display name")
    email: str | None = Field(None, description="Email address")
    photo_url: str | None = Field(None, description="Profile photo URL")
    phone: str | None = Field(None, description="Contact phone number")
    city: str | None = Field(None, description="City")
    address: str | None = Field(None, description="Street address")
    latitude: float | None = Field(None, description="Latitude")
    longitude: float | None = Field(None, description="Longitude")
    nic_front: str | None = Field(
        None, description="Cloud storage URL for NIC front photo"
    )
    nic_rear: str | None = Field(
        None, description="Cloud storage URL for NIC rear photo"
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
    chest: float | None = None
    waist: float | None = None
    shoulder: float | None = None
    sleeve: float | None = None
    neck: float | None = None
    hip: float | None = None
    inseam: float | None = None
    length: float | None = None
    notes: str | None = None


class MeasurementProfileResponse(MeasurementProfileRequest):
    client_id: str
    measurement_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
