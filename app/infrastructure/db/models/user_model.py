from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, Integer, Float, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.db.base import Base
from app.domain.entities.user import Client, Seller, MeasurementProfile, GenderEnum


class ClientModel(Base):
    """
    Stores Firebase-backed client profile data.
    The `id` column holds the Firebase Auth UID — there is no FK to a users table
    because user identity is fully managed by Firebase Auth.
    """
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_domain(self) -> Client:
        return Client(id=self.id, created_at=self.created_at, updated_at=self.updated_at)


class SellerModel(Base):
    """
    Stores Firebase-backed seller/tailor profile data.
    The `id` column holds the Firebase Auth UID — no FK to a users table.
    NIC image URLs point to cloud storage (Firebase Storage / Azure Blob).
    """
    __tablename__ = "sellers"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    nic_front: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    nic_rear: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_domain(self) -> Seller:
        return Seller(
            id=self.id,
            nic_front=self.nic_front,
            nic_rear=self.nic_rear,
            is_verified=self.is_verified,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class MeasurementProfileModel(Base):
    """
    Stores a client's reusable standard body measurements.
    References `clients.id` (Firebase UID) — no dependency on a users table.
    """
    __tablename__ = "measurement_profile"

    measurement_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    chest: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    waist: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    shoulder: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sleeve: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    neck: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hip: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    inseam: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    length: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_domain(self) -> MeasurementProfile:
        return MeasurementProfile(
            measurement_id=self.measurement_id,
            client_id=self.client_id,
            chest=self.chest,
            waist=self.waist,
            shoulder=self.shoulder,
            sleeve=self.sleeve,
            neck=self.neck,
            hip=self.hip,
            inseam=self.inseam,
            length=self.length,
            notes=self.notes,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
