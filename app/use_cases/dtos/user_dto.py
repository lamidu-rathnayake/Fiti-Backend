from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.domain.entities.user import GenderEnum


@dataclass
class ClientRegisterDTO:
    """Input DTO for registering a new client profile after Firebase Auth sign-up."""
    id: str   # Firebase Auth UID passed from the frontend after authentication


@dataclass
class ClientOutputDTO:
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SellerRegisterDTO:
    """Input DTO for registering a new seller profile after Firebase Auth sign-up."""
    id: str           # Firebase Auth UID
    nic_front: Optional[str] = None   # Cloud storage URL
    nic_rear: Optional[str] = None    # Cloud storage URL


@dataclass
class SellerOutputDTO:
    id: str
    nic_front: Optional[str] = None
    nic_rear: Optional[str] = None
    is_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class MeasurementProfileDTO:
    """Input DTO for saving or updating a client's body measurement profile."""
    client_id: str
    chest: Optional[float] = None
    waist: Optional[float] = None
    shoulder: Optional[float] = None
    sleeve: Optional[float] = None
    neck: Optional[float] = None
    hip: Optional[float] = None
    inseam: Optional[float] = None
    length: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class MeasurementProfileOutputDTO:
    client_id: str
    measurement_id: Optional[int] = None
    chest: Optional[float] = None
    waist: Optional[float] = None
    shoulder: Optional[float] = None
    sleeve: Optional[float] = None
    neck: Optional[float] = None
    hip: Optional[float] = None
    inseam: Optional[float] = None
    length: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
