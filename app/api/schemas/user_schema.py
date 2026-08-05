from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ClientRegisterRequest(BaseModel):
    """
    Sent by the web frontend after Firebase Auth sign-up to register a client profile.
    If 'id' is omitted, the backend will automatically extract the verified Firebase UID from the Bearer Token.
    """
    id: str | None = Field(None, description="Firebase Auth UID (optional if Bearer Token is supplied)", json_schema_extra={"example": "firebase_uid_abc123"})


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SellerRegisterRequest(BaseModel):
    """
    Sent by the web frontend after Firebase Auth sign-up to register a seller profile.
    If 'id' is omitted, the backend will automatically extract the verified Firebase UID from the Bearer Token.
    NIC image URLs should point to files already uploaded to cloud storage.
    """
    id: str | None = Field(None, description="Firebase Auth UID (optional if Bearer Token is supplied)", json_schema_extra={"example": "firebase_uid_xyz789"})
    nic_front: str | None = Field(None, description="Cloud storage URL for NIC front photo")
    nic_rear: str | None = Field(None, description="Cloud storage URL for NIC rear photo")


class SellerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nic_front: str | None = None
    nic_rear: str | None = None
    is_verified: bool = False
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
