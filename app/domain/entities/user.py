from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"


@dataclass
class Client:
    """
    Firebase-backed client profile extension.
    The Firebase UID is the primary key — full user identity lives in Firebase Auth.
    """
    id: str  # Firebase Auth UID (PK — no FK to users table)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Tailor:
    """
    Firebase-backed tailor profile extension.
    The Firebase UID is the primary key — full user identity lives in Firebase Auth.
    NIC images are stored as cloud storage URLs.
    Maps to the 'sellers' PostgreSQL table (table name unchanged for DB compatibility).
    """
    id: str  # Firebase Auth UID (PK — no FK to users table)
    nic_front: str | None = None   # Cloud storage URL (Firebase Storage / Azure Blob)
    nic_rear: str | None = None    # Cloud storage URL
    is_verified: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class MeasurementProfile:
    """
    Reusable standard body measurements saved for a client.
    References the client's Firebase UID directly.
    """
    client_id: str  # Firebase Auth UID referencing clients.id
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
