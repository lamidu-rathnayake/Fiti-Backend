from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.domain.entities.user import GenderEnum


@dataclass
class UserCreateInputDTO:
    id: str  # Firebase Auth UID
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
    role: str = "client"  # 'client' or 'seller'


@dataclass
class UserOutputDTO:
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
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SellerCreateInputDTO:
    seller_id: str
    nic_front: Optional[str] = None
    nic_rear: Optional[str] = None


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
    user_id: str
    chest: Optional[float] = None
    waist: Optional[float] = None
    shoulder: Optional[float] = None
    sleeve: Optional[float] = None
    neck: Optional[float] = None
    hip: Optional[float] = None
    inseam: Optional[float] = None
    length: Optional[float] = None
    notes: Optional[str] = None
