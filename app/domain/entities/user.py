from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


@dataclass
class Client:
    """
    Firebase-backed client profile extension.
    The Firebase UID is the primary key — full user identity lives in Firebase Auth.
    """
    id: str  # Firebase Auth UID (PK — no FK to users table)
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class Seller:
    """
    Firebase-backed seller/tailor profile extension.
    The Firebase UID is the primary key — full user identity lives in Firebase Auth.
    NIC images are stored as cloud storage URLs.
    """
    id: str  # Firebase Auth UID (PK — no FK to users table)
    nic_front: str = None   # Cloud storage URL (Firebase Storage / Azure Blob)
    nic_rear: str = None    # Cloud storage URL
    is_verified: bool = False
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class MeasurementProfile:
    """
    Reusable standard body measurements saved for a client.
    References the client's Firebase UID directly.
    """
    client_id: str               # Firebase Auth UID referencing clients.id
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
    created_at: datetime = None
    updated_at: datetime = None
