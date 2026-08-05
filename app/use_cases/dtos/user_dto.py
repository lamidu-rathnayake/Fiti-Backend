from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClientRegisterDTO:
    """Input DTO for registering a new client profile after Firebase Auth sign-up."""
    id: str   # Firebase Auth UID passed from the frontend after authentication


@dataclass
class ClientOutputDTO:
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class SellerRegisterDTO:
    """Input DTO for registering a new seller profile after Firebase Auth sign-up."""
    id: str           # Firebase Auth UID
    nic_front: str | None = None   # Cloud storage URL
    nic_rear: str | None = None    # Cloud storage URL


@dataclass
class SellerOutputDTO:
    id: str
    nic_front: str | None = None
    nic_rear: str | None = None
    is_verified: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class MeasurementProfileDTO:
    """Input DTO for saving or updating a client's body measurement profile."""
    client_id: str
    chest: float | None = None
    waist: float | None = None
    shoulder: float | None = None
    sleeve: float | None = None
    neck: float | None = None
    hip: float | None = None
    inseam: float | None = None
    length: float | None = None
    notes: str | None = None


@dataclass
class MeasurementProfileOutputDTO:
    client_id: str
    measurement_id: int | None = None
    chest: float | None = None
    waist: float | None = None
    shoulder: float | None = None
    sleeve: float | None = None
    neck: float | None = None
    hip: float | None = None
    inseam: float | None = None
    length: float | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
