from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


@dataclass
class User:
    """Pure Domain Entity representing a User mapped to Firebase Auth UID."""
    id: str  # Firebase Auth UID
    name: str
    email: str
    auth_provider: str  # e.g., 'google.com', 'password'
    whatsapp_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    gender: Optional[GenderEnum] = None
    age: Optional[int] = None
    profile_image: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def deactivate(self) -> None:
        self.is_active = False


@dataclass
class Client:
    """Pure Domain Entity representing a Client profile."""
    id: str  # Foreign Key -> User.id
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Seller:
    """Pure Domain Entity representing a Seller/Tailor business profile."""
    id: str  # Foreign Key -> User.id
    nic_front: Optional[str] = None
    nic_rear: Optional[str] = None
    is_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class MeasurementProfile:
    """Pure Domain Entity for client standard measurement profile."""
    measurement_id: Optional[int]
    user_id: str  # Foreign Key -> User.id
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
