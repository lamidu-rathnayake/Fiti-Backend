from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClientRegisterDTO:
    """Input DTO for registering a new client profile after Firebase Auth sign-up.
    UID is always extracted from the Bearer token by the endpoint — never from the request body.
    """

    id: str  # Firebase Auth UID decoded from Bearer token
    display_name: str | None = None
    email: str | None = None
    photo_url: str | None = None
    phone: str | None = None
    city: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass
class ClientUpdateDTO:
    """Input DTO for partially updating a client's contact profile."""

    id: str  # Firebase Auth UID (identifies which record to update)
    display_name: str | None = None
    email: str | None = None
    photo_url: str | None = None
    phone: str | None = None
    city: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass
class ClientOutputDTO:
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


@dataclass
class TailorRegisterDTO:
    """Input DTO for registering a new tailor profile after Firebase Auth sign-up.
    UID is always extracted from the Bearer token by the endpoint — never from the request body.
    """

    id: str  # Firebase Auth UID
    display_name: str | None = None
    email: str | None = None
    photo_url: str | None = None
    nic_front: str | None = None  # Cloud storage URL
    nic_rear: str | None = None  # Cloud storage URL
    phone: str | None = None
    city: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


@dataclass
class TailorUpdateDTO:
    """Input DTO for partially updating a tailor's contact profile."""

    id: str  # Firebase Auth UID (identifies which record to update)
    display_name: str | None = None
    email: str | None = None
    photo_url: str | None = None
    phone: str | None = None
    city: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    nic_front: str | None = None
    nic_rear: str | None = None


@dataclass
class TailorOutputDTO:
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
