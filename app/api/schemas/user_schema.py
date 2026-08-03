from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ClientRegisterRequest(BaseModel):
    """
    Sent by the web frontend after Firebase Auth sign-up to register a client profile.
    If 'id' is omitted, the backend will automatically extract the verified Firebase UID from the Bearer Token.
    """
    id: Optional[str] = Field(None, description="Firebase Auth UID (optional if Bearer Token is supplied)", json_schema_extra={"example": "firebase_uid_abc123"})


class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SellerRegisterRequest(BaseModel):
    """
    Sent by the web frontend after Firebase Auth sign-up to register a seller profile.
    If 'id' is omitted, the backend will automatically extract the verified Firebase UID from the Bearer Token.
    NIC image URLs should point to files already uploaded to cloud storage.
    """
    id: Optional[str] = Field(None, description="Firebase Auth UID (optional if Bearer Token is supplied)", json_schema_extra={"example": "firebase_uid_xyz789"})
    nic_front: Optional[str] = Field(None, description="Cloud storage URL for NIC front photo")
    nic_rear: Optional[str] = Field(None, description="Cloud storage URL for NIC rear photo")


class SellerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nic_front: Optional[str] = None
    nic_rear: Optional[str] = None
    is_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MeasurementProfileRequest(BaseModel):
    """Body measurements used in both profile storage and order clothing requests."""
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
    client_id: str
    measurement_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
